# ==============================================================
# FILE: 01_data_generation.py
# PURPOSE: Generate realistic mock customer data for ShopSphere
# ==============================================================

import pandas as pd
import numpy as np
import random
from faker import Faker

# --- Configuration ---
fake = Faker()
np.random.seed(42)
random.seed(42)
NUM_CUSTOMERS = 5000

def calculate_churn_probability(tenure, satisfaction, complain, distance, cashback):
    """
    Calculates churn probability based on customer attributes.
    Higher risk factors increase probability, retention factors decrease it.
    """
    base_prob = 0.20

    # Tenure effect
    if tenure < 3:
        base_prob += 0.30
    elif tenure < 6:
        base_prob += 0.15
    elif tenure > 24:
        base_prob -= 0.10

    # Satisfaction effect
    if satisfaction <= 2:
        base_prob += 0.25
    elif satisfaction == 3:
        base_prob += 0.05
    elif satisfaction >= 4:
        base_prob -= 0.10

    # Complaint effect (biggest single factor)
    if complain == 1:
        base_prob += 0.35

    # Distance effect
    if distance > 25:
        base_prob += 0.15
    elif distance > 15:
        base_prob += 0.07

    # Cashback effect (retention incentive)
    if cashback > 250:
        base_prob -= 0.12
    elif cashback > 150:
        base_prob -= 0.06

    return max(0.05, min(0.95, base_prob))


print("Generating customer data...")
records = []

for i in range(1, NUM_CUSTOMERS + 1):

    customer_id     = f"CUST-{i:05d}"
    tenure          = np.random.randint(1, 61)
    distance        = np.random.randint(5, 50)
    satisfaction    = np.random.randint(1, 6)
    marital_status  = random.choice(["Single", "Married", "Divorced"])
    order_cat       = random.choice(["Laptop & Accessory", "Mobile Phone",
                                     "Fashion", "Grocery", "Others"])
    complain        = np.random.choice([0, 1], p=[0.70, 0.30])
    days_last_order = np.random.randint(1, 45)
    cashback        = round(np.random.uniform(50, 400), 2)
    login_freq      = random.choice(["Daily", "Weekly", "Monthly", "Rarely"])

    # Introduce realistic missing values (~5%)
    if random.random() < 0.05:
        tenure = np.nan
    if random.random() < 0.05:
        days_last_order = np.nan
    if random.random() < 0.03:
        cashback = np.nan

    # Introduce realistic outliers (~1%)
    if random.random() < 0.01:
        distance = random.choice([-5, 200, 999])
    if random.random() < 0.01:
        cashback = random.choice([-50, 5000])

    # Calculate churn
    churn_prob = calculate_churn_probability(
        tenure       = tenure if not pd.isna(tenure) else 5,
        satisfaction = satisfaction,
        complain     = complain,
        distance     = distance if distance > 0 else 5,
        cashback     = cashback if not pd.isna(cashback) else 150
    )
    churn = int(random.random() < churn_prob)

    records.append({
        "CustomerID"        : customer_id,
        "Tenure"            : tenure,
        "WarehouseToHome"   : distance,
        "Churn"             : churn,
        "PreferredOrderCat" : order_cat,
        "SatisfactionScore" : satisfaction,
        "MaritalStatus"     : marital_status,
        "Complain"          : complain,
        "DaySinceLastOrder" : days_last_order,
        "CashbackAmount"    : cashback,
        "LoginFrequency"    : login_freq,
    })

df_raw = pd.DataFrame(records)
df_raw.to_csv("data/raw/shopsphere_raw.csv", index=False)

print("=" * 50)
print(f"Dataset created: {df_raw.shape[0]:,} rows x {df_raw.shape[1]} columns")
print(f"Churn rate: {df_raw['Churn'].mean():.1%}")
print(f"\nMissing values:")
print(df_raw.isnull().sum()[df_raw.isnull().sum() > 0])
print(f"\nFile saved to: data/raw/shopsphere_raw.csv")
print("=" * 50)