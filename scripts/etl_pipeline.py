"""
etl_pipeline.py
────────────────────────────────────────────────────────────────────
Capstone 2 | Data Visualization & Analytics
Newton School of Technology
Dataset : data/raw/resume_job_matching_dataset_10000_v2.csv
Outputs : data/processed/jobs_cleaned.csv
          data/processed/jobs_tableau_ready.csv
          data/processed/skill_frequency.csv
          data/processed/band_aggregation.csv
          data/processed/role_location_agg.csv
          data/processed/kpis.csv
────────────────────────────────────────────────────────────────────
"""

import os
import logging
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ETL")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE  = os.path.join(BASE_DIR, "data", "raw", "resume_job_matching_dataset_10000_v2.csv")
PROC_DIR  = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — LOAD
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 1 | Loading raw data …")
df = pd.read_csv(RAW_FILE)
log.info(f"  Loaded {df.shape[0]:,} rows × {df.shape[1]} columns")
log.info(f"  Columns: {list(df.columns)}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — STANDARDISE COLUMN NAMES
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 2 | Standardising column names …")
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
    .str.replace(r"[^a-z0-9_]", "", regex=True)
)
log.info(f"  Renamed → {list(df.columns)}")

# Canonical column map (handles any minor naming variation)
COL_MAP = {
    c: c for c in df.columns  # identity — columns already snake_case
}
# Expected canonical names after rename:
# user_id, job_id, user_skills, job_requirements,
# user_skill_count, job_req_count, skill_overlap_count,
# match_score_band, education_level, experience_years, location, job_role


# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — DUPLICATES
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 3 | Removing duplicates …")
before = len(df)
df = df.drop_duplicates(subset=["user_id", "job_id"])
log.info(f"  Removed {before - len(df):,} duplicates. Remaining: {len(df):,}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — NULL AUDIT & HANDLING
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 4 | Null value audit …")
null_report = df.isnull().sum()
log.info(f"\n{null_report}")

# Drop rows only where core identity/match columns are null
CORE_COLS = ["user_id", "job_id", "match_score_band"]
before = len(df)
df = df.dropna(subset=CORE_COLS)
log.info(f"  Dropped {before - len(df):,} rows with null core fields.")

# Fill remaining nulls gracefully
df["user_skills"]      = df["user_skills"].fillna("")
df["job_requirements"] = df["job_requirements"].fillna("")
df["education_level"]  = df["education_level"].fillna("Unknown")
df["location"]         = df["location"].fillna("Unknown")
df["job_role"]         = df["job_role"].fillna("Unknown")
df["experience_years"] = pd.to_numeric(df["experience_years"], errors="coerce").fillna(df["experience_years"].median())
log.info("  Nulls filled for non-core columns.")


# ════════════════════════════════════════════════════════════════════════════
# STEP 5 — DATA TYPE ENFORCEMENT
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 5 | Enforcing data types …")
df["user_skill_count"]    = pd.to_numeric(df["user_skill_count"],    errors="coerce").fillna(0).astype(int)
df["job_req_count"]       = pd.to_numeric(df["job_req_count"],       errors="coerce").fillna(0).astype(int)
df["skill_overlap_count"] = pd.to_numeric(df["skill_overlap_count"], errors="coerce").fillna(0).astype(int)
df["experience_years"]    = pd.to_numeric(df["experience_years"],    errors="coerce").fillna(0).astype(int)

# Standardise categorical columns
df["match_score_band"] = df["match_score_band"].str.strip().str.title()
df["education_level"]  = df["education_level"].str.strip().str.title()
df["location"]         = df["location"].str.strip().str.title()
df["job_role"]         = df["job_role"].str.strip().str.title()

# Ordered categorical for band
BAND_ORDER = pd.CategoricalDtype(categories=["Low", "Medium", "High"], ordered=True)
df["match_score_band"] = df["match_score_band"].astype(BAND_ORDER)
log.info("  Data types enforced.")


# ════════════════════════════════════════════════════════════════════════════
# STEP 6 — OUTLIER DETECTION
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 6 | Outlier detection (IQR) on numeric columns …")
for col in ["user_skill_count", "job_req_count", "skill_overlap_count", "experience_years"]:
    Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    IQR = Q3 - Q1
    lo, hi = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    flagged = ((df[col] < lo) | (df[col] > hi)).sum()
    log.info(f"  {col}: {flagged:,} outliers flagged (kept — clipping not appropriate here)")


# ════════════════════════════════════════════════════════════════════════════
# STEP 7 — CLEAN SKILL STRINGS
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 7 | Cleaning skill strings …")

def clean_skills(s):
    """Strip whitespace, lowercase, de-duplicate, rejoin with pipe separator."""
    if not s or pd.isna(s):
        return ""
    skills = [sk.strip().lower() for sk in str(s).split(",") if sk.strip()]
    return "|".join(dict.fromkeys(skills))  # preserve order, deduplicate

df["user_skills"]      = df["user_skills"].apply(clean_skills)
df["job_requirements"] = df["job_requirements"].apply(clean_skills)
log.info("  Skill strings cleaned: stripped, lowercased, deduplicated, pipe-joined.")


# ════════════════════════════════════════════════════════════════════════════
# STEP 8 — FEATURE ENGINEERING
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 8 | Feature engineering …")

# Recalculate skill counts from cleaned strings (source of truth)
df["user_skill_count"]    = df["user_skills"].apply(lambda x: len(x.split("|")) if x else 0)
df["job_req_count"]       = df["job_requirements"].apply(lambda x: len(x.split("|")) if x else 0)

# Skill overlap recalculated from cleaned sets
df["skill_overlap_count"] = df.apply(
    lambda r: len(
        set(r["user_skills"].split("|")) & set(r["job_requirements"].split("|"))
    ) if r["user_skills"] and r["job_requirements"] else 0,
    axis=1,
)

# Derived metrics
df["skill_gap"]     = (df["job_req_count"] - df["skill_overlap_count"]).clip(lower=0)
df["overlap_ratio"] = (
    df["skill_overlap_count"] / df["job_req_count"].replace(0, 1)
).round(4)

# Experience tier
def exp_tier(yrs):
    if yrs <= 2:  return "Junior (0–2 yrs)"
    elif yrs <= 5: return "Mid (3–5 yrs)"
    elif yrs <= 8: return "Senior (6–8 yrs)"
    else:          return "Expert (9+ yrs)"

df["experience_tier"] = df["experience_years"].apply(exp_tier)

# Education rank (for ordering)
EDU_RANK = {"High School": 1, "Bachelor": 2, "Master": 3, "Phd": 4, "Unknown": 0}
df["education_rank"] = df["education_level"].map(EDU_RANK).fillna(0).astype(int)

# Band numeric proxy for correlation / ordering
BAND_NUM = {"Low": 1, "Medium": 2, "High": 3}
df["band_numeric"] = df["match_score_band"].map(BAND_NUM)

log.info(f"  Feature engineering complete. Final shape: {df.shape}")
log.info(f"  New columns: skill_gap, overlap_ratio, experience_tier, education_rank, band_numeric")


# ════════════════════════════════════════════════════════════════════════════
# STEP 9 — EXPORT: MAIN CLEANED FILE
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 9 | Exporting cleaned data …")
out_main = os.path.join(PROC_DIR, "jobs_cleaned.csv")
df.to_csv(out_main, index=False)
log.info(f"  ✅ jobs_cleaned.csv — {len(df):,} rows × {df.shape[1]} columns")


# ════════════════════════════════════════════════════════════════════════════
# STEP 10 — EXPORT: TABLEAU-READY FILE
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 10 | Creating Tableau-ready export …")
TABLEAU_COLS = [
    "user_id", "job_id",
    "match_score_band", "band_numeric",
    "user_skill_count", "job_req_count", "skill_overlap_count",
    "skill_gap", "overlap_ratio",
    "education_level", "education_rank",
    "experience_years", "experience_tier",
    "location", "job_role",
]
TABLEAU_COLS = [c for c in TABLEAU_COLS if c in df.columns]
df[TABLEAU_COLS].to_csv(os.path.join(PROC_DIR, "jobs_tableau_ready.csv"), index=False)
log.info(f"  ✅ jobs_tableau_ready.csv — {len(TABLEAU_COLS)} columns")


# ════════════════════════════════════════════════════════════════════════════
# STEP 11 — EXPORT: SKILL FREQUENCY
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 11 | Computing skill frequency …")
user_skills_series = df["user_skills"].str.split("|").explode().str.strip().loc[lambda s: s != ""]
job_skills_series  = df["job_requirements"].str.split("|").explode().str.strip().loc[lambda s: s != ""]

sf = pd.concat([
    user_skills_series.value_counts().rename("user_freq"),
    job_skills_series.value_counts().rename("job_freq"),
], axis=1).fillna(0).astype(int)
sf.index.name = "skill"
sf["demand_gap"]    = sf["job_freq"] - sf["user_freq"]
sf["supply_surplus"]= sf["user_freq"] - sf["job_freq"]
sf = sf.sort_values("job_freq", ascending=False).head(30)
sf.to_csv(os.path.join(PROC_DIR, "skill_frequency.csv"))
log.info(f"  ✅ skill_frequency.csv — top {len(sf)} skills")


# ════════════════════════════════════════════════════════════════════════════
# STEP 12 — EXPORT: BAND AGGREGATION
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 12 | Band-level aggregation …")
band_agg = df.groupby("match_score_band", observed=True).agg(
    count            = ("user_id", "count"),
    avg_overlap      = ("skill_overlap_count", "mean"),
    avg_skill_gap    = ("skill_gap", "mean"),
    avg_overlap_ratio= ("overlap_ratio", "mean"),
    avg_exp_years    = ("experience_years", "mean"),
    avg_user_skills  = ("user_skill_count", "mean"),
).reset_index().round(4)
band_agg.to_csv(os.path.join(PROC_DIR, "band_aggregation.csv"), index=False)
log.info(f"  ✅ band_aggregation.csv — {len(band_agg)} bands")


# ════════════════════════════════════════════════════════════════════════════
# STEP 13 — EXPORT: ROLE × LOCATION AGGREGATION
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 13 | Role × Location aggregation …")
role_loc = df.groupby(["job_role", "location"], observed=True).agg(
    count           = ("user_id", "count"),
    avg_overlap     = ("skill_overlap_count", "mean"),
    avg_skill_gap   = ("skill_gap", "mean"),
    avg_exp_years   = ("experience_years", "mean"),
    high_band_count = ("band_numeric", lambda x: (x == 3).sum()),
).reset_index().round(3)
role_loc.to_csv(os.path.join(PROC_DIR, "role_location_agg.csv"), index=False)
log.info(f"  ✅ role_location_agg.csv — {len(role_loc)} role×location pairs")


# ════════════════════════════════════════════════════════════════════════════
# STEP 14 — EXPORT: KPIs
# ════════════════════════════════════════════════════════════════════════════
log.info("STEP 14 | Computing KPIs …")
total = len(df)
kpis = {
    "Total Records"              : total,
    "High Match Rate (%)"        : f"{(df['match_score_band']=='High').mean()*100:.1f}%",
    "Medium Match Rate (%)"      : f"{(df['match_score_band']=='Medium').mean()*100:.1f}%",
    "Low Match Rate (%)"         : f"{(df['match_score_band']=='Low').mean()*100:.1f}%",
    "Avg Skill Overlap"          : f"{df['skill_overlap_count'].mean():.2f}",
    "Avg Skill Gap"              : f"{df['skill_gap'].mean():.2f}",
    "Avg Overlap Ratio"          : f"{df['overlap_ratio'].mean():.3f}",
    "Avg Experience (years)"     : f"{df['experience_years'].mean():.1f}",
    "High Band Avg Overlap"      : f"{df[df['match_score_band']=='High']['skill_overlap_count'].mean():.2f}",
    "Low Band Avg Overlap"       : f"{df[df['match_score_band']=='Low']['skill_overlap_count'].mean():.2f}",
    "High Band Avg Skill Gap"    : f"{df[df['match_score_band']=='High']['skill_gap'].mean():.2f}",
    "Most Common Job Role"       : df["job_role"].mode()[0],
    "Most Common Location"       : df["location"].mode()[0],
    "Most Common Education"      : df["education_level"].mode()[0],
    "Unique Skills (Candidates)" : user_skills_series.nunique(),
    "Unique Skills (Jobs)"       : job_skills_series.nunique(),
}
kpi_df = pd.DataFrame(list(kpis.items()), columns=["KPI", "Value"])
kpi_df.to_csv(os.path.join(PROC_DIR, "kpis.csv"), index=False)
log.info(f"  ✅ kpis.csv — {len(kpi_df)} KPIs")


# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════
log.info("")
log.info("═" * 60)
log.info("ETL PIPELINE COMPLETE")
log.info("═" * 60)
for fname in sorted(os.listdir(PROC_DIR)):
    if fname.endswith(".csv"):
        size_kb = os.path.getsize(os.path.join(PROC_DIR, fname)) / 1024
        log.info(f"  {fname:<40} {size_kb:>8.1f} KB")
log.info("═" * 60)
