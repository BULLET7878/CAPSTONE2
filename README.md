# 🎯 Capstone 2 — Job Market Analytics
### HR Tech | Skills-to-Recommendation Intelligence

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python) ![Tableau](https://img.shields.io/badge/Tableau-Dashboard-orange?logo=tableau) ![Pandas](https://img.shields.io/badge/Pandas-ETL-green?logo=pandas) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 📌 Problem Statement

> **Which skills drive job recommendation success, and can we predict whether a candidate will be recommended based on their skill-match score?**

In a rapidly evolving labour market, HR platforms rely on algorithmic matching to connect candidates with opportunities. This project performs a full end-to-end analytical workflow on a 100,000-record job recommendation dataset to uncover the drivers of successful placements.

---

## 👥 Team

| Member | Role |
|--------|------|
| Rahul Dhakar | Data Engineer & ETL Lead |
| Parth P | EDA & Statistical Analysis |
| *(Team members)* | Tableau & Visualization |
| *(Team members)* | Documentation & Reporting |
| *(Team members)* | Presentation Lead |

---

## 🗂️ Repository Structure

```
Capstone_DVA_2/
├── README.md
├── data/
│   ├── raw/            ← Original dataset (never edited)
│   └── processed/      ← Cleaned output from ETL pipeline
├── notebooks/
│   ├── 01_extraction.ipynb
│   ├── 02_cleaning.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_statistical_analysis.ipynb
│   └── 05_final_load_prep.ipynb
├── scripts/
│   └── etl_pipeline.py
├── tableau/
│   ├── screenshots/
│   └── dashboard_links.md
├── reports/
│   ├── project_report.pdf
│   └── presentation.pdf
└── docs/
    └── data_dictionary.md
```

---

## 🔄 Workflow

```
Raw XLSX → [01] Extract → [02] Clean → [03] EDA → [04] Stats → [05] Export → Tableau
```

1. **Extraction** — Load raw Excel, validate schema, profile data quality  
2. **Cleaning** — Handle nulls, standardize skill lists, remove duplicates  
3. **EDA** — Distributions, skill frequency, match score analysis, correlation heatmaps  
4. **Statistical Analysis** — t-tests, chi-square, ANOVA, logistic regression  
5. **Final Load Prep** — Export Tableau-ready CSVs, summary aggregations  

---

## 📊 Dataset

| Field | Type | Description |
|-------|------|-------------|
| `User_ID` | int | Unique candidate identifier |
| `Job_ID` | int | Unique job posting identifier |
| `User_Skills` | str | Pipe-separated list of candidate skills |
| `Job_Requirements` | str | Pipe-separated list of required skills |
| `Match_Score` | float | Algorithmic match score (0–100) |
| `Recommended` | int | Binary recommendation outcome (0/1) |

**Size:** 100,000 rows × 6 columns  
**Source:** Synthetic HR Tech simulation dataset

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Parth10P/Capstone_DVA_2.git
cd Capstone_DVA_2

# 2. Create virtual environment
python3 -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install pandas openpyxl scipy matplotlib seaborn scikit-learn statsmodels jupyter

# 4. Run ETL pipeline
python scripts/etl_pipeline.py

# 5. Launch notebooks
jupyter notebook notebooks/
```

---

## 📈 Key Findings *(to be updated after analysis)*

- TBD after EDA completion  
- TBD after statistical analysis  
- Dashboard link: see `tableau/dashboard_links.md`

---

## 📁 Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready, reviewed code only |
| `dev` | Active development |
| `feature/notebook-X` | Per-notebook feature branches |

---

*Capstone 2 — Data Visualization & Analytics | 2026*
