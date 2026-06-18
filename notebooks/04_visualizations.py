# ==============================================================
# FILE: 04_visualizations.py
# PURPOSE: Create and save all charts — FIXED VERSION
# This version works even if chart windows do not pop up
# Charts are saved as PNG files in the dashboard/ folder
# ==============================================================

# ── BACKEND FIX — Must be the very first lines ───────────────
import matplotlib
matplotlib.use('Agg')  # Agg saves to file without needing a display
# If you WANT popup windows, change 'Agg' to 'TkAgg'

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
import warnings
import os

warnings.filterwarnings("ignore")

# ── Make sure dashboard folder exists ────────────────────────
os.makedirs("dashboard", exist_ok=True)

# ── Load clean data ───────────────────────────────────────────
df = pd.read_csv("data/cleaned/shopsphere_clean.csv")
df["Churn_Label"] = df["Churn"].map({0: "Retained", 1: "Churned"})

# ── Color palette ─────────────────────────────────────────────
BLUE   = "#2563EB"
RED    = "#DC2626"
AMBER  = "#F59E0B"
GREEN  = "#16A34A"
GRAY   = "#6B7280"
BG     = "#F8FAFC"
WHITE  = "#FFFFFF"

# ── Global style settings ─────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor"  : BG,
    "axes.facecolor"    : WHITE,
    "axes.spines.top"   : False,
    "axes.spines.right" : False,
    "axes.grid"         : True,
    "grid.alpha"        : 0.3,
    "grid.color"        : "#CBD5E1",
    "font.size"         : 11,
    "axes.labelcolor"   : "#1E293B",
    "xtick.color"       : "#475569",
    "ytick.color"       : "#475569",
})

print("=" * 55)
print("CREATING ALL CHARTS")
print("Charts will be saved to: dashboard/ folder")
print("=" * 55)


# ==============================================================
# CHART 1 — KPI Summary Cards
# ==============================================================

print("\nCreating Chart 1: KPI Cards...")

fig, axes = plt.subplots(1, 3, figsize=(15, 3.5))
fig.patch.set_facecolor(BG)

# Calculate KPI values
total_customers  = len(df)
churn_rate       = df["Churn"].mean()
total_churned    = df["Churn"].sum()
avg_satisfaction = df["SatisfactionScore"].mean()

kpis = [
    {
        "title" : "Total Customers",
        "value" : f"{total_customers:,}",
        "sub"   : "Active in database",
        "color" : BLUE,
    },
    {
        "title" : "Overall Churn Rate",
        "value" : f"{churn_rate:.1%}",
        "sub"   : f"{total_churned:,} customers lost",
        "color" : RED,
    },
    {
        "title" : "Avg Satisfaction Score",
        "value" : f"{avg_satisfaction:.2f} / 5",
        "sub"   : "Customer satisfaction",
        "color" : AMBER,
    },
]

