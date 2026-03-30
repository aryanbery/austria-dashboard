# Austria Combined ESI Dashboard

Interactive Streamlit dashboard for analyzing Austrian company growth classifications (2020-2024).

## Features

- **Overview & Funnel**: Year-by-year funnel visualization showing firm classification hierarchy
- **Multi-Year Trends**: Compare growth patterns across 2020-2024
- **Industry & Region Analysis**: Filter by region, industry, and classification type
- **Company Explorer**: Detailed firm-level data with download capability
- **Definitions & Help**: Complete classification definitions and calculation methods

## Data

- **Source**: Bureau van Dijk employment database
- **Country**: Austria
- **Period**: 2020-2024
- **Min Size**: 10+ employees

## Classifications

- **Scalers**: AAGR > 10%
- **HGFs**: AAGR > 20%
- **Consistent HGFs**: HGF + 20%+ growth in 2+ of 3 years
- **Gazelles**: Young (<= 10 yrs) Consistent HGFs
- **Mature HGFs**: Established (> 10 yrs) Consistent HGFs
- **Hypergrowers**: HGF + 40%+ growth in 2+ of 3 years
- **Scaleups**: Young (<= 10 yrs) Hypergrowers
- **Superstars**: Established (> 10 yrs) Hypergrowers

## Installation

```bash
pip install -r requirements.txt
```

## Running Locally

```bash
streamlit run app/combined_dashboard.py
```

Visit `http://localhost:8503`

## Deployment

This dashboard is deployed on Streamlit Cloud and can be accessed at:
[Your app URL will be here]

## Project Structure

```
austria_dashboard_assignment/
├── app/
│   ├── combined_dashboard.py    # Main combined dashboard
│   ├── dashboard.py             # Original 2024-only dashboard
│   └── extended_dashboard.py    # Extended multi-year dashboard
├── data/
│   └── processed/               # Processed datasets
├── notebooks/                   # Jupyter notebooks for analysis
├── outputs/                     # Figures and reports
│   └── press_release/           # Press release documents
└── requirements.txt             # Python dependencies
```

## Author

Aryan Bery  
WHU - Otto Beisheim School of Management
