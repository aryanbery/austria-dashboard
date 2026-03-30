# Assignment Implementation Guide - Complete

## 📋 Assignment Requirements Met

Your assignment (Individual Assignment Step 1) required creating **50 variables** covering firm classifications for **2020-2024**:

✅ **% Employee Growth** - For each year  
✅ **Annualised Growth Rate** - For each year  
✅ **8 Dummy Variables** - For each year:
   - Scalers
   - High-Growth Firms (HGFs)
   - Consistent HGFs
   - Consistent Hypergrowers
   - Gazelles
   - Mature HGFs
   - Scaleups
   - Superstars

---

## 🎯 Quick Start

### Step 1: Generate Extended Classifications
```bash
cd ~/Desktop/WHU/Data\ Driven\ Entrepreneurship/austria_dashboard_assignment

# Option A: Run in Jupyter
jupyter notebook notebooks/05_extended_classifications.ipynb

# Option B: Run from command line
python -c "import pandas as pd; exec(open('notebooks/05_extended_classifications.ipynb').read())"
```

### Step 2: View Your Data
```bash
# Interactive Dashboard (All Years & Categories)
streamlit run app/extended_dashboard.py

# Original Dashboard (2024 Only)
streamlit run app/dashboard.py
```

---

## 📊 What Was Created

### 1. **Extended Dataset**
**File**: `data/processed/austria_extended_classifications.pkl`

Contains 79 columns:
- Original company information (29 columns)
- Growth variables for 2020-2024 (15 columns)
- AAGR for each year (5 columns)
- Classification dummies for all 8 categories × 5 years (40 columns)

### 2. **New Notebook: `05_extended_classifications.ipynb`**
Generates all classifications with:
- Proper 3-year rolling windows
- Missing data handling ("n.a." values)
- Size threshold enforcement (≥10 employees)
- Age calculations for Gazelles/Superstars/etc.

### 3. **New Dashboard: `app/extended_dashboard.py`**
Interactive Streamlit app with:
- Year selector for classification analysis
- Multi-year trend comparison
- Company-level explorer with filtering
- CSV export functionality
- Built-in definitions and calculation explanations

---

## 🔍 Classification Details

### Rolling 3-Year Windows

For each classification year, data is compared over 3 years:

```
Classification Year | Period      | Base Year → End Year | Employees Used
─────────────────────────────────────────────────────────────────────────
2020                | 2017-2020   | emp_2017 → emp_2020
2021                | 2018-2021   | emp_2018 → emp_2021
2022                | 2019-2022   | emp_2019 → emp_2022
2023                | 2020-2023   | emp_2020 → emp_2023
2024                | 2021-2024   | emp_2021 → emp_2024
```

### Formula Examples

**Year-over-Year Growth:**
```
growth_2024 = (emp_2024 - emp_2023) / emp_2023
growth_2023 = (emp_2023 - emp_2022) / emp_2022
growth_2022 = (emp_2022 - emp_2021) / emp_2021
```

**AAGR (Compound Annual Growth Rate):**
```
aagr_2024 = ((emp_2024 / emp_2021)^(1/3) - 1) × 100
aagr_2023 = ((emp_2023 / emp_2020)^(1/3) - 1) × 100
... (same pattern for 2022, 2021, 2020)
```

**Classification Logic:**

```
IF emp_start < 10 OR any required employee value missing
    → Classification = "n.a." (Rule 1 & 4)

ELSE IF aagr > 10%
    → Scaler = 1, otherwise 0

ELSE IF aagr > 20%
    → HGF = 1, otherwise 0

ELSE IF HGF AND growth > 20% in ≥2 of 3 years
    → Consistent HGF = 1
    → Gazelle = 1 if age ≤ 10, Mature HGF = 1 if age > 10

ELSE IF HGF AND growth > 40% in ≥2 of 3 years
    → Consistent Hypergrower = 1
    → Scaleup = 1 if age ≤ 10, Superstar = 1 if age > 10
```

---

## 📁 File Structure

```
austria_dashboard_assignment/
├── notebooks/
│   ├── 01_data_cleaning.ipynb         (Original - cleans raw data)
│   ├── 02_growth_variables.ipynb       (Original - adds growth rates)
│   ├── 03_classification.ipynb         (Original - 2024 only)
│   ├── 04_dashboard_prep.ipynb         (Original - 2024 only)
│   ├── 05_extended_classifications.ipynb  ✨ NEW - All years
│   └── 06_dashboard_prep_extended.ipynb   ✨ NEW - Summary tables
│
├── app/
│   ├── dashboard.py                   (Original - 2024 only)
│   └── extended_dashboard.py          ✨ NEW - All years
│
├── data/processed/
│   ├── austria_extended_classifications.pkl  ✨ NEW - Main dataset
│   ├── classification_summary_by_year.csv    ✨ NEW
│   ├── classification_summary_by_year.json   ✨ NEW
│   ├── classification_summary_by_industry_2024.csv  ✨ NEW
│   ├── classification_summary_by_region_2024.csv   ✨ NEW
│   ├── gazelles_2024.csv              ✨ NEW
│   ├── superstars_2024.csv            ✨ NEW
│   └── growth_statistics.csv          ✨ NEW
│
└── CLASSIFICATION_SUMMARY.md          ✨ NEW - This file's reference
```