for ax, kpi in zip(axes, kpis):
    ax.set_facecolor(kpi["color"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(0.5, 0.60, kpi["value"],
            transform=ax.transAxes,
            ha="center", va="center",
            fontsize=34, fontweight="bold", color=WHITE)
    ax.text(0.5, 0.28, kpi["title"],
            transform=ax.transAxes,
            ha="center", va="center",
            fontsize=12, color=WHITE, alpha=0.95)
    ax.text(0.5, 0.10, kpi["sub"],
            transform=ax.transAxes,
            ha="center", va="center",
            fontsize=9, color=WHITE, alpha=0.75)

fig.suptitle("ShopSphere — Executive KPI Summary",
             fontsize=15, fontweight="bold",
             color="#0F172A", y=1.05)
plt.tight_layout(pad=0.5)
plt.savefig("dashboard/chart1_kpi_cards.png",
            dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  SAVED: dashboard/chart1_kpi_cards.png")


# ==============================================================
# CHART 2 — Churn Rate by Product Category
# ==============================================================

print("\nCreating Chart 2: Churn by Category...")

cat_data = (
    df.groupby("PreferredOrderCat")["Churn"]
    .agg(["mean", "count"])
    .rename(columns={"mean": "Churn_Rate", "count": "Customers"})
    .sort_values("Churn_Rate", ascending=True)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(BG)

# Color bars based on how bad the churn is
bar_colors = [
    RED   if r > 0.40 else
    AMBER if r > 0.30 else
    GREEN
    for r in cat_data["Churn_Rate"]
]

bars = ax.barh(
    cat_data["PreferredOrderCat"],
    cat_data["Churn_Rate"] * 100,
    color=bar_colors,
    edgecolor=WHITE,
    height=0.55
)

# Add labels on each bar
for bar, rate, n in zip(bars, cat_data["Churn_Rate"], cat_data["Customers"]):
    ax.text(
        bar.get_width() + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{rate:.1%}   (n={n:,})",
        va="center", ha="left", fontsize=10, color="#374151"
    )

# Average churn line
company_avg = df["Churn"].mean() * 100
ax.axvline(company_avg, color=GRAY, linestyle="--",
           linewidth=1.5, label=f"Company avg: {company_avg:.1f}%")
ax.legend(fontsize=10)

ax.set_xlabel("Churn Rate (%)", labelpad=10)
ax.set_title("Churn Rate by Preferred Order Category",
             fontsize=14, fontweight="bold", pad=15)
ax.xaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x:.0f}%")
)
ax.set_xlim(0, 75)

plt.tight_layout()
plt.savefig("dashboard/chart2_churn_by_category.png",
            dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  SAVED: dashboard/chart2_churn_by_category.png")


# ==============================================================
# CHART 3 — Complaints vs Churn
# ==============================================================

print("\nCreating Chart 3: Complaints vs Churn...")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.patch.set_facecolor(BG)

# ── Left chart: Customer counts ───────────────────────────────
# Count how many churned and retained in each complaint group
no_complaint_retained  = len(df[(df["Complain"]==0) & (df["Churn"]==0)])
no_complaint_churned   = len(df[(df["Complain"]==0) & (df["Churn"]==1)])
had_complaint_retained = len(df[(df["Complain"]==1) & (df["Churn"]==0)])
had_complaint_churned  = len(df[(df["Complain"]==1) & (df["Churn"]==1)])

categories  = ["No Complaint", "Had Complaint"]
retained_counts = [no_complaint_retained, had_complaint_retained]
churned_counts  = [no_complaint_churned,  had_complaint_churned]

x = np.arange(len(categories))
width = 0.35

axes[0].bar(x - width/2, retained_counts, width,
            label="Retained", color=BLUE, edgecolor=WHITE)
axes[0].bar(x + width/2, churned_counts, width,
            label="Churned", color=RED, edgecolor=WHITE)

axes[0].set_xticks(x)
axes[0].set_xticklabels(categories)
axes[0].set_title("Customer Counts: Complaint vs Churn",
                  fontweight="bold")
axes[0].set_ylabel("Number of Customers")
axes[0].legend()

# ── Right chart: Churn rate comparison ───────────────────────
rate_no_complaint  = df[df["Complain"]==0]["Churn"].mean() * 100
rate_had_complaint = df[df["Complain"]==1]["Churn"].mean() * 100

bar_labels  = ["No Complaint", "Had Complaint"]
bar_heights = [rate_no_complaint, rate_had_complaint]
bar_colors2 = [GREEN, RED]

bars2 = axes[1].bar(
    bar_labels, bar_heights,
    color=bar_colors2,
    edgecolor=WHITE,
    width=0.5
)

# Add percentage labels on top
for bar in bars2:
    axes[1].annotate(
        f"{bar.get_height():.1f}%",
        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
        ha="center", va="bottom",
        fontsize=15, fontweight="bold"
    )

axes[1].set_title("Churn Rate: Complaint vs No Complaint",
                  fontweight="bold")
axes[1].set_ylabel("Churn Rate (%)")
axes[1].set_ylim(0, 100)
axes[1].yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x:.0f}%")
)

fig.suptitle("Impact of Customer Complaints on Churn",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("dashboard/chart3_complaints_vs_churn.png",
            dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  SAVED: dashboard/chart3_complaints_vs_churn.png")


# ==============================================================
# CHART 4 — Cashback vs Churn (FIXED for Python 3.13)
# ==============================================================

print("\nCreating Chart 4: Cashback vs Churn...")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.patch.set_facecolor(BG)

# ── Left: Box plot ─────────────────────────────────────────────
churned_cash  = df[df["Churn"] == 1]["CashbackAmount"]
retained_cash = df[df["Churn"] == 0]["CashbackAmount"]

bp = axes[0].boxplot(
    [retained_cash, churned_cash],
    tick_labels=["Retained", "Churned"],   # FIXED: was 'labels' in old matplotlib
    patch_artist=True,
    medianprops=dict(color=RED, linewidth=2.5),
    whiskerprops=dict(linewidth=1.5),
    capprops=dict(linewidth=1.5),
    flierprops=dict(marker="o", markersize=3, alpha=0.4)
)

# Color the boxes
bp["boxes"][0].set_facecolor(BLUE)
bp["boxes"][0].set_alpha(0.6)
bp["boxes"][1].set_facecolor(RED)
bp["boxes"][1].set_alpha(0.6)

axes[0].set_title("Cashback Distribution: Churned vs Retained",
                  fontweight="bold")
axes[0].set_ylabel("Cashback Amount ($)")

# Add median value labels on the box plot
for i, (label, data) in enumerate(
    zip(["Retained", "Churned"], [retained_cash, churned_cash])
):
    median_val = data.median()
    axes[0].text(
        i + 1,
        median_val + 5,
        f"Median:\n${median_val:.0f}",
        ha="center", va="bottom",
        fontsize=9, color="#1E293B", fontweight="bold"
    )

# ── Right: Churn rate by cashback tier ────────────────────────
cashback_bins = pd.cut(
    df["CashbackAmount"],
    bins=[0, 100, 150, 200, 250, 400],
    labels=["$0-100", "$100-150", "$150-200", "$200-250", "$250-400"]
)

cashback_churn = (
    df.groupby(cashback_bins, observed=True)["Churn"]
    .mean() * 100
)

bar_colors_cb = [
    RED   if r > 40 else
    AMBER if r > 30 else
    GREEN
    for r in cashback_churn.values
]

bars3 = axes[1].bar(
    range(len(cashback_churn)),
    cashback_churn.values,
    color=bar_colors_cb,
    edgecolor=WHITE,
    width=0.6
)

axes[1].set_xticks(range(len(cashback_churn)))
axes[1].set_xticklabels(cashback_churn.index, rotation=25, ha="right")

for bar in bars3:
    axes[1].annotate(
        f"{bar.get_height():.1f}%",
        xy=(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5),
        ha="center", va="bottom", fontsize=10
    )

axes[1].set_title("Churn Rate by Cashback Tier", fontweight="bold")
axes[1].set_xlabel("Cashback Amount")
axes[1].set_ylabel("Churn Rate (%)")
axes[1].yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x:.0f}%")
)

fig.suptitle("Cashback Incentives and Customer Retention",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("dashboard/chart4_cashback_vs_churn.png",
            dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  SAVED: dashboard/chart4_cashback_vs_churn.png")

# ==============================================================
# CHART 5 — Churn Rate by Tenure
# ==============================================================

print("\nCreating Chart 5: Churn by Tenure...")

tenure_churn = (
    df.groupby("Tenure_Bucket", observed=True)["Churn"]
    .agg(["mean", "count"])
    .reset_index()
)

fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(BG)

bar_colors_t = [
    RED   if r > 0.50 else
    AMBER if r > 0.30 else
    GREEN
    for r in tenure_churn["mean"]
]

bars4 = ax.bar(
    tenure_churn["Tenure_Bucket"],
    tenure_churn["mean"] * 100,
    color=bar_colors_t,
    edgecolor=WHITE,
    width=0.55
)

for bar, rate, n in zip(bars4, tenure_churn["mean"], tenure_churn["count"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.8,
        f"{rate:.1%}\n(n={n:,})",
        ha="center", va="bottom",
        fontsize=10, fontweight="bold"
    )

avg_churn_line = df["Churn"].mean() * 100
ax.axhline(avg_churn_line, color=GRAY, linestyle="--",
           linewidth=1.5, label=f"Company avg: {avg_churn_line:.1f}%")
ax.legend(fontsize=10)

ax.set_title(
    "Churn Rate by Tenure — New Customers Are at Highest Risk",
    fontsize=13, fontweight="bold", pad=15
)
ax.set_xlabel("Customer Tenure", labelpad=10)
ax.set_ylabel("Churn Rate (%)")
ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x:.0f}%")
)
ax.set_ylim(0, 90)

plt.tight_layout()
plt.savefig("dashboard/chart5_churn_by_tenure.png",
            dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  SAVED: dashboard/chart5_churn_by_tenure.png")


# ==============================================================
# CHART 6 — Churn Rate by Distance
# ==============================================================

print("\nCreating Chart 6: Churn by Distance...")

distance_churn = (
    df.groupby("Distance_Category", observed=True)["Churn"]
    .agg(["mean", "count"])
    .reset_index()
)

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(BG)

bar_colors_d = [
    RED   if r > 0.40 else
    AMBER if r > 0.30 else
    GREEN
    for r in distance_churn["mean"]
]

bars5 = ax.bar(
    distance_churn["Distance_Category"],
    distance_churn["mean"] * 100,
    color=bar_colors_d,
    edgecolor=WHITE,
    width=0.55
)

for bar, rate, n in zip(bars5, distance_churn["mean"], distance_churn["count"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        f"{rate:.1%}\n(n={n:,})",
        ha="center", va="bottom",
        fontsize=10, fontweight="bold"
    )

ax.set_title(
    "Churn Rate by Distance — Farther Customers Leave More Often",
    fontsize=13, fontweight="bold", pad=15
)
ax.set_xlabel("Distance from Warehouse", labelpad=10)
ax.set_ylabel("Churn Rate (%)")
ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x:.0f}%")
)
ax.set_ylim(0, 75)

plt.tight_layout()
plt.savefig("dashboard/chart6_distance_vs_churn.png",
            dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  SAVED: dashboard/chart6_distance_vs_churn.png")


# ==============================================================
# DONE — Print summary
# ==============================================================

print("\n" + "=" * 55)
print("ALL 6 CHARTS CREATED SUCCESSFULLY")
print("=" * 55)
print("\nYour charts are saved here:")

chart_files = [
    "chart1_kpi_cards.png",
    "chart2_churn_by_category.png",
    "chart3_complaints_vs_churn.png",
    "chart4_cashback_vs_churn.png",
    "chart5_churn_by_tenure.png",
    "chart6_distance_vs_churn.png",
]

for i, filename in enumerate(chart_files, 1):
    filepath = f"dashboard/{filename}"
    exists = os.path.exists(filepath)
    status = "EXISTS" if exists else "MISSING"
    print(f"  {i}. {filepath}  [{status}]")

print("\nHow to view the charts:")
print("  → Open VS Code")
print("  → Click on the dashboard/ folder in the sidebar")
print("  → Click any .png file to preview it")
print("=" * 55)