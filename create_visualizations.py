import pandas as pd
import matplotlib.pyplot as plt
import os

# Create directory
os.makedirs('outputs/figures', exist_ok=True)
print('Directory created')

# Load and process data
df = pd.read_pickle('data/raw/AT.pkl')
print('Data loaded, shape:', df.shape)

# Rename columns
column_rename_map = {
    'Company name Latin alphabet': 'company_name',
    'Country ISO code': 'country_code',
    'City\nLatin Alphabet': 'city',
    'NACE Rev. 2, core code (4 digits)': 'nace_code',
    'BvD ID number': 'bvd_id',
    'NACE Rev. 2 main section': 'nace_section',
    'Region in country': 'region_raw',
    'Status': 'status',
    'Date of incorporation': 'incorporation_date'
}
df = df.rename(columns=column_rename_map)

# Add employee columns
years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
for year in years:
    raw_col = f'Number of employees\n{year}'
    num_col = f'emp_{year}_num'
    if raw_col in df.columns:
        df[num_col] = pd.to_numeric(df[raw_col], errors='coerce')

# Clean region
region_col = 'Region in country clean'
if region_col in df.columns:
    df['region'] = df[region_col].str.strip()

# Calculate growth variables
def safe_growth(emp_current, emp_previous):
    if pd.isna(emp_current) or pd.isna(emp_previous) or emp_previous == 0:
        return 'n.a.'
    return (emp_current - emp_previous) / emp_previous

df['growth_2024'] = df.apply(lambda row: safe_growth(row['emp_2024_num'], row['emp_2023_num']), axis=1)
df['growth_2023'] = df.apply(lambda row: safe_growth(row['emp_2023_num'], row['emp_2022_num']), axis=1)
df['growth_2022'] = df.apply(lambda row: safe_growth(row['emp_2022_num'], row['emp_2021_num']), axis=1)

def calculate_aagr(growth_2024, growth_2023, growth_2022):
    growths = [growth_2024, growth_2023, growth_2022]
    if any(g == 'n.a.' for g in growths):
        return 'n.a.'
    product = 1
    for g in growths:
        product *= (1 + g)
    return product**(1/3) - 1

df['aagr_2024'] = df.apply(lambda row: calculate_aagr(row['growth_2024'], row['growth_2023'], row['growth_2022']), axis=1)

# Apply classification
def classify_high_growth_firm(row):
    if pd.isna(row['emp_2021_num']) or row['emp_2021_num'] < 10:
        return 'n.a.'
    required_growth = [row['growth_2024_num'], row['growth_2023_num'], row['growth_2022_num']]
    if any(pd.isna(g) for g in required_growth):
        return 'n.a.'
    avg_growth = sum(required_growth) / len(required_growth)
    if avg_growth > 0.10:
        return 1
    else:
        return 0

df['ConsistentHighGrowthFirm_2024'] = df.apply(classify_high_growth_firm, axis=1)

print('Data processing complete')

# Visual 1: Overall distribution
total_firms = len(df)
classified_firms = (df['ConsistentHighGrowthFirm_2024'] != 'n.a.').sum()
unclassified_firms = total_firms - classified_firms
high_growth_firms = (df['ConsistentHighGrowthFirm_2024'] == 1).sum()
not_high_growth_firms = (df['ConsistentHighGrowthFirm_2024'] == 0).sum()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.bar(['Classified', 'Unclassified'], [classified_firms, unclassified_firms],
        color=['#1f77b4', '#ff7f0e'], alpha=0.7)
ax1.set_title('Firm Classification Status', fontsize=14, fontweight='bold')
ax1.set_ylabel('Number of Firms', fontsize=12)
ax1.grid(axis='y', alpha=0.3)
for i, v in enumerate([classified_firms, unclassified_firms]):
    ax1.text(i, v + 500, f'{v:,}\n({v/total_firms:.1%})', ha='center', va='bottom', fontsize=10)

ax2.bar(['High-Growth', 'Not High-Growth'], [high_growth_firms, not_high_growth_firms],
        color=['#2ca02c', '#d62728'], alpha=0.7)
ax2.set_title('Distribution Among Classified Firms', fontsize=14, fontweight='bold')
ax2.set_ylabel('Number of Firms', fontsize=12)
ax2.grid(axis='y', alpha=0.3)
for i, v in enumerate([high_growth_firms, not_high_growth_firms]):
    ax2.text(i, v + 50, f'{v:,}\n({v/classified_firms:.1%})', ha='center', va='bottom', fontsize=10)

