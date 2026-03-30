import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Austria ESI Dashboard", layout="wide")

# Get the absolute path to the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BASE_PATH = os.path.join(PROJECT_ROOT, "data", "processed")

@st.cache_data
def load_data():
    master_company_table = pd.read_pickle(os.path.join(BASE_PATH, "master_company_table.pkl"))
    industry_summary = pd.read_pickle(os.path.join(BASE_PATH, "industry_summary.pkl"))
    region_summary = pd.read_pickle(os.path.join(BASE_PATH, "region_summary.pkl"))
    size_summary = pd.read_pickle(os.path.join(BASE_PATH, "size_summary.pkl"))
    kpis = pd.read_pickle(os.path.join(BASE_PATH, "kpis.pkl"))
    return master_company_table, industry_summary, region_summary, size_summary, kpis

master_company_table, industry_summary, region_summary, size_summary, kpis = load_data()

st.title("Austria Employment Growth Dashboard")
st.markdown("Interactive ESI-style dashboard for exploring Austrian company growth by industry and region.")

st.sidebar.header("Filters")

region_options = sorted([x for x in master_company_table["region"].dropna().unique()])
industry_options = sorted([x for x in master_company_table["nace_section"].dropna().unique()])

classification_col = "high_growth_classification"
class_options = sorted([str(x) for x in master_company_table[classification_col].dropna().unique()]) if classification_col in master_company_table.columns else []

size_col = "size_band_2021" if "size_band_2021" in master_company_table.columns else None

selected_regions = st.sidebar.multiselect("Region", region_options, default=region_options)
selected_industries = st.sidebar.multiselect("Industry", industry_options, default=industry_options)
selected_classes = st.sidebar.multiselect("Classification", class_options, default=class_options) if class_options else []

filtered = master_company_table[
    master_company_table["region"].isin(selected_regions) &
    master_company_table["nace_section"].isin(selected_industries)
].copy()

if class_options:
    filtered = filtered[filtered[classification_col].astype(str).isin(selected_classes)]

# Calculate metrics
total_firms = len(filtered)
high_growth_firms = (filtered[classification_col] == 1).sum()
not_high_growth_firms = (filtered[classification_col] == 0).sum()
share_high_growth = high_growth_firms / (high_growth_firms + not_high_growth_firms) if (high_growth_firms + not_high_growth_firms) > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Firms (Classifiable)", f"{int(total_firms):,}")
col2.metric("High-Growth Firms", f"{int(high_growth_firms):,}")
col3.metric("Not High-Growth Firms", f"{int(not_high_growth_firms):,}")
col4.metric("High-Growth Share", f"{share_high_growth:.1%}")

industry_filtered = (
    filtered.groupby("nace_section", dropna=False)
    .agg(
        total_firms=("company_name", "count"),
        high_growth_firms=(classification_col, lambda x: (x == 1).sum())
    )
    .reset_index()
)
industry_filtered["share_high_growth"] = industry_filtered["high_growth_firms"] / industry_filtered["total_firms"]

region_filtered = (
    filtered.groupby("region", dropna=False)
    .agg(
        total_firms=("company_name", "count"),
        high_growth_firms=(classification_col, lambda x: (x == 1).sum())
    )
    .reset_index()
)
region_filtered["share_high_growth"] = region_filtered["high_growth_firms"] / region_filtered["total_firms"]

st.subheader("Overview")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**High-Growth Share by Industry**")
    plot_industry = industry_filtered.dropna(subset=["share_high_growth"]).sort_values(
        "share_high_growth", ascending=False
    )
    if len(plot_industry) > 0:
        st.bar_chart(plot_industry.set_index("nace_section")["share_high_growth"])
    else:
        st.info("No industry data available for the selected filters.")

with chart_col2:
    st.markdown("**High-Growth Share by Region**")
    plot_region = region_filtered.dropna(subset=["share_high_growth"]).sort_values(
        "share_high_growth", ascending=False
    )
    if len(plot_region) > 0:
        st.bar_chart(plot_region.set_index("region")["share_high_growth"])
    else:
        st.info("No region data available for the selected filters.")

if size_col:
    st.subheader("Size Band Analysis")
    size_filtered = (
        filtered.groupby(size_col, dropna=False)
        .agg(
            total_firms=("company_name", "count"),
            high_growth_firms=(classification_col, lambda x: (x == 1).sum())
        )
        .reset_index()
    )
    size_filtered["share_high_growth"] = size_filtered["high_growth_firms"] / size_filtered["total_firms"]

    plot_size = size_filtered.dropna(subset=["share_high_growth"]).sort_values(
        "share_high_growth", ascending=False
    )

    if len(plot_size) > 0:
        st.bar_chart(plot_size.set_index(size_col)["share_high_growth"])
    else:
        st.info("No size-band data available for the selected filters.")

st.subheader("Company-Level Data")

display_cols = [
    col for col in [
        "company_name",
        "region",
        "nace_section",
        "founded_year",
        "employees_2021",
        "employees_2024",
        "growth_2022",
        "growth_2023",
        "growth_2024",
        "aagr_2024",
        "high_growth_classification"
    ] if col in filtered.columns
]

if display_cols:
    st.dataframe(filtered[display_cols], use_container_width=True)
else:
    st.error("No columns available to display")

csv = filtered[display_cols].to_csv(index=False).encode("utf-8") if display_cols else b""
st.download_button(
    label="Download filtered company data as CSV",
    data=csv,
    file_name="filtered_austria_dashboard_data.csv",
    mime="text/csv",
    disabled=(len(csv) == 0)
)
