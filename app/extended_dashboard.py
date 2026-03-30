import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Austria Extended ESI Dashboard", layout="wide")

# Get the absolute path to the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BASE_PATH = os.path.join(PROJECT_ROOT, "data", "processed")

@st.cache_data
def load_extended_data():
    """Load the extended dataset with all classifications"""
    df = pd.read_pickle(os.path.join(BASE_PATH, "austria_extended_classifications.pkl"))
    return df

# Load data
try:
    df = load_extended_data()
    st.success(f"✓ Loaded extended dataset: {df.shape[0]:,} firms, {df.shape[1]} variables")
except FileNotFoundError:
    st.error(f"Extended dataset not found at {BASE_PATH}. Please run notebook 05_extended_classifications.ipynb first.")
    st.stop()

st.title("🚀 Austria Extended ESI Dashboard")
st.markdown("Comprehensive analysis of firm growth classifications for 2020-2024")

# ============================================================================
# SECTION 1: OVERVIEW BY YEAR
# ============================================================================
st.header("1️⃣ Overview by Classification Year")

year_col1, year_col2 = st.columns(2)

with year_col1:
    selected_year = st.selectbox("Select Classification Year", options=[2020, 2021, 2022, 2023, 2024], key="year_select")

with year_col2:
    st.write("")  # Spacing

prefix = f"{selected_year}_"
available_categories = [
    "scaler", "hgf", "consistent_hgf", "consistent_hypergrower",
    "gazelle", "mature_hgf", "scaleup", "superstar"
]

# Calculate statistics for selected year
stats = {}
for cat in available_categories:
    col_name = f"{prefix}{cat}"
    if col_name in df.columns:
        count_1 = (df[col_name] == 1).sum()
        count_0 = (df[col_name] == 0).sum()
        count_na = (df[col_name] == 'n.a.').sum()
        total_classifiable = count_1 + count_0
        pct_1 = (count_1 / total_classifiable * 100) if total_classifiable > 0 else 0
        stats[cat] = {
            "Count": count_1,
            "Percentage": pct_1,
            "Total Classifiable": total_classifiable,
            "Not Classified": count_na
        }

# Display metrics for selected year
st.subheader(f"Firm Classifications - Year {selected_year}")

cols = st.columns(4)
cat_names = ["Scalers", "HGFs", "Consistent HGFs", "Hypergrowers"]
cat_keys = ["scaler", "hgf", "consistent_hgf", "consistent_hypergrower"]

for i, (col, name, key) in enumerate(zip(cols, cat_names, cat_keys)):
    if key in stats:
        with col:
            st.metric(
                name,
                f"{stats[key]['Count']:,}",
                f"{stats[key]['Percentage']:.1f}% of classifiable"
            )

# Second row of metrics
cols2 = st.columns(4)
cat_names2 = ["Gazelles", "Mature HGFs", "Scaleups", "Superstars"]
cat_keys2 = ["gazelle", "mature_hgf", "scaleup", "superstar"]

for i, (col, name, key) in enumerate(zip(cols2, cat_names2, cat_keys2)):
    if key in stats:
        with col:
            st.metric(
                name,
                f"{stats[key]['Count']:,}",
                f"{stats[key]['Percentage']:.1f}% of HGFs/Hypergrowers"
            )

# ============================================================================
# SECTION 2: MULTI-YEAR COMPARISON
# ============================================================================
st.header("2️⃣ Multi-Year Trend Analysis")

# Create a comparison table across years
comparison_data = []
for year in [2020, 2021, 2022, 2023, 2024]:
    prefix = f"{year}_"
    row = {"Year": year}
    
    for cat in available_categories:
        col_name = f"{prefix}{cat}"
        if col_name in df.columns:
            count = (df[col_name] == 1).sum()
            row[cat.replace("_", " ").title()] = count
    
    comparison_data.append(row)

comparison_df = pd.DataFrame(comparison_data)
st.subheader("Classification Counts Across Years")
st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# Chart: Trend lines
st.subheader("Trend: Number of Firms by Category")

chart_data = pd.DataFrame()
for cat in ["scaler", "hgf", "consistent_hgf", "consistent_hypergrower"]:
    cat_name = cat.replace("_", " ").title()
    values = []
    for year in [2020, 2021, 2022, 2023, 2024]:
        col_name = f"{year}_{cat}"
        count = (df[col_name] == 1).sum() if col_name in df.columns else 0
        values.append(count)
    chart_data[cat_name] = values

