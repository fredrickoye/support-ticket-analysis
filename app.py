"""
Support Ticket / Incident Analysis Dashboard
Streamlit interactive dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Support Ticket Dashboard",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    path = Path(__file__).parent / "data" / "support_tickets.csv"
    df = pd.read_csv(path, parse_dates=["created_at", "resolved_at"])
    df["escalated"] = df["escalated"].astype(bool)
    return df

df = load_data()

# Sidebar filters
st.sidebar.title("Filters")
categories = st.sidebar.multiselect(
    "Category",
    options=sorted(df["category"].unique()),
    default=sorted(df["category"].unique())
)
priorities = st.sidebar.multiselect(
    "Priority",
    options=["Critical", "High", "Medium", "Low"],
    default=["Critical", "High", "Medium", "Low"]
)

filtered = df[
    (df["category"].isin(categories)) &
    (df["priority"].isin(priorities))
]

# Header
st.title("🎫 Support Ticket / Incident Dashboard")
st.markdown("""
**Problem:** Support teams are flooded with tickets about failed deposits, stuck withdrawals and wallet issues.  
Without clear visibility into which categories take longest and escalate most, the team stays reactive. This dashboard surfaces the bottlenecks.

*Synthetic data only. Figures illustrate methodology — they do **not** represent any real company’s support metrics.*
""")

# KPIs
total = len(filtered)
esc_rate = filtered["escalated"].mean() * 100 if total else 0
med_res = filtered["resolution_time_hours"].median() if total else 0
mean_res = filtered["resolution_time_hours"].mean() if total else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Tickets", f"{total:,}")
c2.metric("Escalation Rate", f"{esc_rate:.1f}%")
c3.metric("Median Resolution", f"{med_res:.1f} h")
c4.metric("Mean Resolution", f"{mean_res:.1f} h")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Ticket Volume by Category")
    vol = filtered["category"].value_counts().reset_index()
    vol.columns = ["category", "count"]
    fig = px.bar(
        vol, y="category", x="count", orientation="h",
        color="count", color_continuous_scale="Blues",
        labels={"category": "Category", "count": "Tickets"}
    )
    fig.update_layout(showlegend=False, height=400, margin=dict(t=30),
                      yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Median Resolution Time by Category")
    med = filtered.groupby("category")["resolution_time_hours"].median().reset_index()
    med = med.sort_values("resolution_time_hours", ascending=True)
    fig = px.bar(
        med, y="category", x="resolution_time_hours", orientation="h",
        color="resolution_time_hours", color_continuous_scale="Reds",
        labels={"category": "Category", "resolution_time_hours": "Median Hours"}
    )
    fig.update_layout(showlegend=False, height=400, margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)

left2, right2 = st.columns(2)

with left2:
    st.subheader("Escalation Rate by Category")
    esc = filtered.groupby("category")["escalated"].mean().reset_index()
    esc["rate_pct"] = esc["escalated"] * 100
    esc = esc.sort_values("rate_pct", ascending=True)
    fig = px.bar(
        esc, y="category", x="rate_pct", orientation="h",
        color="rate_pct", color_continuous_scale="Oranges",
        labels={"category": "Category", "rate_pct": "Escalation Rate (%)"}
    )
    fig.update_layout(showlegend=False, height=400, margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)

with right2:
    st.subheader("Channel Mix")
    chan = filtered["channel"].value_counts().reset_index()
    chan.columns = ["channel", "count"]
    fig = px.pie(chan, names="channel", values="count", hole=0.4)
    fig.update_layout(height=400, margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Resolution Time Distribution")
fig = px.histogram(
    filtered, x="resolution_time_hours", nbins=40,
    labels={"resolution_time_hours": "Resolution Time (hours)"},
    color_discrete_sequence=["#55a868"]
)
fig.update_layout(height=360, margin=dict(t=20))
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Key Insights")
st.markdown("""
- **Stuck Withdrawal**, **Wallet Discrepancy** and **Payment Provider Error** tickets take the longest *and* escalate the most.
- These are the same operational problems analysed in the Transaction Failure and Wallet Reconciliation projects.
- Improving root-cause visibility on these three categories would reduce both resolution time and escalation load.
- Live chat (Tawk.to style) is the dominant channel → real-time support quality matters most.
""")

st.caption("Built by [Omololu Oyewumi](https://www.linkedin.com/in/omololu-oyewumi-4aa682331) · Synthetic data only")
