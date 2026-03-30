
import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Austria Combined ESI Dashboard", layout="wide")

# Get the absolute path to the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BASE_PATH = os.path.join(PROJECT_ROOT, "data", "processed")

@st.cache_data
def load_all_data():
    """Load both extended and original datasets"""
    df_extended = pd.read_pickle(os.path.join(BASE_PATH, "austria_extended_classifications.pkl"))
    master_company_table = pd.read_pickle(os.path.join(BASE_PATH, "master_company_table.pkl"))
    return df_extended, master_company_table

# Load data
try:
    df, master_company_table = load_all_data()
    st.success(f"✓ Loaded datasets: {df.shape[0]:,} firms, {df.shape[1]} variables")
except FileNotFoundError as e:
    st.error(f"Dataset not found. Please ensure all pickle files exist in {BASE_PATH}")
    st.stop()

st.title("🚀 Austria Combined ESI Dashboard")
st.markdown("Comprehensive analysis of firm growth classifications for 2020-2024 with industry and regional insights")

# ============================================================================
# NAVIGATION
# ============================================================================
st.sidebar.header("📊 Navigation")
page = st.sidebar.radio("Select Section", [
    "Overview & Funnel",
    "Multi-Year Trends",
    "Industry & Region Analysis",
    "Company Explorer",
    "Definitions & Help"
])

