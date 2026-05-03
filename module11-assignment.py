# Module 11 Assignment: Data Visualization with Matplotlib
# SunCoast Retail Visual Analysis

# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Welcome message
print("=" * 60)
print("SUNCOAST RETAIL VISUAL ANALYSIS")
print("=" * 60)

# ----- USE THE FOLLOWING CODE TO CREATE SAMPLE DATA (DO NOT MODIFY) -----
np.random.seed(42)


_QFREQ = 'QE' if int(pd.__version__.split('.')[0]) >= 2 else 'Q'
quarters = pd.date_range(start='2022-01-01', periods=8, freq=_QFREQ)
quarter_labels = ['Q1 2022', 'Q2 2022', 'Q3 2022', 'Q4 2022',
                  'Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023']

locations = ['Tampa', 'Miami', 'Orlando', 'Jacksonville']
categories = ['Electronics', 'Clothing', 'Home Goods', 'Sporting Goods', 'Beauty']

quarterly_data = []

for quarter_idx, quarter in enumerate(quarters):
    for location in locations:
        for category in categories:
            base_sales = np.random.normal(loc=100000, scale=20000)
            seasonal_factor = 1.0
            if quarter.quarter == 4:
                seasonal_factor = 1.3
            elif quarter.quarter == 1:
                seasonal_factor = 0.8

            location_factor = {
                'Tampa': 1.0, 'Miami': 1.2, 'Orlando': 0.9, 'Jacksonville': 0.8
            }[location]

            category_factor = {
                'Electronics': 1.5, 'Clothing': 1.0, 'Home Goods': 0.8,
                'Sporting Goods': 0.7, 'Beauty': 0.9
            }[category]

            growth_factor = (1 + 0.05 / 4) ** quarter_idx
            sales = base_sales * seasonal_factor * location_factor * category_factor * growth_factor
            sales = sales * np.random.normal(loc=1.0, scale=0.1)
            ad_spend = (sales ** 0.7) * 0.05 * np.random.normal(loc=1.0, scale=0.2)

            quarterly_data.append({
                'Quarter': quarter,
                'QuarterLabel': quarter_labels[quarter_idx],
                'Location': location,
                'Category': category,
                'Sales': round(sales, 2),
                'AdSpend': round(ad_spend, 2),
                'Year': quarter.year
            })

customer_data = []
total_customers = 2000

age_params = {
    'Tampa': (45, 15),
    'Miami': (35, 12),
    'Orlando': (38, 14),
    'Jacksonville': (42, 13)
}

for location in locations:
    mean_age, std_age = age_params[location]
    customer_count = int(total_customers * {
        'Tampa': 0.3, 'Miami': 0.35, 'Orlando': 0.2, 'Jacksonville': 0.15
    }[location])

    ages = np.random.normal(loc=mean_age, scale=std_age, size=customer_count)
    ages = np.clip(ages, 18, 80).astype(int)

    for age in ages:
        if age < 30:
            category_preference = np.random.choice(categories, p=[0.3, 0.3, 0.1, 0.2, 0.1])
        elif age < 50:
            category_preference = np.random.choice(categories, p=[0.25, 0.2, 0.25, 0.15, 0.15])
        else:
            category_preference = np.random.choice(categories, p=[0.15, 0.1, 0.35, 0.1, 0.3])

        base_amount = np.random.gamma(shape=5, scale=20)
        price_tier = np.random.choice(['Budget', 'Mid-range', 'Premium'], p=[0.3, 0.5, 0.2])
        tier_factor = {'Budget': 0.7, 'Mid-range': 1.0, 'Premium': 1.8}[price_tier]
        purchase_amount = base_amount * tier_factor

        customer_data.append({
            'Location': location,
            'Age': age,
            'Category': category_preference,
            'PurchaseAmount': round(purchase_amount, 2),
            'PriceTier': price_tier
        })

sales_df = pd.DataFrame(quarterly_data)
customer_df = pd.DataFrame(customer_data)

sales_df['Quarter_Num'] = sales_df['Quarter'].dt.quarter
sales_df['SalesPerDollarSpent'] = sales_df['Sales'] / sales_df['AdSpend']

print("\nSales Data Sample:")
print(sales_df.head())
print("\nCustomer Data Sample:")
print(customer_df.head())
print("\nDataFrames created successfully. Ready for visualization!")
# ----- END OF DATA CREATION -----


