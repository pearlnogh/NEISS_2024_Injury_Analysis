# Factors Associated with Hospital Admission After Emergency Department Injury Visits: A Nationally Representative Analysis Using NEISS 2024 Data.
## Project Overview
This project analyzes nationally representative 2024 emergency department injury data from the National Electronic Injury Surveillance System (NEISS) to examine how demographic, injury-related, and incident characteristics are associated with patient disposition.

## Project Structure
```text
NEISS_2024_Injury_Analysis/
│
├── raw_data/                            # Original unmodified datasets
│   ├── neiss_2024_raw.xlsx
│   └── neiss_2022_dictionary.xlsx
│
├── cleaned_data/                        # Datasets after preprocessing
│   └── neiss_2024_cleaned.csv
│
├── notebooks/                           # Python workflow scripts
│   ├── 01_data_overview.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_statistical_analysis.ipynb
│   ├── 05_modeling_baseline.ipynb
│   └── 06_modeling_iteration.ipynb
│  
├── models/                             
│   ├── model_baseline.pkl
│   └── model_iteration.pkl
│
├── app/                                
│   └── app.py  
│
├── docs/                                # Final Project Deliverables
│   ├── Final_Report.pdf
│   └── NEISS_2024_Injury_Analysis.pptx
│
├── requirements.txt                     # Python dependencies
└── README.md                            # Project documentation
```

## Team Members
- Ameenat Ali
- Foluso Ojo
- Gurpreet Kaur
- Pei- Ru Chen