# ============================================================================
# PAGE 1: OVERVIEW & FUNNEL
# ============================================================================
if page == "Overview & Funnel":
    st.header("1️⃣ Overview by Year with Funnel Visualization")
    
    year_col1, year_col2 = st.columns(2)
    
    with year_col1:
        selected_year = st.selectbox("Select Classification Year", options=[2020, 2021, 2022, 2023, 2024], key="year_select")
    
    with year_col2:
        st.write("")  # Spacing
    
    # Calculate statistics for selected year
    prefix = f"{selected_year}_"
    available_categories = [
        "scaler", "hgf", "consistent_hgf", "consistent_hypergrower",
        "gazelle", "mature_hgf", "scaleup", "superstar"
    ]
    
    stats = {}
    for cat in available_categories:
        col_name = f"{prefix}{cat}"
        if col_name in df.columns:
            count_1 = (df[col_name] == 1).sum()
            count_0 = (df[col_name] == 0).sum()
            count_na = (df[col_name] == 'n.a.').sum()
            total_classifiable = count_1 + count_0
            pct_1 = (count_1 / total_classifiable * 100) if total_classifiable > 0 else 0
            pct_of_scalers = (count_1 / (df[f"{prefix}scaler"] == 1).sum() * 100) if (df[f"{prefix}scaler"] == 1).sum() > 0 else 0
            stats[cat] = {
                "Count": count_1,
                "Percentage": pct_1,
                "Pct of Scalers": pct_of_scalers,
                "Total Classifiable": total_classifiable,
                "Not Classified": count_na
            }
    
    # Display metrics
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
    
    cols2 = st.columns(4)
    cat_names2 = ["Gazelles", "Mature HGFs", "Scaleups", "Superstars"]
    cat_keys2 = ["gazelle", "mature_hgf", "scaleup", "superstar"]
    
    for i, (col, name, key) in enumerate(zip(cols2, cat_names2, cat_keys2)):
        if key in stats:
            with col:
                st.metric(
                    name,
                    f"{stats[key]['Count']:,}",
                    f"{stats[key]['Percentage']:.1f}% of consistent HGFs"
                )
    
    # Create funnel visualization
    st.subheader(f"Funnel: Firm Classification Hierarchy - {selected_year}")
    
    # Prepare data for funnel
    all_firms = len(df) - (df[f"{prefix}scaler"] == 'n.a.').sum()
    scaler_count = stats["scaler"]["Count"]
    hgf_count = stats["hgf"]["Count"]
    consistent_hgf_count = stats["consistent_hgf"]["Count"]
    gazelle_count = stats["gazelle"]["Count"]
    mature_hgf_count = stats["mature_hgf"]["Count"]
    hypergrower_count = stats["consistent_hypergrower"]["Count"]
    scaleup_count = stats["scaleup"]["Count"]
    superstar_count = stats["superstar"]["Count"]
    
    # Create funnel stages
    funnel_names = [
        f"<b>Scalers</b><br>10%+ Growth",
        f"<b>HGFs</b><br>20%+ Growth",
        f"<b>Consistent\nGrowth</b><br>20%+",
        f"<b>Gazelles</b><br>(≤10 yrs old)",
        f"<b>Mature HGFs</b><br>(>10 yrs old)",
        f"<b>Consistent\nHypergrowers</b><br>40%+",
        f"<b>Scaleups</b><br>(≤10 yrs old)",
        f"<b>Superstars</b><br>(>10 yrs old)"
    ]
    
    funnel_values = [
        scaler_count,
        hgf_count,
        consistent_hgf_count,
        gazelle_count,
        mature_hgf_count,
        hypergrower_count,
        scaleup_count,
        superstar_count
    ]
    
    # Calculate percentages
    percentages = [(v / all_firms * 100) if all_firms > 0 else 0 for v in funnel_values]
    
    # Create colors for different categories
    colors = [
        "#7fa89f",  # Scaler
        "#6b9e99",  # HGF
        "#5d9493",  # Consistent HGF
        "#b3ccc7",  # Gazelle (light)
        "#9bbfb8",  # Mature HGF (medium)
        "#4a8a89",  # Hypergrower
        "#8fb3ac",  # Scaleup (light)
        "#7aa399"   # Superstar (medium)
    ]
    
    fig = go.Figure(go.Funnel(
        y=funnel_names,
        x=funnel_values,
        textposition="inside",
        textinfo="label+value+percent initial",
        marker=dict(color=colors),
        hovertemplate="<b>%{y}</b><br>Count: %{x:,}<br>Share of all firms: %{percentInitial:.2f}%<extra></extra>"
    ))
    
    fig.update_layout(
        height=600,
        font=dict(size=11),
        margin=dict(l=100, r=50, t=50, b=50),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics box
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Classifiable Firms", f"{all_firms:,}")
    with col2:
        st.metric("HGF Share", f"{(hgf_count/all_firms*100):.2f}%")
    with col3:
        st.metric("Consistent HGF Share", f"{(consistent_hgf_count/all_firms*100):.2f}%")

# ============================================================================
# PAGE 2: MULTI-YEAR TRENDS
# ============================================================================
elif page == "Multi-Year Trends":
    st.header("2️⃣ Multi-Year Trend Analysis")
    
    available_categories = [
        "scaler", "hgf", "consistent_hgf", "consistent_hypergrower",
        "gazelle", "mature_hgf", "scaleup", "superstar"
    ]
    
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
    
    # Chart: Trend lines for main categories
    st.subheader("Trend: Main Categories")
    
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
    
    # Chart: Detailed classifications
    st.subheader("Trend: Detailed Classifications")
    
    chart_data_detail = pd.DataFrame()
    for cat in ["gazelle", "mature_hgf", "scaleup", "superstar"]:
        cat_name = cat.replace("_", " ").title()
        values = []
        for year in [2020, 2021, 2022, 2023, 2024]:
            col_name = f"{year}_{cat}"
            count = (df[col_name] == 1).sum() if col_name in df.columns else 0
            values.append(count)
        chart_data_detail[cat_name] = values
    
    chart_data_detail["Year"] = [2020, 2021, 2022, 2023, 2024]
    st.line_chart(chart_data_detail.set_index("Year"))

# ============================================================================
# PAGE 3: INDUSTRY & REGION ANALYSIS
# ============================================================================
elif page == "Industry & Region Analysis":
    st.header("3️⃣ Industry & Region Analysis (2024)")
    
    st.sidebar.header("Filters")
    
    region_options = sorted([x for x in master_company_table["region"].dropna().unique()])
    industry_options = sorted([x for x in master_company_table["nace_section"].dropna().unique()])
    
    classification_col = "high_growth_classification"
    class_options = sorted([str(x) for x in master_company_table[classification_col].dropna().unique()]) if classification_col in master_company_table.columns else []
    
    selected_regions = st.sidebar.multiselect("Region", region_options, default=region_options[:5])
    selected_industries = st.sidebar.multiselect("Industry", industry_options, default=industry_options[:10])
    selected_classes = st.sidebar.multiselect("Classification", class_options, default=class_options) if class_options else []
    
    # Filter data
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
    col3.metric("Not High-Growth", f"{int(not_high_growth_firms):,}")
    col4.metric("HGF Share", f"{share_high_growth:.1%}")
    
    # Industry aggregation
    industry_filtered = (
        filtered.groupby("nace_section", dropna=False)
        .agg(
            total_firms=("company_name", "count"),
            high_growth_firms=(classification_col, lambda x: (x == 1).sum())
        )
        .reset_index()
    )
    industry_filtered["share_high_growth"] = industry_filtered["high_growth_firms"] / industry_filtered["total_firms"]
    
    # Region aggregation
    region_filtered = (
        filtered.groupby("region", dropna=False)
        .agg(
            total_firms=("company_name", "count"),
            high_growth_firms=(classification_col, lambda x: (x == 1).sum())
        )
        .reset_index()
    )
    region_filtered["share_high_growth"] = region_filtered["high_growth_firms"] / region_filtered["total_firms"]
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("High-Growth Share by Industry")
        plot_industry = industry_filtered.dropna(subset=["share_high_growth"]).sort_values(
            "share_high_growth", ascending=False
        )
        if len(plot_industry) > 0:
            st.bar_chart(plot_industry.set_index("nace_section")["share_high_growth"])
        else:
            st.info("No industry data available for the selected filters.")
    
    with chart_col2:
        st.subheader("High-Growth Share by Region")
        plot_region = region_filtered.dropna(subset=["share_high_growth"]).sort_values(
            "share_high_growth", ascending=False
        )
        if len(plot_region) > 0:
            st.bar_chart(plot_region.set_index("region")["share_high_growth"])
        else:
            st.info("No region data available for the selected filters.")
    
    # Size band analysis
    size_col = "size_band_2021" if "size_band_2021" in master_company_table.columns else None
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

# ============================================================================
# PAGE 4: COMPANY EXPLORER
# ============================================================================
elif page == "Company Explorer":
    st.header("4️⃣ Company-Level Data Explorer")
    
    st.subheader("Filter and Explore Individual Firms")
    
    # Filters
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        selected_year_company = st.selectbox("Classification Year", [2020, 2021, 2022, 2023, 2024], key="company_year")
    
    with filter_col2:
        region_filter_options = sorted([x for x in df["region"].dropna().unique()])
        selected_region_comp = st.multiselect("Region", region_filter_options, default=region_filter_options[:3], key="region_filter")
    
    with filter_col3:
        category_filter = st.multiselect(
            "Firm Categories",
            options=["Scalers", "HGFs", "Consistent HGFs", "Hypergrowers", "Gazelles", "Mature HGFs", "Scaleups", "Superstars"],
            default=["HGFs", "Consistent HGFs"],
            key="category_filter"
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
    filtered_companies = df[df["region"].isin(selected_region_comp)].copy()
    
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
# PAGE 5: DEFINITIONS & HELP
# ============================================================================
elif page == "Definitions & Help":
    st.header("5️⃣ Classification Definitions & Help")
    
    with st.expander("📖 Classification Definitions", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Growth-Based Classifications
            
            **Scalers**
            - Average Annualised Growth Rate (AAGR) > 10% over 3-year period
            - Minimum 10 employees at start of period
            - Broadest category of growing firms
            
            **High-Growth Firms (HGFs)**
            - AAGR > 20% over 3-year period
            - Minimum 10 employees at start of period
            - Subset of Scalers with strong growth
            
            **Consistent HGFs**
            - Meet HGF criteria (AAGR > 20%)
            - Year-over-year growth > 20% in at least 2 of 3 years
            - More consistent growth pattern than HGFs
            """)
        
        with col2:
            st.markdown("""
            ### Age-Based Classifications
            
            **Gazelles**
            - Young Consistent HGFs
            - Company age ≤ 10 years at start of period
            - Represents high growth in young firms
            
            **Mature HGFs**
            - Established Consistent HGFs
            - Company age > 10 years at start of period
            
            **Consistent Hypergrowers**
            - Meet HGF criteria (AAGR > 20%)
            - Year-over-year growth > 40% in at least 2 of 3 years
            - Exceptional growth intensity
            
            **Scaleups & Superstars**
            - Young (≤10 yrs) and Mature (>10 yrs) Hypergrowers
            - Fastest-growing segment
            """)
    
    with st.expander("📊 Calculation Methods"):
        st.markdown("""
        ### Year-over-Year Growth
        ```
        Growth Rate = (Employees in Year N - Employees in Year N-1) / Employees in Year N-1
        ```
        
        ### Annual Annualized Growth Rate (AAGR)
        ```
        AAGR = [(End Year Employees / Start Year Employees)^(1/3) - 1] × 100
        ```
        Example for 2024 classification (2021-2024 period):
        ```
        AAGR_2024 = [(emp_2024 / emp_2021)^(1/3) - 1] × 100
        ```
        
        ### Rolling 3-Year Windows
        | Year | Base Year | End Year | Period |
        |------|-----------|----------|---------|
        | 2020 | 2017 | 2020 | 3 years |
        | 2021 | 2018 | 2021 | 3 years |
        | 2022 | 2019 | 2022 | 3 years |
        | 2023 | 2020 | 2023 | 3 years |
        | 2024 | 2021 | 2024 | 3 years |
        """)
    
    with st.expander("⚙️ Data Handling Rules"):
        st.markdown("""
        ### Rule 1: Missingness
        If input employee value is unavailable (missing), the output classification is also unavailable ("n.a.")
        
        ### Rule 2: No Zero Estimation
        Do not convert missing values to zero. Maintain missingness to preserve data integrity.
        
        ### Rule 3: Proper Windows
        Each classification year uses a separate 3-year rolling window with its own base and end years.
        
        ### Rule 4: Size Threshold
        Minimum 10 employees at the beginning of the 3-year period. Smaller firms are marked as "n.a."
        
        This ensures meaningful and comparable growth metrics across firms.
        """)
    
    with st.expander("❓ Frequently Asked Questions"):
        st.markdown("""
        **Q: Why do some firms show "n.a." for classifications?**
        A: Missing employee data, fewer than 10 employees at period start, or incomplete growth information.
        
        **Q: How are Gazelles different from Superstars?**
        A: Gazelles are young (≤10 yrs) Consistent HGFs (20%+ growth), while Superstars are young Consistent Hypergrowers (40%+ growth).
        
        **Q: Can a firm be classified in multiple categories in one year?**
        A: Yes. Hierarchy structure means: Superstars are subset of Hypergrowers, which are subset of HGFs, which are subset of Scalers.
        
        **Q: Why use 3-year rolling windows?**
        A: Smooths out year-to-year volatility and captures medium-term growth trends.
        
        **Q: What's the data source?**
        A: Bureau van Dijk employment database for Austrian firms (2017-2024).
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 12px; color: #666;'>
<p>Austria Combined ESI Dashboard | Multi-Year Classifications Analysis</p>
<p>Data Source: Bureau van Dijk | Classification Years: 2020-2024 | Created: March 2026</p>
</div>
""", unsafe_allow_html=True)
