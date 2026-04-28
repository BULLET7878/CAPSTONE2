# Data Visualization & Analytics Final Project Report

## 1. Cover Page

**Project Title:** Job Market Analytics: Resume-Job Fit, Skill Gaps, and Hiring Readiness  
**Sector:** HR Tech / Talent Intelligence / Workforce Analytics  
**Institute:** Newton School of Technology  
**GitHub Repository URL:** [https://github.com/BULLET7878/CAPSTONE2](https://github.com/BULLET7878/CAPSTONE2)  
**Tableau Public Dashboard URL:** To be inserted after publishing  
**Submission Date:** April 28, 2026  

**Team Members and Roles**

| Team Member | Role |
|-------------|------|
| Rahul Dhakar | Data Engineer, ETL Pipeline, Repository Management |
| Harsh Raj | EDA, Statistical Analysis, Storytelling |
| Suraj Kumar Rai | Tableau Dashboard Development |
| Harshil Singh | Report Writing, Documentation, and Presentation |
me
> Replace placeholder names and the Tableau URL before submission.

## 2. Executive Summary

Hiring teams often struggle to decide whether available candidate supply is actually aligned with current job demand. This project addresses that challenge using a structured resume-job matching dataset and converts raw skill lists into business-ready indicators of candidate readiness, skill gaps, and role-level hiring pressure.

The team built a Python-led ETL and analytics workflow around the uploaded dataset `data/raw/resume_job_matching_dataset_10000_v2.csv`. The pipeline standardised the schema, validated row integrity, cleaned skill strings, recomputed overlap-based features, and exported processed files for analysis and Tableau consumption. The analytical focus shifted from binary recommendation prediction to market-fit diagnostics because the uploaded dataset contains match bands but not the original continuous score or hiring outcome label.

Four findings stand out. First, overall fit is weak: average skill overlap is only `1.27` skills against `5.02` average job requirements, leaving a mean skill gap of `3.75`. Second, the market is highly concentrated in low-fit profiles: `61.6%` of records fall in the `Low` match band, while only `1.6%` reach `High`. Third, skill alignment is driven far more by actual skill inventory than by experience; experience has near-zero correlation with overlap (`-0.014`), while user skill count is positively related to overlap (`0.361`). Fourth, role segments differ: `Business Analyst` and `Software Engineer` roles show the strongest mean overlap, while `ML Engineer` has the weakest average fit, indicating a tighter talent bottleneck.

The highest-impact recommendations are straightforward. Talent teams should prioritize skill-gap reduction programs around the most demanded skills such as `Python`, `AWS`, `SQL`, `Communication`, and `Data Analysis`. Recruiters should segment requisitions by readiness tier so low-fit roles are not treated the same as medium-fit pipelines. Finally, HR leadership should operationalize a readiness dashboard to monitor role-wise gaps and redirect sourcing budgets toward hard-to-fill roles before hiring delays escalate.

## 3. Sector & Business Context

The project sits in the HR Tech and workforce analytics sector, where companies increasingly depend on digital screening systems to handle rising applicant volumes and specialised skill requirements. Modern hiring challenges include talent shortages in technical roles, poor match quality between resumes and job descriptions, inflated time-to-hire, and inefficient sourcing spend.

The primary decision-maker for this analysis is an HR leader, talent acquisition head, or workforce planning manager. This stakeholder needs an evidence-based view of where candidate supply aligns with demand and where hiring friction is most severe.

This problem was chosen because matching inefficiency is one of the most expensive hidden costs in recruitment. When job requirements outpace candidate readiness, organisations spend more on sourcing, lose time in screening, and experience vacancy delays. Solving this problem creates value by improving shortlist quality, reducing recruiter effort, and making skill-development investments more targeted.

## 4. Problem Statement & Objectives

### Formal Problem Definition

The project evaluates how well candidate skill inventories align with job requirements across roles, education levels, and locations, and identifies where the largest skill gaps exist in the hiring funnel.

### Scope

**In scope**

- Candidate-job fit analysis using skill overlap fields
- Role, education, and location segmentation
- ETL standardisation in Python
- Tableau-ready output generation
- Actionable recommendations for talent strategy

**Out of scope**

- Predicting actual hiring or recommendation outcomes
- Time-series trend analysis or forecasting
- Causal hiring-performance attribution
- Resume text parsing beyond the supplied structured fields

### Success Criteria

The project succeeds if it:

- Produces a clean and reproducible dataset for analysis
- Quantifies fit using business-friendly KPIs
- Identifies the highest-gap roles, skills, and segments
- Supports an executive dashboard and decision-ready recommendations

## 5. Data Description

### Dataset Source and Access

The analysis uses the uploaded project dataset: `data/raw/resume_job_matching_dataset_10000_v2.csv`.  
Direct repository path: `data/raw/resume_job_matching_dataset_10000_v2.csv`

This appears to be a structured synthetic or simulated resume-job matching dataset prepared for academic analytics use. No external public citation was provided with the upload, so the repository file itself is treated as the authoritative source.

### Data Structure

- Rows: `10,000`
- Columns: `12`
- Time period: Not available in the dataset
- Grain: One candidate-job match record per row

### Key Fields

| Field | Meaning |
|-------|---------|
| `User_ID` | Candidate identifier |
| `Job_ID` | Job posting identifier |
| `User_Skills` | Candidate skill inventory |
| `Job_Requirements` | Skill requirements for the role |
| `User_Skill_Count` | Number of listed candidate skills |
| `Job_Req_Count` | Number of required job skills |
| `Skill_Overlap_Count` | Exact matched skills between candidate and job |
| `Match_Score_Band` | Fit band: `Low`, `Medium`, `High` |
| `Education_Level` | Candidate education segment |
| `Experience_Years` | Years of experience |
| `Location` | Geography segment |
| `Job_Role` | Target job family |

### Data Limitations and Known Biases

- No timestamp is available, so trend analysis and seasonality cannot be studied.
- No numeric match score is included, only score bands.
- No final recommendation or hiring outcome label is present.
- The data is likely synthetic, which limits external validity.
- Skills are simplified into exact string matches, which may understate semantic similarity.

## 6. Data Cleaning & ETL Pipeline

All primary cleaning and transformation steps were executed in Python through [`scripts/etl_pipeline.py`](/Users/rahuldhakar/Desktop/DATA/CAPSTONE/scripts/etl_pipeline.py).

### Cleaning and Transformation Steps

1. Loaded the uploaded CSV from `data/raw/`.
2. Standardised all column names to lowercase snake_case.
3. Validated required columns against the new schema.
4. Removed exact duplicates.
5. Trimmed and lowercased skill strings for both candidate and job skill fields.
6. Recomputed `user_skill_count`, `job_req_count`, and `skill_overlap_count` from the cleaned skill strings.
7. Converted numeric fields such as experience and skill counts to strict numeric types.
8. Engineered `skill_gap`, `overlap_ratio`, and `candidate_readiness`.
9. Exported cleaned data and Tableau-ready files to `data/processed/`.

### Missing Values

No missing values were found in the uploaded CSV.

| Column Group | Missing Values | Handling |
|--------------|----------------|----------|
| All 12 source columns | `0` | No imputation required |

### Duplicate Handling

- Exact duplicate rows detected: `0`
- Action taken: none required

### Outlier Detection and Treatment

An IQR-style reasonableness check was applied to numeric fields.

- `User_Skill_Count`: no outliers
- `Job_Req_Count`: no outliers
- `Experience_Years`: no outliers
- `Skill_Overlap_Count`: `194` observations above the upper IQR bound, but these are plausible high-match cases rather than data errors

Because the overlap outliers are analytically meaningful, they were retained.

### Standardisation and Data Types

- IDs retained as strings
- Count fields stored as integers
- Skills standardised to lowercase comma-separated tokens
- Categorical labels normalised for band, education, role, and location fields

### Feature Engineering

| Derived Field | Logic | Purpose |
|---------------|-------|---------|
| `skill_gap` | `job_req_count - skill_overlap_count` | Measures unmet demand |
| `overlap_ratio` | `skill_overlap_count / job_req_count` | Normalised fit indicator |
| `candidate_readiness` | Banded from overlap ratio | Supports dashboard segmentation |

### Assumptions

- Exact skill name overlap is an acceptable proxy for candidate-job fit.
- The uploaded score band can be used directionally even without a raw numeric score.
- High overlap observations are valid business signals, not noise.
- Since no outcome label exists, fit analysis substitutes for recommendation modelling.

### Notebook Reference

The cleaning logic is aligned to the capstone ETL workflow and should be reflected in `notebooks/02_cleaning.ipynb` during final notebook refresh.

## 7. KPI & Metric Framework

### Core KPIs

| KPI | Logic | Why It Matters |
|-----|-------|----------------|
| Average Skill Overlap | Mean of `skill_overlap_count` | Shows average alignment between supply and demand |
| Average Skill Gap | Mean of `skill_gap` | Quantifies unmet skill requirements |
| Overlap Ratio | `skill_overlap_count / job_req_count` | Normalises fit across jobs with different requirement counts |
| Match Band Mix | Share of `Low`, `Medium`, `High` | Summarises overall portfolio quality |
| Role Fit Score | Mean overlap ratio by `job_role` | Helps prioritise hiring intervention by role |
| Location Fit Score | Mean overlap ratio by `location` | Reveals market-wise sourcing friction |

### KPI-to-Objective Mapping

| Objective | KPI |
|-----------|-----|
| Quantify overall market fit | Average skill overlap, overlap ratio |
| Identify shortage severity | Average skill gap, match band mix |
| Prioritise hiring segments | Role fit score, location fit score |
| Guide upskilling strategy | Top demanded skills, top overlap skills |

## 8. Exploratory Data Analysis (EDA)

### Distribution Analysis

- Average candidate skills: `5.00`
- Average job requirements: `5.02`
- Average exact overlap: `1.27`
- Median overlap ratio: `0.25`
- Average skill gap: `3.75`

This shows that the average candidate covers only about one quarter of required skills, which is a major operational signal for recruiters and learning teams.

### Match Band Distribution

| Match Band | Count | Share |
|------------|-------|-------|
| Low | `6,158` | `61.58%` |
| Medium | `3,686` | `36.86%` |
| High | `156` | `1.56%` |

The business meaning is clear: high-quality matches are scarce. Most candidate-job pairings are not immediately shortlist-ready, so the organisation must either reduce screening waste or actively close the skill gap.

### Comparison Across Roles

| Job Role | Avg Overlap | Avg Overlap Ratio | Avg Skill Gap |
|----------|-------------|-------------------|---------------|
| Business Analyst | `1.332` | `0.262` | `3.751` |
| Software Engineer | `1.318` | `0.263` | `3.673` |
| Data Scientist | `1.276` | `0.253` | `3.772` |
| DevOps Engineer | `1.272` | `0.251` | `3.765` |
| Backend Developer | `1.256` | `0.251` | `3.739` |
| Data Analyst | `1.244` | `0.251` | `3.788` |
| ML Engineer | `1.160` | `0.240` | `3.757` |

`ML Engineer` emerges as the hardest-fit role in the dataset, suggesting a tighter supply-demand mismatch. `Business Analyst` and `Software Engineer` are comparatively healthier, though still far from strong-fit territory.

### Comparison Across Locations

| Location | Avg Overlap | Avg Overlap Ratio |
|----------|-------------|-------------------|
| Mumbai | `1.289` | `0.256` |
| Hyderabad | `1.275` | `0.254` |
| Delhi | `1.271` | `0.254` |
| Bangalore | `1.266` | `0.251` |
| Chennai | `1.258` | `0.253` |
| Pune | `1.240` | `0.250` |

Location differences are modest, which suggests the bigger issue is not geography alone but role-specific skill supply.

### Comparison Across Education Segments

Education level shows only small differences in overlap ratio, indicating that formal qualification by itself is a weak screening shortcut. This matters because many employers overuse degree-based filters when actual skills are the stronger signal.

### Skill Frequency Analysis

**Top candidate skills**

`Leadership`, `Kubernetes`, `TensorFlow`, `C++`, `Python`, `Machine Learning`, `Excel`, `Java`, `NLP`, `Pandas`

**Top required job skills**

`Python`, `Statistics`, `AWS`, `Kubernetes`, `SQL`, `Communication`, `Data Analysis`, `C++`, `Docker`, `Excel`

**Top actual overlap skills**

`Kubernetes`, `Statistics`, `Leadership`, `SQL`, `Machine Learning`, `Pandas`, `NumPy`, `Java`, `Python`, `Docker`

The interpretation is important. Some skills are common on both sides, but overlap remains low, which means demand is broad while candidate skill bundles are not aligned in the right combinations.

### Correlation Analysis

| Variable Pair | Correlation | Interpretation |
|---------------|-------------|----------------|
| User Skill Count vs Skill Overlap | `0.361` | Candidates with more skills tend to fit more roles |
| Job Requirement Count vs Skill Overlap | `0.354` | More complex jobs still create more absolute overlap opportunities |
| Experience vs Skill Overlap | `-0.014` | Experience adds almost no explanatory power |
| Overlap Ratio vs Skill Gap | `-0.630` | Higher fit strongly reduces unmet skill demand |

Business takeaway: experience-heavy screening is less useful than skill-based screening in this dataset.

### Trend Analysis

Not applicable because the uploaded dataset has no time field.

### Notebook Reference

EDA outputs map to `notebooks/03_eda.ipynb` and the Tableau-ready extracts in `data/processed/`.

## 9. Statistical Analysis

The dataset does not support forecasting or outcome prediction because it lacks time and recommendation labels. Instead, statistical analysis was reframed toward segmentation, risk detection, and root-cause diagnosis.

### Segmentation

Three readiness tiers were defined from overlap ratio:

- Low readiness: overlap ratio `<= 0.20`
- Medium readiness: overlap ratio `> 0.20` and `<= 0.40`
- High readiness: overlap ratio `> 0.40`

This segmentation supports operational routing. Low-readiness records are better suited for nurture or training pathways, while medium-readiness records are stronger shortlist candidates.

### Root Cause Analysis

The weak overall fit is primarily driven by two conditions:

- candidate skill inventory is not aligned to the most demanded employer skill bundles
- job postings require materially more matched skills than candidates currently demonstrate

The average job requires `5.02` skills, but exact overlap is only `1.27`, leaving a large structural gap.

### Risk and Anomaly Detection

High-overlap cases are rare but strategically important. Only `1.56%` of records fall in the `High` match band. This scarcity is a hiring risk because strong-fit talent pools may be too small to support scale hiring without proactive sourcing or upskilling.

### Scenario Analysis

If average overlap improved by one additional matched skill per candidate-job pair, the average skill gap would fall from `3.75` to `2.75`, a reduction of about `26.7%`. Even a modest skill-alignment improvement could therefore materially improve shortlist efficiency.

### Notebook Reference

The statistical interpretation should be reflected in `notebooks/04_statistical_analysis.ipynb` during final submission cleanup.

## 10. Tableau Dashboard Design

### Dashboard Objective

The dashboard should help HR leaders answer one core question: where are the biggest candidate-job fit gaps, and which roles or markets need intervention first?

### Suggested View Structure

**Executive summary view**

- Total records
- Match band distribution
- Average overlap ratio
- Average skill gap
- Top mismatch roles
- Top demanded skills

**Operational drill-down view**

- Filters for role, location, education level, and readiness tier
- Heatmap of demand vs overlap skills
- Role-wise and city-wise fit comparison
- Candidate-readiness distribution

### Filters and Interactions

- `Job_Role`
- `Location`
- `Education_Level`
- `Match_Score_Band`
- `Candidate_Readiness`

### Screenshots and References

Screenshots should be stored under `tableau/screenshots/`.  
Published link should be added to [`tableau/dashboard_links.md`](/Users/rahuldhakar/Desktop/DATA/CAPSTONE/tableau/dashboard_links.md).

## 11. Insights Summary

1. Most candidate-job matches are weak, with `61.58%` of records in the low-fit band.
2. Average exact overlap is only `1.27` skills against `5.02` required skills, indicating a structurally underqualified pipeline.
3. The average skill gap of `3.75` shows that most roles need substantial upskilling or broader sourcing.
4. `ML Engineer` has the lowest average overlap ratio, making it the highest-priority role for sourcing intervention.
5. `Business Analyst` and `Software Engineer` show relatively better fit, but the difference is small and does not eliminate shortage risk.
6. Experience does not explain fit in this dataset, so skill-based screening is more valuable than tenure-based filtering.
7. Role and skill mismatch matter more than geography, since location-level differences are narrow.
8. Employer demand is concentrated around `Python`, `AWS`, `SQL`, `Communication`, and `Data Analysis`, so these should anchor talent development plans.
9. Only a tiny fraction of records are high-fit, meaning recruiters should preserve and fast-track these candidates.
10. Degree level alone is a weak differentiator, which supports more inclusive, skills-first hiring logic.

## 12. Recommendations

| Insight | Recommendation | Expected Business Impact | Feasibility |
|---------|----------------|--------------------------|-------------|
| Large average skill gap | Launch targeted upskilling tracks around top-demand skills | Improves candidate readiness and shortlist quality | Medium |
| ML Engineer fit is weakest | Allocate specialist sourcing budget and niche-channel outreach to ML roles | Reduces hard-to-fill vacancy delays | Medium |
| High-fit candidates are scarce | Fast-track high-readiness candidates with dedicated recruiter SLAs | Prevents loss of top-fit talent | High |
| Experience is weak as a predictor | Shift screening rules toward skill overlap and readiness tiers | Reduces false negatives in candidate selection | High |
| Geography differences are small | Rebalance sourcing by role before expanding city-level campaigns | Improves recruitment spend efficiency | High |

## 13. Impact Estimation

The following estimates are directional but business-reasonable:

- If the organisation reduces average skill gap by `1` skill per match, shortlist quality could improve enough to cut early-stage screening waste by roughly `20%` to `30%`.
- If hard-to-fill roles such as `ML Engineer` are supported with specialised sourcing, time-to-fill could reasonably improve by `10%` to `15%`.
- If high-readiness candidates are automatically prioritised, recruiter effort spent on low-fit applications could drop materially, creating efficiency gains without additional hiring headcount.

The stakeholder should act now because the current fit distribution is heavily skewed toward weak matches. Waiting increases sourcing costs and leaves specialised vacancies open longer.

## 14. Limitations

- No time variable means the report cannot claim hiring trends or forecast future demand.
- No hiring outcome label means this is a fit diagnostic, not a validated predictive hiring model.
- Exact string overlap may miss semantically similar skills.
- The dataset appears synthetic, so live-market deployment should include validation on real ATS data.
- The report cannot estimate revenue impact directly because no cost-per-hire or vacancy-cost data was supplied.

## 15. Future Scope

- Add application dates to enable trend and seasonality analysis.
- Add recommendation, interview, and hiring outcome labels to build predictive models.
- Add salary, company, and seniority fields for deeper market segmentation.
- Add embeddings or ontology-based skill mapping to capture semantic similarity.
- Publish a live Tableau dashboard or real-time operational dashboard connected to hiring systems.

## 16. Conclusion

This project delivered a practical talent-intelligence analysis of candidate-job fit using a structured resume-job matching dataset. The Python ETL pipeline cleaned and standardised the uploaded data, engineered fit metrics, and produced dashboard-ready outputs. The key insight is that the market represented here is dominated by low-fit matches, with substantial skill gaps across nearly every role. The recommended action is to move toward skills-first hiring operations, role-specific sourcing strategy, and targeted upskilling programs to improve shortlist quality and reduce recruitment inefficiency.

## 17. Appendix

### A. Data Dictionary

See [`docs/data_dictionary.md`](/Users/rahuldhakar/Desktop/DATA/CAPSTONE/docs/data_dictionary.md).

### B. Useful Logic Excerpts

- ETL and export logic: [`scripts/etl_pipeline.py`](/Users/rahuldhakar/Desktop/DATA/CAPSTONE/scripts/etl_pipeline.py)
- Cleaned outputs: `data/processed/jobs_cleaned.csv`, `data/processed/jobs_tableau_ready.csv`, `data/processed/skill_frequency.csv`

### C. Raw Cleaning Log Summary

- Rows loaded: `10,000`
- Columns loaded: `12`
- Missing values: `0`
- Duplicates removed: `0`
- Records retained after cleaning: `10,000`

### D. Additional EDA Notes

- Median overlap ratio: `0.25`
- 90th percentile overlap ratio: `0.50`
- Correlation between overlap ratio and skill gap: `-0.630`

## 18. Contribution Matrix

| Team Member | Dataset & Sourcing | ETL & Cleaning | EDA & Analysis | Statistical Analysis | Tableau Dashboard | Report Writing | PPT & Viva |
|-------------|--------------------|----------------|----------------|----------------------|------------------|----------------|------------|
| Rahul Dhakar | High | High | Medium | Medium | Low | Medium | Medium |
| Harsh Raj | Medium | Medium | High | High | Medium | High | Medium |
| Suraj Kumar Rai | Low | Low | Medium | Low | High | Medium | Medium |
| Harshil Singh | Low | Low | Medium | Medium | Medium | High | High |

> Final contribution claims must be aligned with GitHub commits, pull requests, notebook ownership, and dashboard evidence before submission.