chart_data["Year"] = [2020, 2021, 2022, 2023, 2024]
st.line_chart(chart_data.set_index("Year"))

# ============================================================================
# SECTION 3: COMPANY-LEVEL DATA EXPLORER
# ============================================================================
st.header("3️⃣ Company-Level Data Explorer")

st.subheader("Filter and Explore Individual Firms")

# Filters
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_year_company = st.selectbox("Classification Year (for company table)", [2020, 2021, 2022, 2023, 2024], key="company_year")

with filter_col2:
    category_filter = st.multiselect(
        "Select Firm Categories",
        options=["Scalers", "HGFs", "Consistent HGFs", "Hypergrowers", "Gazelles", "Mature HGFs", "Scaleups", "Superstars"],
        default=["HGFs", "Consistent HGFs"]
    )

# Map display names to column names
category_map = {
    "Scalers": "scaler",
    "HGFs": "hgf",
    "Consistent HGFs": "consistent_hgf",
    "Hypergrowers": "consistent_hypergrower",
    "Gazelles": "gazelle",
    "Mature HGFs": "mature_hgf",
    "Scaleups": "scaleup",
    "Superstars": "superstar"
}

# Filter companies
prefix = f"{selected_year_company}_"
filtered_companies = df.copy()

if category_filter:
    for display_name in category_filter:
        col_key = category_map[display_name]
        col_name = f"{prefix}{col_key}"
        filtered_companies = filtered_companies[filtered_companies[col_name] == 1]

# Select columns to display
display_columns = [
    "company_name", "region", "nace_section", "founded_year",
    f"emp_{selected_year_company - 3}_num", f"emp_{selected_year_company}_num",
    f"growth_{selected_year_company - 2}", f"growth_{selected_year_company - 1}", f"growth_{selected_year_company}",
    f"aagr_{selected_year_company}"
]

display_columns = [col for col in display_columns if col in filtered_companies.columns]

st.write(f"Found {len(filtered_companies)} firms matching criteria")
st.dataframe(
    filtered_companies[display_columns],
    use_container_width=True,
    height=400
)

# Download button
csv = filtered_companies[display_columns].to_csv(index=False).encode("utf-8")
st.download_button(
    label=f"Download {len(filtered_companies)} firms as CSV",
    data=csv,
    file_name=f"austria_firms_{selected_year_company}.csv",
    mime="text/csv"
)

# ============================================================================
# SECTION 4: EXPLANATIONS
# ============================================================================
st.header("4️⃣ Classification Definitions")

with st.expander("📖 View Classification Definitions"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Growth-Based Classifications
        
        **Scalers**
        - Average Annualised Growth Rate > 10% over 3-year period
        - Minimum 10 employees at start of period
        
        **High-Growth Firms (HGFs)**
        - Average Annualised Growth Rate > 20% over 3-year period
        - Minimum 10 employees at start of period
        
        **Consistent HGFs**
        - Meet HGF criteria (AAGR > 20%)
        - Year-over-year growth > 20% in at least 2 of 3 years
        
        **Consistent Hypergrowers**
        - Meet HGF criteria (AAGR > 20%)
        - Year-over-year growth > 40% in at least 2 of 3 years
        """)
    
    with col2:
        st.markdown("""
        ### Age-Based Classifications
        
        **Gazelles**
        - Consistent HGFs
        - Company age ≤ 10 years at start of period
        
        **Mature HGFs**
        - Consistent HGFs
        - Company age > 10 years at start of period
        
        **Scaleups**
        - Consistent Hypergrowers
        - Company age ≤ 10 years at start of period
        
        **Superstars**
        - Consistent Hypergrowers
        - Company age > 10 years at start of period
        """)

with st.expander("📊 Calculate Metrics"):
    st.markdown("""
    ### Growth Rates Calculation
    - **Year-over-Year Growth**: (emp_current - emp_previous) / emp_previous × 100
    - **AAGR (3-year)**: (emp_end / emp_start)^(1/3) - 1) × 100
    
    ### Data Handling
    - **Rule 1**: If input employee value is unavailable, output is "n.a."
    - **Rule 4**: Size threshold of 10 employees at beginning of period
    - **Missing Data**: Preserved as "n.a." strings throughout
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 12px; color: #666;'>
<p>Austria Employment Growth Dashboard | Extended Classifications Analysis</p>
<p>Data Source: Bureau van Dijk | Classification Years: 2020-2024</p>
</div>
""", unsafe_allow_html=True)
