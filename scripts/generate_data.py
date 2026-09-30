"""
Generate synthetic support ticket / incident data
modelled on common fintech support patterns (Jira + Tawk.to style).
"""
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
from pathlib import Path

fake = Faker()
np.random.seed(77)
Faker.seed(77)

n = 4500
categories = [
    'Failed Deposit', 'Stuck Withdrawal', 'Wallet Discrepancy',
    'Account Issue', 'Payment Provider Error', 'Login / Access',
    'General Enquiry', 'Refund Request'
]
channels = ['Tawk.to', 'Email', 'In-app', 'Phone']
priorities = ['Low', 'Medium', 'High', 'Critical']

start = datetime.now() - timedelta(days=90)
created = [start + timedelta(seconds=np.random.randint(0, 90*24*3600)) for _ in range(n)]

# Resolution times (hours) – skewed, some long
base_hours = np.random.exponential(scale=4, size=n)
# Some categories take longer
cat = np.random.choice(categories, n, p=[0.22, 0.18, 0.15, 0.12, 0.10, 0.08, 0.10, 0.05])
priority = np.random.choice(priorities, n, p=[0.25, 0.40, 0.25, 0.10])

# Adjust resolution time by category & priority
mult = np.ones(n)
for i, c in enumerate(cat):
    if c in ['Wallet Discrepancy', 'Stuck Withdrawal', 'Payment Provider Error']:
        mult[i] *= 1.6
    if c == 'General Enquiry':
        mult[i] *= 0.6
for i, p in enumerate(priority):
    if p == 'Critical':
        mult[i] *= 0.7   # faster response
    elif p == 'Low':
        mult[i] *= 1.4

resolution_hours = np.clip(base_hours * mult, 0.1, 72)
resolved = [created[i] + timedelta(hours=float(resolution_hours[i])) for i in range(n)]

# Escalation more likely for certain categories and longer tickets
escalated = []
for i in range(n):
    prob = 0.08
    if cat[i] in ['Wallet Discrepancy', 'Stuck Withdrawal', 'Payment Provider Error']:
        prob = 0.22
    if resolution_hours[i] > 12:
        prob += 0.15
    if priority[i] in ['High', 'Critical']:
        prob += 0.10
    escalated.append(np.random.rand() < min(prob, 0.55))

df = pd.DataFrame({
    'ticket_id': [f"TKT-{10000+i}" for i in range(n)],
    'created_at': created,
    'resolved_at': resolved,
    'category': cat,
    'channel': np.random.choice(channels, n, p=[0.55, 0.20, 0.15, 0.10]),
    'priority': priority,
    'escalated': escalated,
    'resolution_time_hours': np.round(resolution_hours, 2),
})

df = df.sort_values('created_at').reset_index(drop=True)

out = Path(__file__).parent.parent / "data" / "support_tickets.csv"
df.to_csv(out, index=False)
print(f"Generated {len(df)} rows → {out}")
print(df['category'].value_counts())
print(f"Escalation rate: {df['escalated'].mean()*100:.1f}%")
print(f"Median resolution time: {df['resolution_time_hours'].median():.1f} hours")
