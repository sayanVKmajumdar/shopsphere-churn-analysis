-- ==============================================================
-- FILE: churn_analysis_queries.sql
-- PURPOSE: Analyze ShopSphere churn data using SQL
-- Run in: DB Browser for SQLite
-- ==============================================================


-- ── Q1: Overall Churn Rate ────────────────────────────────────
SELECT
    COUNT(*)                              AS Total_Customers,
    SUM(Churn)                            AS Total_Churned,
    COUNT(*) - SUM(Churn)                 AS Total_Retained,
    ROUND(AVG(Churn) * 100.0, 2)          AS Churn_Rate_Pct,
    SUM(Churn) * 85                       AS Monthly_Revenue_At_Risk_USD
FROM shopsphere_customers;


-- ── Q2: Complaint vs Churn ────────────────────────────────────
SELECT
    CASE
        WHEN Complain = 1 THEN 'Had Complaint'
        ELSE 'No Complaint'
    END                                   AS Complaint_Status,
    COUNT(*)                              AS Total_Customers,
    SUM(Churn)                            AS Churned,
    ROUND(AVG(Churn) * 100.0, 2)          AS Churn_Rate_Pct,
    ROUND(AVG(SatisfactionScore), 2)      AS Avg_Satisfaction
FROM shopsphere_customers
GROUP BY Complain
ORDER BY Churn_Rate_Pct DESC;


-- ── Q3: Churn by Product Category ────────────────────────────
SELECT
    PreferredOrderCat,
    COUNT(*)                              AS Total_Customers,
    SUM(Churn)                            AS Churned,
    ROUND(AVG(Churn) * 100.0, 2)          AS Churn_Rate_Pct,
    ROUND(AVG(SatisfactionScore), 2)      AS Avg_Satisfaction,
    ROUND(AVG(CashbackAmount), 2)         AS Avg_Cashback
FROM shopsphere_customers
GROUP BY PreferredOrderCat
ORDER BY Churn_Rate_Pct DESC;


-- ── Q4: Distance vs Churn ─────────────────────────────────────
SELECT
    CASE
        WHEN Churn = 1 THEN 'Churned'
        ELSE 'Retained'
    END                                   AS Status,
    ROUND(AVG(WarehouseToHome), 2)        AS Avg_Distance_km,
    ROUND(MIN(WarehouseToHome), 2)        AS Min_Distance_km,
    ROUND(MAX(WarehouseToHome), 2)        AS Max_Distance_km,
    COUNT(*)                              AS Customer_Count
FROM shopsphere_customers
GROUP BY Churn;


-- ── BONUS: Churn by Tenure Bucket ────────────────────────────
SELECT
    Tenure_Bucket,
    COUNT(*)                              AS Customers,
    SUM(Churn)                            AS Churned,
    ROUND(AVG(Churn) * 100.0, 2)          AS Churn_Rate_Pct,
    ROUND(AVG(CashbackAmount), 2)         AS Avg_Cashback
FROM shopsphere_customers
GROUP BY Tenure_Bucket
ORDER BY
    CASE Tenure_Bucket
        WHEN '0-3 Mo'   THEN 1
        WHEN '3-6 Mo'   THEN 2
        WHEN '6-12 Mo'  THEN 3
        WHEN '12-24 Mo' THEN 4
        WHEN '24+ Mo'   THEN 5
    END;


-- ── BONUS: High-Risk Customer Segments ───────────────────────
SELECT
    Tenure_Bucket,
    CASE
        WHEN Complain = 1 THEN 'Complained'
        ELSE 'No Complaint'
    END                                   AS Complaint_Status,
    COUNT(*)                              AS Customers,
    ROUND(AVG(Churn) * 100.0, 2)          AS Churn_Rate_Pct,
    ROUND(AVG(SatisfactionScore), 2)      AS Avg_Satisfaction
FROM shopsphere_customers
WHERE Tenure_Bucket IN ('0-3 Mo', '3-6 Mo')
GROUP BY Tenure_Bucket, Complain
ORDER BY Churn_Rate_Pct DESC;