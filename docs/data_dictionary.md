# 📖 Data Dictionary — Job Market Analytics Dataset

**Dataset:** `Job Datsset.xlsx`  
**Location:** `data/raw/`  
**Rows:** 100,000 | **Columns:** 6  
**Last Updated:** April 2026

---

## Column Definitions

| # | Column Name | Data Type | Range / Format | Description | Notes |
|---|-------------|-----------|----------------|-------------|-------|
| 1 | `User_ID` | Integer | 1 – 100,000 | Unique identifier for each job candidate | Primary key; no nulls expected |
| 2 | `Job_ID` | Integer | 1 – N | Unique identifier for each job posting | Multiple users may apply to the same job |
| 3 | `User_Skills` | String | Pipe-delimited (`\|`) | Skills possessed by the candidate | e.g. `Python\|SQL\|Excel` |
| 4 | `Job_Requirements` | String | Pipe-delimited (`\|`) | Skills required by the job posting | e.g. `Python\|Machine Learning\|Communication` |
| 5 | `Match_Score` | Float | 0.0 – 100.0 | Algorithmic skill-overlap match score | Higher = better match |
| 6 | `Recommended` | Integer (Binary) | 0 or 1 | Whether the candidate was recommended for the job | 1 = Recommended, 0 = Not Recommended |

---

## Derived / Engineered Columns (added in cleaning/EDA)

| Column Name | Source | Description |
|-------------|--------|-------------|
| `user_skill_count` | `User_Skills` | Number of skills the candidate has |
| `job_req_count` | `Job_Requirements` | Number of skills the job requires |
| `skill_overlap_count` | Both | Count of exact skill matches |
| `match_score_band` | `Match_Score` | Binned category: Low / Medium / High |

---

## Score Banding

| Band | Match Score Range | Interpretation |
|------|------------------|----------------|
| Low | 0 – 33 | Poor fit — unlikely to be recommended |
| Medium | 34 – 66 | Moderate fit — borderline recommendation |
| High | 67 – 100 | Strong fit — likely to be recommended |

---

## Known Quality Issues

| Issue | Column | Resolution |
|-------|--------|------------|
| Possible leading/trailing whitespace in skills | `User_Skills`, `Job_Requirements` | Strip whitespace during cleaning |
| Duplicate rows possible | All | Drop exact duplicates in notebook 02 |
| Inconsistent skill casing | `User_Skills`, `Job_Requirements` | Lowercase all skills |

---

*Data Dictionary v1.0 — Capstone 2 Team*
