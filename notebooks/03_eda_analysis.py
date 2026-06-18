# ==============================================================
# FILE: 03_eda_analysis.py
# PURPOSE: Answer business questions through data analysis
# ==============================================================

import pandas as pd
import numpy as np

df = pd.read_csv("data/cleaned/shopsphere_clean.csv")

print("PHASE 2: EXPLORATORY DATA ANALYSIS")
print("=" * 55)
print(f"Loaded {df.shape[0]:,} customer records\n")


# ── BUSINESS QUESTION 1: Overall Churn Rate ───────────────────
print("━" * 55)
print("Q1: WHAT IS THE OVERALL CHURN RATE?")
print("━" * 55)

total       = len(df)
churned     = df["Churn"].sum()
retained    = total - churned
churn_rate  = df["Churn"].mean()
revenue_risk = churned * 85  # Estimated $85 avg monthly revenue per customer

print(f"  Total customers  : {total:,}")
print(f"  Churned          : {churned:,}")
print(f"  Retained         : {retained:,}")
print(f"  Churn Rate       : {churn_rate:.1%}")
print(f"  Revenue at Risk  : ${revenue_risk:,.0f} per month")
print(f"  Annual Risk      : ${revenue_risk * 12:,.0f}")


# ── BUSINESS QUESTION 2: Complaints vs Churn ─────────────────
print("\n" + "━" * 55)
print("Q2: DO COMPLAINTS PREDICT CHURN?")
print("━" * 55)

# Calculate churn rate for each complaint group
complaint_groups = df.groupby("Complain").agg(
    Customers  = ("Churn", "count"),
    Churned    = ("Churn", "sum"),
    Churn_Rate = ("Churn", "mean")
).reset_index()

# Make labels readable
complaint_groups["Complain"] = complaint_groups["Complain"].map(
    {0: "No Complaint", 1: "Had Complaint"}
)
complaint_groups["Churn_Rate_%"] = (complaint_groups["Churn_Rate"] * 100).round(1)

print(complaint_groups[["Complain", "Customers", "Churned", "Churn_Rate_%"]].to_string(index=False))

# Calculate the lift (how many times more likely to churn)
rate_no_complaint  = df[df["Complain"] == 0]["Churn"].mean()
rate_had_complaint = df[df["Complain"] == 1]["Churn"].mean()
churn_lift = rate_had_complaint / rate_no_complaint

print(f"\n  No complaint churn rate  : {rate_no_complaint:.1%}")
print(f"  Had complaint churn rate : {rate_had_complaint:.1%}")
print(f"  Churn LIFT from complaining: {churn_lift:.1f}x higher risk")
print(f"\n  INSIGHT: A customer who complains is {churn_lift:.1f}x MORE")
print(f"  likely to leave than one who does not complain.")


# ── BUSINESS QUESTION 3: Churn by Product Category ───────────
print("\n" + "━" * 55)
print("Q3: WHICH PRODUCT CATEGORIES HAVE HIGHEST CHURN?")
print("━" * 55)

category_analysis = (
    df.groupby("PreferredOrderCat")
    .agg(
        Customers        = ("Churn", "count"),
        Churned          = ("Churn", "sum"),
        Churn_Rate       = ("Churn", "mean"),
        Avg_Satisfaction = ("SatisfactionScore", "mean"),
        Avg_Cashback     = ("CashbackAmount", "mean")
    )
    .sort_values("Churn_Rate", ascending=False)
    .reset_index()
)

category_analysis["Churn_Rate_%"]    = (category_analysis["Churn_Rate"] * 100).round(1)
category_analysis["Avg_Satisfaction"] = category_analysis["Avg_Satisfaction"].round(2)
category_analysis["Avg_Cashback"]     = category_analysis["Avg_Cashback"].round(2)

print(category_analysis[[
    "PreferredOrderCat", "Customers", "Churned",
    "Churn_Rate_%", "Avg_Satisfaction", "Avg_Cashback"
]].to_string(index=False))

highest_churn_cat = category_analysis.iloc[0]["PreferredOrderCat"]
highest_rate      = category_analysis.iloc[0]["Churn_Rate_%"]
print(f"\n  INSIGHT: '{highest_churn_cat}' buyers have the highest churn at {highest_rate}%")


# ── BUSINESS QUESTION 4: Distance vs Churn ───────────────────
print("\n" + "━" * 55)
print("Q4: HOW DOES WAREHOUSE DISTANCE AFFECT CHURN?")
print("━" * 55)

# Compare averages for churned vs retained
distance_comparison = df.groupby("Churn")["WarehouseToHome"].agg(
    ["mean", "median", "min", "max"]
).round(2)
distance_comparison.index = ["Retained Customers", "Churned Customers"]
print(distance_comparison)

# Churn rate by distance band
distance_band_analysis = (
    df.groupby("Distance_Category", observed=True)["Churn"]
    .agg(
        Customers  = "count",
        Churn_Rate = "mean"
    )
    .reset_index()
)
distance_band_analysis["Churn_Rate_%"] = (
    distance_band_analysis["Churn_Rate"] * 100
).round(1)

print(f"\n  Churn by Distance Band:")
print(distance_band_analysis[["Distance_Category", "Customers", "Churn_Rate_%"]].to_string(index=False))

avg_distance_churned  = df[df["Churn"] == 1]["WarehouseToHome"].mean()
avg_distance_retained = df[df["Churn"] == 0]["WarehouseToHome"].mean()
print(f"\n  Average distance for churned customers : {avg_distance_churned:.1f} km")
print(f"  Average distance for retained customers: {avg_distance_retained:.1f} km")
print(f"  Difference: {avg_distance_churned - avg_distance_retained:.1f} km farther for churned")


# ── BONUS: Tenure vs Churn ────────────────────────────────────
print("\n" + "━" * 55)
print("BONUS: CHURN RATE BY CUSTOMER TENURE")
print("━" * 55)

tenure_analysis = (
    df.groupby("Tenure_Bucket", observed=True)["Churn"]
    .agg(
        Customers  = "count",
        Churn_Rate = "mean"
    )
    .reset_index()
)
tenure_analysis["Churn_Rate_%"] = (tenure_analysis["Churn_Rate"] * 100).round(1)
print(tenure_analysis[["Tenure_Bucket", "Customers", "Churn_Rate_%"]].to_string(index=False))


# ── BONUS: Cashback vs Churn ──────────────────────────────────
print("\n" + "━" * 55)
print("BONUS: CASHBACK AMOUNT VS CHURN RATE")
print("━" * 55)

cashback_bins = pd.cut(
    df["CashbackAmount"],
    bins   = [0, 100, 150, 200, 250, 400],
    labels = ["$0-100", "$100-150", "$150-200", "$200-250", "$250-400"]
)
cashback_analysis = (
    df.groupby(cashback_bins, observed=True)["Churn"]
    .agg(Customers="count", Churn_Rate="mean")
    .reset_index()
)
cashback_analysis["Churn_Rate_%"] = (cashback_analysis["Churn_Rate"] * 100).round(1)
print(cashback_analysis[["CashbackAmount", "Customers", "Churn_Rate_%"]].to_string(index=False))

print("\n" + "=" * 55)
print("EDA COMPLETE")
print("All findings ready. Run 04_visualizations.py next.")
print("=" * 55)