# Colour palette used throughout
LOCATION_COLORS = {
    'Tampa': '#2196F3', 'Miami': '#FF5722',
    'Orlando': '#4CAF50', 'Jacksonville': '#9C27B0'
}
CATEGORY_COLORS = {
    'Electronics': '#3F51B5', 'Clothing': '#E91E63',
    'Home Goods': '#FF9800', 'Sporting Goods': '#009688', 'Beauty': '#F44336'
}
TIER_COLORS = {'Budget': '#64B5F6', 'Mid-range': '#42A5F5', 'Premium': '#1565C0'}


# TODO 1: Time Series Visualization - Sales Trends

def plot_quarterly_sales_trend():
    """Line chart: total sales per quarter (all locations & categories)."""
    quarterly_totals = (
        sales_df.groupby('QuarterLabel')['Sales']
        .sum()
        .reindex(quarter_labels)          # preserve chronological order
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(quarterly_totals.index, quarterly_totals.values / 1e6,
            marker='o', color='#1976D2', linewidth=2.5, markersize=8,
            markerfacecolor='white', markeredgewidth=2)

    # Annotate the data points
    for i, (label, val) in enumerate(zip(quarterly_totals.index, quarterly_totals.values)):
        ax.annotate(f'${val/1e6:.2f}M',
                    xy=(i, val / 1e6), xytext=(0, 10),
                    textcoords='offset points', ha='center', fontsize=8)

    ax.set_title('SunCoast Retail – Quarterly Sales Trend (All Locations)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Quarter', fontsize=11)
    ax.set_ylabel('Total Sales ($ Millions)', fontsize=11)
    ax.set_xticks(range(len(quarter_labels)))
    ax.set_xticklabels(quarter_labels, rotation=30, ha='right')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    return fig


def plot_location_sales_comparison():
    """Multi-line chart: quarterly sales per location."""
    loc_quarterly = (
        sales_df.groupby(['QuarterLabel', 'Location'])['Sales']
        .sum()
        .unstack('Location')
        .reindex(quarter_labels)
    )

    markers = ['o', 's', '^', 'D']
    fig, ax = plt.subplots(figsize=(11, 5))

    for (loc, marker) in zip(locations, markers):
        ax.plot(loc_quarterly.index, loc_quarterly[loc] / 1e6,
                marker=marker, label=loc, color=LOCATION_COLORS[loc],
                linewidth=2, markersize=7)

    ax.set_title('Quarterly Sales Comparison by Location', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Quarter', fontsize=11)
    ax.set_ylabel('Sales ($ Millions)', fontsize=11)
    ax.set_xticks(range(len(quarter_labels)))
    ax.set_xticklabels(quarter_labels, rotation=30, ha='right')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))
    ax.legend(title='Location', framealpha=0.9)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    return fig


# TODO 2: Categorical Comparison - Product Performance by Location