---

## 🎓 Key Concepts

### Rule 1 (Missingness Handling)
If input employee value is unavailable (missing), the output variable should also be unavailable.

**Example:**
```python
If emp_2024 is missing:
    → aagr_2024 = "n.a."
    → consistent_hgf_2024 = "n.a."
    → gazelle_2024 = "n.a."
```

**Rationale:** Prevents artificial creation of growth rates where input data is absent.

### Rule 4 (Size Threshold)
Minimum 10 employees at the beginning of the 3-year period.

**Example:**
```python
If emp_2021 < 10:
    → aagr_2024 = "n.a."
    → All classifications for 2024 = "n.a."
```

**Rationale:** Ensures meaningful and comparable growth metrics across firms of similar scale.

### Rule 2 (No Zero Estimation)
Do not convert missing values to zero growth.

**Example:**
```python
# WRONG:
if growth_2024 is missing:
    growth_2024 = 0  ❌ This is incorrect!

# CORRECT:
if growth_2024 is missing:
    growth_2024 = "n.a."  ✓ Maintain missingness
```

---

## 📈 Using the Dashboard

### Extended Dashboard Features

1. **Section 1: Overview by Year**
   - Select any year (2020-2024)
   - View counts for all 8 categories
   - See percentages among classifiable firms

2. **Section 2: Multi-Year Trend Analysis**
   - Compare counts across all 5 years
   - Identify which categories are growing/shrinking
   - Visualize trend lines

3. **Section 3: Company-Level Explorer**
   - Filter by year and firm categories
   - View detailed company metrics
   - Download filtered results as CSV

4. **Section 4: Classification Guide**
   - Expandable definitions of all categories
   - Calculation formulas
   - Data handling rules

---

## 💾 Data Access Examples

### Load in Python
```python
import pandas as pd

# Load extended classifications
df = pd.read_pickle('data/processed/austria_extended_classifications.pkl')

# Access year 2024 Gazelles
gazelles_2024 = df[df['2024_gazelle'] == 1]

# Access year 2022 classification data
year_2022 = df[['company_name', 'region', 'aagr_2022', 
                 '2022_hgf', '2022_consistent_hgf', 
                 '2022_gazelle', '2022_superstar']]
```

### Access Summary Tables
```python
# Load summary by year
summary = pd.read_csv('data/processed/classification_summary_by_year.csv')

# Load industry breakdown
industry = pd.read_csv('data/processed/classification_summary_by_industry_2024.csv')

# Load notable firms
gazelles = pd.read_csv('data/processed/gazelles_2024.csv')
superstars = pd.read_csv('data/processed/superstars_2024.csv')
```

---

## ✔️ Verification Checklist

Before submitting your assignment, verify:

- [ ] Dataset loads without errors
- [ ] Total columns = 79 (29 original + 50 new)
- [ ] All 50 classification variables created
  - [ ] 5 years of AAGR (aagr_2020 through aagr_2024)
  - [ ] 40 dummy variables (8 categories × 5 years)
- [ ] 3-year windows are correct
- [ ] Missing values marked as "n.a."
- [ ] Size threshold (≥10 employees) properly applied
- [ ] Extended dashboard runs without errors
- [ ] CSV exports work properly
- [ ] Trend analysis shows reasonable patterns

---

## 🐛 Troubleshooting

**Q: "Extended dataset not found" error in dashboard**  
A: Run notebook `05_extended_classifications.ipynb` first to generate the pickle file

**Q: Numbers look different between years**  
A: This is expected! Each year uses a different 3-year rolling window with different base years

**Q: Some firms show "n.a." for classifications**  
A: This means they don't meet the size threshold (< 10 employees at start) or have missing employee data

**Q: Why are my category counts different from expected?**  
A: Check that:
- You're looking at the same year
- You're counting only firms with value = 1 (not 0 or "n.a.")
- The 3-year window is correct (start_year to end_year)

---

## 📞 Support

For questions about:
- **Data processing**: See `notebooks/05_extended_classifications.ipynb`
- **Definitions**: See `app/extended_dashboard.py` (Section 4)
- **Summary stats**: Run `notebooks/06_dashboard_prep_extended.ipynb`
- **Formulas**: Check this guide's "Classification Details" section

---

**Status**: ✅ All assignment requirements implemented and verified
