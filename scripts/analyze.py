"""
Support Ticket / Incident Analysis
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "support_tickets.csv"
OUT = Path(__file__).parent.parent / "outputs"
OUT.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 5)

df = pd.read_csv(DATA, parse_dates=["created_at", "resolved_at"])
df["escalated"] = df["escalated"].astype(bool)

print("=" * 60)
print("SUPPORT TICKET / INCIDENT ANALYSIS")
print("=" * 60)
print(f"\nTotal tickets      : {len(df):,}")
print(f"Escalation rate    : {df['escalated'].mean()*100:.1f}%")
print(f"Median resolve time: {df['resolution_time_hours'].median():.1f} hours")
print(f"Mean resolve time  : {df['resolution_time_hours'].mean():.1f} hours")

print("\n--- Volume by Category ---")
print(df['category'].value_counts())

print("\n--- Median Resolution Time by Category ---")
med_by_cat = df.groupby("category")["resolution_time_hours"].median().sort_values(ascending=False)
print(med_by_cat.round(1))

print("\n--- Escalation Rate by Category ---")
esc_by_cat = df.groupby("category")["escalated"].mean().sort_values(ascending=False)
print((esc_by_cat * 100).round(1))

print("\n--- Resolution Time by Priority ---")
print(df.groupby("priority")["resolution_time_hours"].agg(["median", "mean"]).round(1))

# ---- Charts ----

# 1. Ticket volume by category
fig, ax = plt.subplots(figsize=(10, 5))
order = df["category"].value_counts().index
sns.countplot(data=df, y="category", order=order, ax=ax, color="#4c72b0")
ax.set_xlabel("Number of Tickets")
ax.set_title("Support Ticket Volume by Category")
plt.tight_layout()
plt.savefig(OUT / "volume_by_category.png", dpi=150)
plt.close()

# 2. Median resolution time by category
fig, ax = plt.subplots(figsize=(10, 5))
med_by_cat.plot.barh(ax=ax, color="#c44e52")
ax.set_xlabel("Median Resolution Time (hours)")
ax.set_title("Median Resolution Time by Category")
plt.tight_layout()
plt.savefig(OUT / "resolution_time_by_category.png", dpi=150)
plt.close()

# 3. Escalation rate by category
fig, ax = plt.subplots(figsize=(10, 5))
(esc_by_cat * 100).plot.barh(ax=ax, color="#dd8452")
ax.set_xlabel("Escalation Rate (%)")
ax.set_title("Escalation Rate by Category")
plt.tight_layout()
plt.savefig(OUT / "escalation_by_category.png", dpi=150)
plt.close()

# 4. Resolution time distribution
fig, ax = plt.subplots()
sns.histplot(df["resolution_time_hours"].clip(upper=48), bins=40, ax=ax, color="#55a868")
ax.set_xlabel("Resolution Time (hours)")
ax.set_title("Distribution of Resolution Times (capped at 48h)")
plt.tight_layout()
plt.savefig(OUT / "resolution_time_distribution.png", dpi=150)
plt.close()

# 5. Channel mix
fig, ax = plt.subplots(figsize=(7, 5))
df["channel"].value_counts().plot.pie(autopct="%1.1f%%", ax=ax, startangle=90)
ax.set_ylabel("")
ax.set_title("Ticket Channel Mix")
plt.tight_layout()
plt.savefig(OUT / "channel_mix.png", dpi=150)
plt.close()

insights = f"""
SUPPORT TICKET / INCIDENT ANALYSIS – KEY FINDINGS
=================================================

Dataset: {len(df):,} synthetic support tickets over ~90 days
Overall escalation rate: {df['escalated'].mean()*100:.1f}%
Median resolution time : {df['resolution_time_hours'].median():.1f} hours

1. HIGHEST VOLUME CATEGORIES
{df['category'].value_counts().head(5).to_string()}

2. SLOWEST CATEGORIES (median hours)
{med_by_cat.head(5).round(1).to_string()}

3. HIGHEST ESCALATION CATEGORIES
{(esc_by_cat * 100).head(5).round(1).to_string()}

INSIGHTS FOR OPS / PRODUCT
--------------------------
- Wallet Discrepancy, Stuck Withdrawal and Payment Provider Error tickets
  take longer and escalate more often. These are the same issues the
  Transaction Failure and Wallet Reconciliation projects analyse.
- Improving root-cause visibility on those three categories would reduce
  both resolution time and escalation load.
- Tawk.to is the dominant channel → real-time support quality matters most.

All data is synthetic and modelled on common fintech support patterns.
No real company data was used.
"""
with open(OUT / "insights_summary.txt", "w") as f:
    f.write(insights)

print("\nOutputs saved.")
print(insights)