plt.suptitle('Austria High-Growth Firms: Overall Distribution', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('outputs/figures/growth_class_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print('Saved: outputs/figures/growth_class_distribution.png')

# Visual 2: Industry comparison
industry_stats = df.groupby('nace_section').agg(
    total_firms=('ConsistentHighGrowthFirm_2024', 'size'),
    classified_firms=('ConsistentHighGrowthFirm_2024', lambda x: (x != 'n.a.').sum()),
    high_growth_firms=('ConsistentHighGrowthFirm_2024', lambda x: (x == 1).sum())
).sort_values('total_firms', ascending=False).head(10)
industry_stats['high_growth_share'] = industry_stats['high_growth_firms'] / industry_stats['classified_firms']

fig, ax = plt.subplots(figsize=(12, 8))
industry_names = [name.split(' - ')[1][:30] + '...' if len(name.split(' - ')) > 1 and len(name.split(' - ')[1]) > 30
                 else name.split(' - ')[1] if len(name.split(' - ')) > 1
                 else name[:30] + '...' if len(name) > 30 else name
                 for name in industry_stats.index]
bars = ax.barh(industry_names, industry_stats['high_growth_share'] * 100, color='#1f77b4', alpha=0.7)
ax.set_title('High-Growth Firm Share by Industry (Top 10 by Firm Count)', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('High-Growth Firm Share (%)', fontsize=12)
ax.grid(axis='x', alpha=0.3)
for bar, share in zip(bars, industry_stats['high_growth_share']):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, f'{share:.1%}', ha='left', va='center', fontsize=10, fontweight='bold')
for i, (bar, total) in enumerate(zip(bars, industry_stats['total_firms'])):
    ax.text(0.5, bar.get_y() + bar.get_height()/2, f'{total:,} firms', ha='left', va='center', fontsize=9, alpha=0.8)
plt.tight_layout()
plt.savefig('outputs/figures/industry_growth_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print('Saved: outputs/figures/industry_growth_comparison.png')

# Visual 3: Regional comparison
region_stats = df.groupby('region').agg(
    total_firms=('ConsistentHighGrowthFirm_2024', 'size'),
    classified_firms=('ConsistentHighGrowthFirm_2024', lambda x: (x != 'n.a.').sum()),
    high_growth_firms=('ConsistentHighGrowthFirm_2024', lambda x: (x == 1).sum())
).sort_values('total_firms', ascending=False)
region_stats['high_growth_share'] = region_stats['high_growth_firms'] / region_stats['classified_firms']

fig, ax = plt.subplots(figsize=(12, 8))
region_stats_sorted = region_stats.sort_values('high_growth_share', ascending=True)
bars = ax.barh(range(len(region_stats_sorted)), region_stats_sorted['high_growth_share'] * 100, color='#2ca02c', alpha=0.7)
ax.set_title('High-Growth Firm Share by Region', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('High-Growth Firm Share (%)', fontsize=12)
ax.set_yticks(range(len(region_stats_sorted)))
ax.set_yticklabels(region_stats_sorted.index)
ax.grid(axis='x', alpha=0.3)
for bar, share in zip(bars, region_stats_sorted['high_growth_share']):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2, f'{share:.1%}', ha='left', va='center', fontsize=10, fontweight='bold')
for i, (bar, total) in enumerate(zip(bars, region_stats_sorted['total_firms'])):
    ax.text(0.2, bar.get_y() + bar.get_height()/2, f'{total:,} firms', ha='left', va='center', fontsize=9, alpha=0.8)
vienna_idx = list(region_stats_sorted.index).index('Wien')
bars[vienna_idx].set_color('#ff7f0e')
ax.text(bars[vienna_idx].get_width() + 0.05, bars[vienna_idx].get_y() + bars[vienna_idx].get_height()/2,
       f'{region_stats_sorted.loc["Wien", "high_growth_share"]:.1%} ← Vienna',
       ha='left', va='center', fontsize=11, fontweight='bold', color='#ff7f0e')
plt.tight_layout()
plt.savefig('outputs/figures/region_growth_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print('Saved: outputs/figures/region_growth_comparison.png')

print('All visualizations created successfully!')