def plot_category_performance_by_location():
    """Grouped bar chart: category sales per location (most recent quarter)."""
    recent = sales_df[sales_df['QuarterLabel'] == quarter_labels[-1]]
    pivot = recent.groupby(['Location', 'Category'])['Sales'].sum().unstack('Category')

    n_locs = len(locations)
    n_cats = len(categories)
    x = np.arange(n_locs)
    width = 0.15

    fig, ax = plt.subplots(figsize=(13, 6))

    for i, cat in enumerate(categories):
        offset = (i - n_cats / 2 + 0.5) * width
        bars = ax.bar(x + offset, pivot[cat] / 1e3, width=width,
                      label=cat, color=CATEGORY_COLORS[cat], edgecolor='white', linewidth=0.5)

    ax.set_title(f'Category Performance by Location – {quarter_labels[-1]}',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Location', fontsize=11)
    ax.set_ylabel('Sales ($ Thousands)', fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(locations)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}K'))
    ax.legend(title='Category', bbox_to_anchor=(1.01, 1), loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    return fig


def plot_sales_composition_by_location():
    """Stacked bar chart: % breakdown of sales by category per location."""
    pivot = (
        sales_df.groupby(['Location', 'Category'])['Sales']
        .sum()
        .unstack('Category')
        .reindex(locations)
    )
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(len(locations))

    for cat in categories:
        ax.bar(locations, pivot_pct[cat], bottom=bottom,
               label=cat, color=CATEGORY_COLORS[cat], edgecolor='white', linewidth=0.5)
        # Label inside bar if segment is large enough
        for j, (loc, val) in enumerate(zip(locations, pivot_pct[cat])):
            if val > 5:
                ax.text(j, bottom[j] + val / 2, f'{val:.1f}%',
                        ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        bottom += pivot_pct[cat].values

    ax.set_title('Sales Composition by Location (% Share per Category)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Location', fontsize=11)
    ax.set_ylabel('Percentage of Sales (%)', fontsize=11)
    ax.set_ylim(0, 105)
    ax.legend(title='Category', bbox_to_anchor=(1.01, 1), loc='upper left')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    return fig


# TODO 3: Relationship Analysis - Advertising and Sales

def plot_ad_spend_vs_sales():
    """Scatter plot: advertising spend vs sales with best-fit line."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for loc in locations:
        subset = sales_df[sales_df['Location'] == loc]
        ax.scatter(subset['AdSpend'] / 1e3, subset['Sales'] / 1e6,
                   label=loc, color=LOCATION_COLORS[loc], alpha=0.65, s=50, edgecolors='none')

    # Best-fit line over all data using numpy
    x_data = sales_df['AdSpend'].values
    y_data = sales_df['Sales'].values
    coeffs = np.polyfit(x_data, y_data, 1)
    slope, intercept = coeffs
    ss_res = np.sum((y_data - (slope * x_data + intercept)) ** 2)
    ss_tot = np.sum((y_data - y_data.mean()) ** 2)
    r_squared = 1 - ss_res / ss_tot

    x_fit = np.linspace(x_data.min(), x_data.max(), 200)
    ax.plot(x_fit / 1e3, (slope * x_fit + intercept) / 1e6,
            color='black', linewidth=1.8, linestyle='--', label=f'Best Fit  R²={r_squared:.2f}')

    # Annotate top outlier (highest sales)
    top = sales_df.loc[sales_df['Sales'].idxmax()]
    ax.annotate('Peak Sale',
                xy=(top['AdSpend'] / 1e3, top['Sales'] / 1e6),
                xytext=(15, -15), textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color='red'), color='red', fontsize=8)

    ax.set_title('Advertising Spend vs. Sales by Location', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Ad Spend ($ Thousands)', fontsize=11)
    ax.set_ylabel('Sales ($ Millions)', fontsize=11)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}K'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.1f}M'))
    ax.legend(framealpha=0.9)
    ax.grid(linestyle='--', alpha=0.4)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    return fig


def plot_ad_efficiency_over_time():
    """Line chart: average SalesPerDollarSpent per quarter."""
    efficiency = (
        sales_df.groupby('QuarterLabel')['SalesPerDollarSpent']
        .mean()
        .reindex(quarter_labels)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(efficiency.index, efficiency.values,
            marker='o', color='#E65100', linewidth=2.5, markersize=8,
            markerfacecolor='white', markeredgewidth=2)

    #  Best and worst quarter
    best_q = efficiency.idxmax()
    worst_q = efficiency.idxmin()
    ax.annotate(f'Best: {best_q}',
                xy=(list(quarter_labels).index(best_q), efficiency[best_q]),
                xytext=(10, 8), textcoords='offset points',
                fontsize=8, color='green',
                arrowprops=dict(arrowstyle='->', color='green'))
    ax.annotate(f'Worst: {worst_q}',
                xy=(list(quarter_labels).index(worst_q), efficiency[worst_q]),
                xytext=(10, -15), textcoords='offset points',
                fontsize=8, color='red',
                arrowprops=dict(arrowstyle='->', color='red'))

    ax.axhline(efficiency.mean(), color='gray', linestyle=':', linewidth=1.5,
               label=f'Average: {efficiency.mean():.1f}x')
    ax.set_title('Advertising Efficiency Over Time (Sales per $1 Ad Spend)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Quarter', fontsize=11)
    ax.set_ylabel('Sales per Dollar of Ad Spend', fontsize=11)
    ax.set_xticks(range(len(quarter_labels)))
    ax.set_xticklabels(quarter_labels, rotation=30, ha='right')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    return fig


# TODO 4: Distribution Analysis - Customer Demographics

def plot_customer_age_distribution():
    """Histograms: overall age distribution + one per location (subplots)."""
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle('Customer Age Distribution – Overall and by Location',
                 fontsize=15, fontweight='bold', y=1.01)

    panels = [('All Locations', customer_df)] + [
        (loc, customer_df[customer_df['Location'] == loc]) for loc in locations
    ]
    # Only 5 panels; hide the 6th
    axes_flat = axes.flatten()

    for ax, (title, data) in zip(axes_flat, panels):
        ax.hist(data['Age'], bins=20, color='#1976D2', edgecolor='white',
                alpha=0.8, density=False)
        mean_age = data['Age'].mean()
        med_age = data['Age'].median()
        ax.axvline(mean_age, color='red', linewidth=1.5, linestyle='--',
                   label=f'Mean {mean_age:.1f}')
        ax.axvline(med_age, color='orange', linewidth=1.5, linestyle='-.',
                   label=f'Median {med_age:.1f}')
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlabel('Age', fontsize=9)
        ax.set_ylabel('Count', fontsize=9)
        ax.legend(fontsize=8)
        ax.spines[['top', 'right']].set_visible(False)

    axes_flat[-1].set_visible(False)
    plt.tight_layout()
    return fig


def plot_purchase_by_age_group():
    """Box plots: purchase amounts by age group."""
    bins = [18, 30, 45, 60, 80]
    labels_ag = ['18–30', '31–45', '46–60', '61+']
    customer_df['AgeGroup'] = pd.cut(customer_df['Age'], bins=bins,
                                     labels=labels_ag, right=True)

    groups = [customer_df[customer_df['AgeGroup'] == g]['PurchaseAmount'].values
              for g in labels_ag]

    fig, ax = plt.subplots(figsize=(9, 5))
    bp = ax.boxplot(groups, tick_labels=labels_ag, patch_artist=True,
                    medianprops=dict(color='white', linewidth=2))

    colors = ['#1565C0', '#1976D2', '#42A5F5', '#90CAF9']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)

    ax.set_title('Purchase Amounts by Age Group', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Age Group', fontsize=11)
    ax.set_ylabel('Purchase Amount ($)', fontsize=11)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}'))
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    return fig


# TODO 5: Sales Distribution - Pricing Tiers

def plot_purchase_amount_distribution():
    """Histogram: distribution of individual purchase amounts."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(customer_df['PurchaseAmount'], bins=40,
            color='#00897B', edgecolor='white', alpha=0.85)

    ax.axvline(customer_df['PurchaseAmount'].mean(), color='red', linewidth=1.8,
               linestyle='--', label=f"Mean ${customer_df['PurchaseAmount'].mean():.2f}")
    ax.axvline(customer_df['PurchaseAmount'].median(), color='orange', linewidth=1.8,
               linestyle='-.', label=f"Median ${customer_df['PurchaseAmount'].median():.2f}")

    ax.set_title('Distribution of Purchase Amounts', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Purchase Amount ($)', fontsize=11)
    ax.set_ylabel('Number of Customers', fontsize=11)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}'))
    ax.legend()
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    return fig


def plot_sales_by_price_tier():
    """Pie chart: total purchase value by price tier."""
    tier_sales = customer_df.groupby('PriceTier')['PurchaseAmount'].sum()
    tier_order = ['Budget', 'Mid-range', 'Premium']
    tier_sales = tier_sales.reindex(tier_order)

    explode = [0.0, 0.0, 0.0]
    max_idx = tier_sales.values.argmax()
    explode[max_idx] = 0.07

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        tier_sales,
        labels=tier_order,
        autopct='%1.1f%%',
        explode=explode,
        colors=[TIER_COLORS[t] for t in tier_order],
        startangle=140,
        wedgeprops=dict(edgecolor='white', linewidth=1.5),
        pctdistance=0.80
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_color('white')
        at.set_fontweight('bold')

    ax.set_title('Sales Breakdown by Price Tier', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig


# TODO 6: Market Share Analysis

def plot_category_market_share():
    """Pie chart: overall sales share per product category."""
    cat_sales = sales_df.groupby('Category')['Sales'].sum().reindex(categories)
    explode = [0.0] * len(categories)
    explode[cat_sales.values.argmax()] = 0.07

    fig, ax = plt.subplots(figsize=(8, 7))
    wedges, texts, autotexts = ax.pie(
        cat_sales,
        labels=categories,
        autopct='%1.1f%%',
        explode=explode,
        colors=[CATEGORY_COLORS[c] for c in categories],
        startangle=120,
        wedgeprops=dict(edgecolor='white', linewidth=1.5),
        pctdistance=0.80
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight('bold')
        at.set_color('white')

    ax.set_title('Market Share by Product Category', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig


def plot_location_sales_distribution():
    """Pie chart: total sales distribution across store locations."""
    loc_sales = sales_df.groupby('Location')['Sales'].sum().reindex(locations)

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        loc_sales,
        labels=locations,
        autopct='%1.1f%%',
        colors=[LOCATION_COLORS[l] for l in locations],
        startangle=130,
        wedgeprops=dict(edgecolor='white', linewidth=1.5),
        pctdistance=0.80
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight('bold')
        at.set_color('white')

    ax.set_title('Sales Distribution by Store Location', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig


# TODO 7: Comprehensive Dashboard

def create_business_dashboard():
    """4-subplot dashboard highlighting key business insights."""
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle('SunCoast Retail – Executive Business Dashboard',
                 fontsize=17, fontweight='bold', y=1.01)

    # Subplot 1: Quarterly sales trend (top-left)
    ax1 = fig.add_subplot(2, 2, 1)
    quarterly_totals = (
        sales_df.groupby('QuarterLabel')['Sales']
        .sum().reindex(quarter_labels)
    )
    ax1.plot(range(len(quarter_labels)), quarterly_totals / 1e6,
             marker='o', color='#1976D2', linewidth=2, markersize=6,
             markerfacecolor='white', markeredgewidth=2)
    ax1.fill_between(range(len(quarter_labels)), quarterly_totals / 1e6, alpha=0.15, color='#1976D2')
    ax1.set_title('Overall Quarterly Sales Trend', fontsize=11, fontweight='bold')
    ax1.set_xticks(range(len(quarter_labels)))
    ax1.set_xticklabels([q.replace(' ', '\n') for q in quarter_labels], fontsize=7)
    ax1.set_ylabel('Sales ($ M)', fontsize=9)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.1f}M'))
    ax1.grid(axis='y', linestyle='--', alpha=0.4)
    ax1.spines[['top', 'right']].set_visible(False)

    # Subplot 2: Location comparison – bar (top-right)
    ax2 = fig.add_subplot(2, 2, 2)
    loc_totals = sales_df.groupby('Location')['Sales'].sum().reindex(locations)
    bars = ax2.bar(locations, loc_totals / 1e6,
                   color=[LOCATION_COLORS[l] for l in locations], edgecolor='white')
    for bar, val in zip(bars, loc_totals / 1e6):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                 f'${val:.1f}M', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax2.set_title('Total Sales by Location (2022–2023)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Sales ($ M)', fontsize=9)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))
    ax2.spines[['top', 'right']].set_visible(False)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)

    #  Subplot 3: Category market share pie (bottom-left)
    ax3 = fig.add_subplot(2, 2, 3)
    cat_sales = sales_df.groupby('Category')['Sales'].sum().reindex(categories)
    explode = [0.0] * len(categories)
    explode[cat_sales.values.argmax()] = 0.06
    ax3.pie(cat_sales, labels=categories, autopct='%1.1f%%', explode=explode,
            colors=[CATEGORY_COLORS[c] for c in categories],
            startangle=120, pctdistance=0.80,
            wedgeprops=dict(edgecolor='white', linewidth=1))
    ax3.set_title('Category Market Share', fontsize=11, fontweight='bold')

    # Subplot 4: Ad efficiency over time (bottom-right)
    ax4 = fig.add_subplot(2, 2, 4)
    eff = (
        sales_df.groupby('QuarterLabel')['SalesPerDollarSpent']
        .mean().reindex(quarter_labels)
    )
    ax4.bar(range(len(quarter_labels)), eff,
            color=['#2E7D32' if v >= eff.mean() else '#C62828' for v in eff],
            edgecolor='white')
    ax4.axhline(eff.mean(), color='black', linestyle='--', linewidth=1.2,
                label=f'Avg {eff.mean():.1f}x')
    ax4.set_title('Ad Efficiency per Quarter\n(Sales / $1 Ad Spend)',
                  fontsize=11, fontweight='bold')
    ax4.set_xticks(range(len(quarter_labels)))
    ax4.set_xticklabels([q.replace(' ', '\n') for q in quarter_labels], fontsize=7)
    ax4.set_ylabel('Sales per $ Ad Spend', fontsize=9)
    ax4.legend(fontsize=8)
    ax4.spines[['top', 'right']].set_visible(False)
    ax4.grid(axis='y', linestyle='--', alpha=0.4)

    plt.tight_layout()
    return fig


# Main

def main():
    print("\n" + "=" * 60)
    print("SUNCOAST RETAIL VISUAL ANALYSIS RESULTS")
    print("=" * 60)

    # Time Series Analysis
    fig1 = plot_quarterly_sales_trend()
    print("✓ Fig 1  – Quarterly Sales Trend")

    fig2 = plot_location_sales_comparison()
    print("✓ Fig 2  – Location Sales Comparison")

    # Categorical Comparison
    fig3 = plot_category_performance_by_location()
    print("✓ Fig 3  – Category Performance by Location")

    fig4 = plot_sales_composition_by_location()
    print("✓ Fig 4  – Sales Composition by Location")

    # Relationship Analysis
    fig5 = plot_ad_spend_vs_sales()
    print("✓ Fig 5  – Ad Spend vs Sales")

    fig6 = plot_ad_efficiency_over_time()
    print("✓ Fig 6  – Ad Efficiency Over Time")

    # Distribution Analysis
    fig7 = plot_customer_age_distribution()
    print("✓ Fig 7  – Customer Age Distribution")

    fig8 = plot_purchase_by_age_group()
    print("✓ Fig 8  – Purchase by Age Group")

    # Sales Distribution
    fig9 = plot_purchase_amount_distribution()
    print("✓ Fig 9  – Purchase Amount Distribution")

    fig10 = plot_sales_by_price_tier()
    print("✓ Fig 10 – Sales by Price Tier")

    # Market Share Analysis
    fig11 = plot_category_market_share()
    print("✓ Fig 11 – Category Market Share")

    fig12 = plot_location_sales_distribution()
    print("✓ Fig 12 – Location Sales Distribution")

    # Dashboard
    fig13 = create_business_dashboard()
    print("✓ Fig 13 – Business Dashboard")

    # ── KEY BUSINESS INSIGHTS ────────────────────────────────────────────────
    print("\nKEY BUSINESS INSIGHTS:")
    print("-" * 60)

    # 1. Overall trend
    qt = sales_df.groupby('QuarterLabel')['Sales'].sum().reindex(quarter_labels)
    growth = (qt.iloc[-1] - qt.iloc[0]) / qt.iloc[0] * 100
    print(f"\n1. SALES TREND: Overall sales grew {growth:.1f}% from {quarter_labels[0]} "
          f"to {quarter_labels[-1]}, with a clear Q4 holiday season spike each year.")
    print("   → Recommendation: Stock up inventory and increase ad spend in Q3 to "
          "maximise Q4 momentum.")

    # 2. Location performance
    loc_totals = sales_df.groupby('Location')['Sales'].sum().sort_values(ascending=False)
    top_loc = loc_totals.index[0]
    low_loc = loc_totals.index[-1]
    print(f"\n2. LOCATION PERFORMANCE: {top_loc} leads all locations in total sales "
          f"while {low_loc} lags behind.")
    print(f"   → Recommendation: Investigate {low_loc}'s lower performance – consider "
          "localised marketing campaigns or product-mix adjustments.")

    # 3. Category leadership
    cat_totals = sales_df.groupby('Category')['Sales'].sum().sort_values(ascending=False)
    top_cat = cat_totals.index[0]
    print(f"\n3. PRODUCT MIX: Electronics is the dominant category (~{cat_totals[top_cat]/cat_totals.sum()*100:.0f}% "
          "of total sales).")
    print("   → Recommendation: Protect Electronics shelf space and explore premium "
          "product bundles to grow average transaction value.")

    # 4. Advertising efficiency
    avg_eff = sales_df['SalesPerDollarSpent'].mean()
    print(f"\n4. AD EFFICIENCY: On average, every $1 of advertising generates ${avg_eff:.1f} "
          "in sales. Q4 shows the highest returns.")
    print("   → Recommendation: Shift ad budgets toward Q4 and evaluate underperforming "
          "quarters to optimise ROI.")

    # 5. Demographics
    print("\n5. CUSTOMER DEMOGRAPHICS: Miami skews younger (avg ~35 yrs) and Tampa older "
          "(avg ~45 yrs), suggesting location-specific product and messaging opportunities.")
    print("   → Recommendation: Tailor in-store and digital promotions to each location's "
          "demographic profile (e.g., tech & sports in Miami; home goods & beauty in Tampa).")

    # 6. Pricing tiers
    tier_sums = customer_df.groupby('PriceTier')['PurchaseAmount'].sum()
    top_tier = tier_sums.idxmax()
    print(f"\n6. PRICE TIERS: '{top_tier}' drives the largest share of purchase revenue.")
    print("   → Recommendation: Ensure solid stock depth in the Mid-range tier and "
          "introduce loyalty rewards to nudge Budget shoppers upward.")

    print("\n" + "=" * 60)
    print("Analysis complete. Displaying all charts…")
    print("=" * 60)

    plt.show()


if __name__ == "__main__":
    main()