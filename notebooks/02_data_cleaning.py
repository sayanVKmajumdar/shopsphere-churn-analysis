# ==============================================================
# FILE: 02_data_cleaning.py
# PURPOSE: Clean and transform the raw ShopSphere dataset
# ==============================================================

import pandas as pd
import numpy as np

# --- Load the raw data ---
df = pd.read_csv("data/raw/shopsphere_raw.csv")

print("PHASE 1: DATA CLEANING")
print("=" * 50)
print(f"Starting shape: {df.shape[0]:,} rows x {df.shape[1]} columns")


# ── STEP 1: Initial Audit ────────────────────────────────────
print("\n[1/5] INITIAL AUDIT")
print("-" * 40)
print("Column data types:")
print(df.dtypes)
print("\nNull counts per column:")
print(df.isnull().sum())
print("\nBasic statistics:")
print(df.describe().round(2))


# ── STEP 2: Fix Outliers BEFORE Imputation ───────────────────
print("\n[2/5] FIXING OUTLIERS")
print("-" * 40)

# Distance must be between 1 and 100 km
bad_distance = (df["WarehouseToHome"] < 1) | (df["WarehouseToHome"] > 100)
print(f"  Bad distance values found: {bad_distance.sum()}")
df.loc[bad_distance, "WarehouseToHome"] = np.nan

# Cashback must be between $0 and $1000
bad_cashback = (df["CashbackAmount"] < 0) | (df["CashbackAmount"] > 1000)
print(f"  Bad cashback values found: {bad_cashback.sum()}")
df.loc[bad_cashback, "CashbackAmount"] = np.nan

# Tenure cannot be negative
bad_tenure = df["Tenure"] < 0
print(f"  Negative tenure values found: {bad_tenure.sum()}")
df.loc[bad_tenure, "Tenure"] = np.nan

# Satisfaction must be 1 to 5
bad_satisfaction = ~df["SatisfactionScore"].between(1, 5)
print(f"  Bad satisfaction scores found: {bad_satisfaction.sum()}")
df = df[~bad_satisfaction].copy()


# ── STEP 3: Fill Missing Values ───────────────────────────────
print("\n[3/5] FILLING MISSING VALUES")
print("-" * 40)

# Use median for all numerical columns
# Median is better than mean because it is not affected by outliers
median_columns = ["Tenure", "DaySinceLastOrder", "CashbackAmount", "WarehouseToHome"]

for col in median_columns:
    missing_count = df[col].isnull().sum()
    if missing_count > 0:
        median_value = df[col].median()
        df[col] = df[col].fillna(median_value)
        print(f"  {col}: filled {missing_count} nulls with median = {median_value:.1f}")

print(f"\n  Total nulls remaining: {df.isnull().sum().sum()}")


# ── STEP 4: Create New Columns ────────────────────────────────
print("\n[4/5] CREATING NEW FEATURES")
print("-" * 40)

# App Usage Level (from LoginFrequency)
usage_mapping = {
    "Daily"   : "High",
    "Weekly"  : "Medium",
    "Monthly" : "Low",
    "Rarely"  : "Very Low"
}
df["App_Usage_Level"] = df["LoginFrequency"].map(usage_mapping)
print(f"  App_Usage_Level created")
print(f"  Values: {df['App_Usage_Level'].value_counts().to_dict()}")

# Tenure Bucket — groups customers by how long they have been around
df["Tenure_Bucket"] = pd.cut(
    df["Tenure"],
    bins   = [0, 3, 6, 12, 24, 99],
    labels = ["0-3 Mo", "3-6 Mo", "6-12 Mo", "12-24 Mo", "24+ Mo"]
)
print(f"\n  Tenure_Bucket created")
print(f"  Distribution:\n{df['Tenure_Bucket'].value_counts().sort_index()}")

# Distance Category
df["Distance_Category"] = pd.cut(
    df["WarehouseToHome"],
    bins   = [0, 10, 20, 30, 100],
    labels = ["Under 10km", "10-20km", "20-30km", "Over 30km"]
)

# High Cashback flag (top 25% of cashback receivers)
cashback_75th_percentile = df["CashbackAmount"].quantile(0.75)
df["High_Cashback"] = (df["CashbackAmount"] >= cashback_75th_percentile).astype(int)
print(f"\n  High Cashback threshold: ${cashback_75th_percentile:.2f}")

# Inactive flag — has not ordered in 30+ days
df["Inactive_Flag"] = (df["DaySinceLastOrder"] >= 30).astype(int)
print(f"  Inactive customers (30+ days no order): {df['Inactive_Flag'].sum():,}")


# ── STEP 5: Save Clean Data ───────────────────────────────────
print("\n[5/5] SAVING CLEAN DATA")
print("-" * 40)
print(f"  Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"  Churn rate in clean data: {df['Churn'].mean():.1%}")
print(f"  Zero nulls remaining: {df.isnull().sum().sum() == 0}")

df.to_csv("data/cleaned/shopsphere_clean.csv", index=False)
print(f"\n  SUCCESS: Saved to data/cleaned/shopsphere_clean.csv")
print("=" * 50)