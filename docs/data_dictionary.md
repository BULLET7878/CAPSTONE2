# Data Dictionary — Job Market Analytics Dataset

**Dataset:** `resume_job_matching_dataset_10000_v2.csv`  
**Location:** `data/raw/`  
**Rows:** 10,000 | **Columns:** 12  
**Last Updated:** April 28, 2026

## Column Definitions

| # | Column Name | Data Type | Description |
|---|-------------|-----------|-------------|
| 1 | `User_ID` | String | Unique identifier for each candidate profile |
| 2 | `Job_ID` | String | Unique identifier for each job posting |
| 3 | `User_Skills` | String | Comma-separated list of candidate skills |
| 4 | `Job_Requirements` | String | Comma-separated list of required job skills |
| 5 | `User_Skill_Count` | Integer | Number of skills listed for the candidate |
| 6 | `Job_Req_Count` | Integer | Number of skills required by the job |
| 7 | `Skill_Overlap_Count` | Integer | Exact count of matched skills between candidate and job |
| 8 | `Match_Score_Band` | Categorical | Match-quality band: `Low`, `Medium`, or `High` |
| 9 | `Education_Level` | Categorical | Highest education level of the candidate |
| 10 | `Experience_Years` | Integer | Candidate experience in years |
| 11 | `Location` | Categorical | Candidate or market location |
| 12 | `Job_Role` | Categorical | Role family associated with the job posting |

## ETL-Derived Fields

| Column Name | Source | Description |
|-------------|--------|-------------|
| `skill_gap` | `Job_Req_Count - Skill_Overlap_Count` | Number of required skills still missing |
| `overlap_ratio` | `Skill_Overlap_Count / Job_Req_Count` | Share of job requirements already covered |
| `candidate_readiness` | `overlap_ratio` | Rule-based tier: `Low`, `Medium`, `High` |

## Known Limitations

| Issue | Impact |
|-------|--------|
| No timestamp or application date | Trend analysis and forecasting are not supported |
| No raw numeric `Match_Score` | Band-level analysis is possible, but fine-grained scoring is not |
| No recommendation / hiring outcome label | Predictive recommendation modelling cannot be validated on this dataset |
| Synthetic or simulated structure is likely | Findings are directionally useful, but should be validated on live hiring data |
