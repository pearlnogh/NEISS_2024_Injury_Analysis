# Factors Associated with Hospital Admission After Emergency Department Injury Visits: A Nationally Representative Analysis Using NEISS 2024 Data.
## Project Overview
This project analyzes nationally representative 2024 emergency department injury data from the National Electronic Injury Surveillance System (NEISS) to examine how demographic, injury-related, and incident characteristics are associated with patient disposition.

## Project Structure
```text
NEISS_2024_Injury_Analysis/
│
├── raw_data/                          # Original unmodified datasets
│   ├── neiss_2024_cleaned.xlsx
│   └── neiss_2022_dictionary.xlsx   
│
├── cleaned_data/                      # Datasets after preprocessing
│   ├── neiss_2024_cleaned.xlsx
│   └── neiss_2024_dictionary.xlsx    
│
├── python_scripts/                    # Python workflow scripts
│   ├── 01_neiss_data_overview.ipynb
│   ├── 02_neiss_data_cleaning.ipynb
│   ├── 03_neiss_feature_engineering.ipynb
│   └── 04_neiss_data_export.ipynb
│
├── eda/                               # All exploratory data analysis work
│   ├── eda_questions.ipynb
│   └── neiss_2024_eda.ipynb           # Univariate, Bivariate & Multivariate analysis
│
├── docs/                              # Final Project Deliverables
│   ├── data_dictionary.md
│   ├── neiss_2024_final_report.pdf
│   └── tableau/
│       ├── dashboard_screenshots/
│       └── tableau_story_outline.md
│
├── requirements.txt                   # Python dependencies
│
└── README.md                          # Project documentation
```

## Team Members
Ameenat Ali
Foluso Ojo
Gurpreet Kaur
Pei- Ru Chen
