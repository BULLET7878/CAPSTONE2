"""
etl_pipeline.py
===============
Capstone 2 — Job Market Analytics
HR Tech / Labour Market Analytics

End-to-end ETL pipeline:
  1. EXTRACT  — Load raw Excel dataset
  2. TRANSFORM — Clean, standardize, engineer features
  3. LOAD      — Export processed CSVs for analysis & Tableau

Usage:
    python scripts/etl_pipeline.py

Output:
    data/processed/jobs_cleaned.csv       — Full cleaned dataset
    data/processed/jobs_tableau_ready.csv — Aggregated Tableau-ready export
    data/processed/skill_frequency.csv    — Skill frequency table
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
RAW_FILE = RAW_DIR / "Job Datsset.xlsx"
SKILL_SEP = ","  # delimiter used in User_Skills and Job_Requirements columns

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1: EXTRACT
# ══════════════════════════════════════════════════════════════════════════════
def extract(filepath: Path) -> pd.DataFrame:
    """Load raw Excel file into a DataFrame."""
    log.info(f"[EXTRACT] Loading: {filepath}")
    if not filepath.exists():
        log.error(f"File not found: {filepath}")
        sys.exit(1)

    df = pd.read_excel(filepath, engine="openpyxl")
    log.info(f"[EXTRACT] Loaded {len(df):,} rows × {df.shape[1]} columns")
    log.info(f"[EXTRACT] Columns: {list(df.columns)}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2: TRANSFORM
# ══════════════════════════════════════════════════════════════════════════════
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and engineer features from raw job data."""
    log.info("[TRANSFORM] Starting transformation...")

    original_len = len(df)

    # ── 2.1 Standardise column names ──────────────────────────────────────────
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    log.info(f"[TRANSFORM] Normalised columns: {list(df.columns)}")

    # ── 2.2 Drop exact duplicates ─────────────────────────────────────────────
    df = df.drop_duplicates()
    log.info(f"[TRANSFORM] After dedup: {len(df):,} rows (removed {original_len - len(df):,})")

    # ── 2.3 Drop rows where critical columns are null ─────────────────────────
    critical = ["user_skills", "job_requirements", "match_score", "recommended"]
    # Handle column name variations
    col_map = {}
    for col in df.columns:
        if "skill" in col and "user" in col:
            col_map[col] = "user_skills"
        elif "requirement" in col or ("skill" in col and "job" in col):
            col_map[col] = "job_requirements"
        elif "match" in col and "score" in col:
            col_map[col] = "match_score"
        elif "recommend" in col:
            col_map[col] = "recommended"
        elif "user" in col and "id" in col:
            col_map[col] = "user_id"
        elif "job" in col and "id" in col:
            col_map[col] = "job_id"
    df = df.rename(columns=col_map)
    log.info(f"[TRANSFORM] Final columns after rename: {list(df.columns)}")

    before_null_drop = len(df)
    df = df.dropna(subset=["match_score", "recommended"])
    log.info(f"[TRANSFORM] After null drop: {len(df):,} rows (removed {before_null_drop - len(df):,})")

    # ── 2.4 Clean skill strings ────────────────────────────────────────────────
    def clean_skill_string(s):
        if pd.isna(s):
            return ""
        return ",".join(
            skill.strip().lower()
            for skill in str(s).split(",")
            if skill.strip()
        )

    df["user_skills"] = df["user_skills"].apply(clean_skill_string)
    df["job_requirements"] = df["job_requirements"].apply(clean_skill_string)

    # ── 2.5 Ensure numeric types ──────────────────────────────────────────────
    df["match_score"] = pd.to_numeric(df["match_score"], errors="coerce")
    df["recommended"] = pd.to_numeric(df["recommended"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["match_score", "recommended"])

    # ── 2.6 Feature Engineering ───────────────────────────────────────────────
    df["user_skill_count"] = df["user_skills"].apply(
        lambda x: len(x.split(",")) if x else 0
    )
    df["job_req_count"] = df["job_requirements"].apply(
        lambda x: len(x.split(",")) if x else 0
    )
    df["skill_overlap_count"] = df.apply(
        lambda row: len(
            set(row["user_skills"].split(",")) & set(row["job_requirements"].split(","))
        ) if row["user_skills"] and row["job_requirements"] else 0,
        axis=1,
    )

    # Match score banding
    df["match_score_band"] = pd.cut(
        df["match_score"],
        bins=[0, 33, 66, 100],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    )

    log.info("[TRANSFORM] Feature engineering complete")
    log.info(f"[TRANSFORM] Final shape: {df.shape}")
    log.info(f"[TRANSFORM] Recommendation rate: {df['recommended'].mean():.2%}")

    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3: LOAD
# ══════════════════════════════════════════════════════════════════════════════
def load(df: pd.DataFrame) -> None:
    """Export cleaned data and aggregations to CSV."""

    # ── 3.1 Full cleaned dataset ──────────────────────────────────────────────
    out_main = PROCESSED_DIR / "jobs_cleaned.csv"
    df.to_csv(out_main, index=False)
    log.info(f"[LOAD] Saved: {out_main} ({len(df):,} rows)")

    # ── 3.2 Tableau-ready (no list columns — exploded for Tableau) ────────────
    tableau_cols = [
        "user_id", "job_id", "match_score", "recommended",
        "user_skill_count", "job_req_count", "skill_overlap_count", "match_score_band"
    ]
    tableau_cols = [c for c in tableau_cols if c in df.columns]
    df[tableau_cols].to_csv(PROCESSED_DIR / "jobs_tableau_ready.csv", index=False)
    log.info(f"[LOAD] Saved: jobs_tableau_ready.csv")

    # ── 3.3 Skill frequency table ─────────────────────────────────────────────
    all_user_skills = (
        df["user_skills"]
        .str.split(",")
        .explode()
        .str.strip()
        .dropna()
        .loc[lambda s: s != ""]
    )
    all_job_reqs = (
        df["job_requirements"]
        .str.split(",")
        .explode()
        .str.strip()
        .dropna()
        .loc[lambda s: s != ""]
    )

    user_freq = all_user_skills.value_counts().rename("user_skill_freq")
    job_freq = all_job_reqs.value_counts().rename("job_req_freq")

    skill_freq = pd.concat([user_freq, job_freq], axis=1).fillna(0).astype(int)
    skill_freq.index.name = "skill"
    skill_freq = skill_freq.sort_values("job_req_freq", ascending=False)
    skill_freq.to_csv(PROCESSED_DIR / "skill_frequency.csv")
    log.info(f"[LOAD] Saved: skill_frequency.csv ({len(skill_freq):,} unique skills)")

    # ── 3.4 Summary stats ─────────────────────────────────────────────────────
    log.info("\n" + "=" * 60)
    log.info("PIPELINE SUMMARY")
    log.info("=" * 60)
    log.info(f"Total records processed : {len(df):,}")
    log.info(f"Recommendation rate     : {df['recommended'].mean():.2%}")
    log.info(f"Avg match score         : {df['match_score'].mean():.2f}")
    log.info(f"Unique skills (users)   : {all_user_skills.nunique():,}")
    log.info(f"Unique skills (jobs)    : {all_job_reqs.nunique():,}")
    log.info("=" * 60)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    log.info("=" * 60)
    log.info("Capstone 2 — Job Market Analytics ETL Pipeline")
    log.info("=" * 60)

    df_raw = extract(RAW_FILE)
    df_clean = transform(df_raw)
    load(df_clean)

    log.info("[DONE] ETL pipeline completed successfully.")


if __name__ == "__main__":
    main()
