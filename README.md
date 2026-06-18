# shopsphere-churn-analysis
End-to-end customer churn analysis using Python and SQL

# ShopSphere Customer Churn Analysis

## What This Project Does
Analyzes 5,000 customer records to identify why customers leave
ShopSphere and which customers are at highest risk of churning.

## Tech Stack
- Python (pandas, numpy, matplotlib, seaborn) — Data cleaning and analysis
- SQL (SQLite) — Business question queries
- Faker — Realistic data generation

## Key Findings
- 38% overall churn rate = $1.6M annual revenue at risk
- Customers who complain are 2.4x more likely to churn
- 67% of customers in their first 3 months churn
- Churn rate doubles for customers living over 20km from warehouse

## How to Run
pip install pandas numpy matplotlib seaborn faker
python notebooks/01_data_generation.py
python notebooks/02_data_cleaning.py
python notebooks/03_eda_analysis.py
python notebooks/04_visualizations.py

## Business Impact
Three recommendations with estimated $70,000/month in
recoverable revenue. See reports/business_recommendations.md

