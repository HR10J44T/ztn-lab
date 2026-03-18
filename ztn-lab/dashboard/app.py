import os
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Zero Trust Dashboard", layout="wide")
st.title("🔐 Zero Trust Network Simulation Lab")
st.caption("Continuous verification, policy enforcement, and micro-segmentation observability")


def fetch_json(path: str):
    try:
        response = requests.get(f"{API_BASE_URL}{path}", timeout=10)
        response.raise_for_status()
        return response.json(), None
    except Exception as exc:
        return None, str(exc)


metrics, metrics_error = fetch_json("/metrics")
events, events_error = fetch_json("/events")

if metrics_error:
    st.error(f"Could not reach backend: {metrics_error}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Events", metrics["total_events"])
col2.metric("Allowed", metrics["allowed"])
col3.metric("Denied", metrics["denied"])
col4.metric("Avg Risk", metrics["average_risk"])

if events_error:
    st.warning("Metrics are available but events could not be loaded.")
    st.stop()

if not events:
    st.info("No events yet. Use the API to generate access decisions.")
    st.stop()

frame = pd.DataFrame(events)
frame["created_at"] = pd.to_datetime(frame["created_at"])

left, right = st.columns(2)
with left:
    st.subheader("Decision Distribution")
    fig = px.pie(frame, names="decision", title="Allow vs Deny")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Risk by Segment")
    risk_fig = px.bar(
        frame.groupby("resource_segment", as_index=False)["risk_score"].mean(),
        x="resource_segment",
        y="risk_score",
        title="Average Risk Score by Segment",
    )
    st.plotly_chart(risk_fig, use_container_width=True)

st.subheader("Recent Access Events")
st.dataframe(frame.sort_values("created_at", ascending=False), use_container_width=True)

st.subheader("Top Rejection Reasons")
reason_fig = px.bar(
    frame[frame["decision"] == "deny"]["reason"].value_counts().reset_index().rename(columns={"index": "reason", "reason": "count"}),
    x="reason",
    y="count",
    title="Denied Access Reasons",
)
st.plotly_chart(reason_fig, use_container_width=True)
