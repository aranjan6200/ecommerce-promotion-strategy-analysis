"""
CommerceIQ E-commerce Price Elasticity Analysis
Case Study: Conglomerate Inc - Promotional Strategy Analysis

This notebook analyzes price elasticity and promotional effectiveness across
three categories: Diapers, Headphones, and Breakfast Cereals (2017-2019)


"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('ggplot')
sns.set_palette("husl")

# Configuration
DATA_FILE = 'ecom-elasticity-data1.tsv'
OUTPUT_DIR = 'outputs'

# Create output directory for visualizations
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*80)
print("COMMERCEIQ E-COMMERCE PRICE ELASTICITY ANALYSIS")
print("="*80)
print(f"\nLoading data from {DATA_FILE}...")

# ============================================================================
# DATA LOADING AND PREPROCESSING
# ============================================================================

def load_data(file_path):
    """
    Load and preprocess the e-commerce data.
    
    Assumptions:
    - Data is tab-separated
    - Columns: ASIN, Category, Date, Price, Units_Sold
    - Date format: YYYY-MM-DD
    """
    df = pd.read_csv(file_path, sep='\t', header=None, 
                     names=['ASIN', 'Category', 'Date', 'Price', 'Units_Sold'])
    
    # Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Extract year and month for analysis
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['YearMonth'] = df['Date'].dt.to_period('M')
    
    # Calculate revenue
    df['Revenue'] = df['Price'] * df['Units_Sold']
    
    print(f"✓ Data loaded successfully!")
    print(f"  - Total records: {len(df):,}")
    print(f"  - Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"  - Categories: {df['Category'].unique().tolist()}")
    print(f"  - Unique ASINs: {df['ASIN'].nunique():,}")
    
    return df

df = load_data(DATA_FILE)

# ============================================================================
# SECTION 1: IDENTIFY SALE EVENTS AND SALES SPIKES
# ============================================================================

print("\n" + "="*80)
print("SECTION 1: IDENTIFYING SALE EVENTS AND SALES SPIKES")
print("="*80)

def identify_sale_events(df, window_days=7, threshold_multiplier=1.5):
    """
    Identify sale events by detecting significant spikes in sales volume.
    
    Methodology:
    1. Calculate rolling average sales for each ASIN
    2. Identify days where sales exceed threshold (default: 1.5x rolling average)
    3. Group consecutive high-sales days into sale events
    4. Calculate spike magnitude as ratio of sale period to baseline
    
    Assumptions:
    - Sale events are characterized by sales spikes > 50% above baseline
    - Sale events last at least 1 day and up to 14 days
    - Baseline is calculated using 30-day rolling window excluding sale periods
    """
    sale_events = []
    
    for category in df['Category'].unique():
        cat_df = df[df['Category'] == category].copy()
        
        # Calculate daily total sales per category
        daily_sales = cat_df.groupby('Date')['Units_Sold'].sum().reset_index()
        daily_sales = daily_sales.sort_values('Date')
        
        # Calculate rolling average (30-day window)
        daily_sales['Rolling_Avg'] = daily_sales['Units_Sold'].rolling(
            window=30, min_periods=7, center=True
        ).mean()
        
        # Calculate rolling standard deviation
        daily_sales['Rolling_Std'] = daily_sales['Units_Sold'].rolling(
            window=30, min_periods=7, center=True
        ).std()
        
        # Identify spikes (sales > threshold * rolling average)
        daily_sales['Is_Spike'] = (
            daily_sales['Units_Sold'] > 
            (daily_sales['Rolling_Avg'] + threshold_multiplier * daily_sales['Rolling_Std'])
        )
        
        # Group consecutive spike days into events
        daily_sales['Event_Group'] = (
            (daily_sales['Is_Spike'] != daily_sales['Is_Spike'].shift()).cumsum()
        )
        
        # Calculate metrics for each potential event
        for event_id in daily_sales[daily_sales['Is_Spike']]['Event_Group'].unique():
            event_data = daily_sales[daily_sales['Event_Group'] == event_id]
            
            if len(event_data) >= 1:  # At least 1 day of spike
                event_start = event_data['Date'].min()
                event_end = event_data['Date'].max()
                event_duration = (event_end - event_start).days + 1
                
                # Calculate baseline (30 days before event)
                baseline_start = event_start - timedelta(days=30)
                baseline_data = daily_sales[
                    (daily_sales['Date'] >= baseline_start) & 
                    (daily_sales['Date'] < event_start)
                ]
                
                if len(baseline_data) > 0:
                    baseline_avg = baseline_data['Units_Sold'].mean()
                    event_avg = event_data['Units_Sold'].mean()
                    spike_multiplier = event_avg / baseline_avg if baseline_avg > 0 else 0
                    
                    sale_events.append({
                        'Category': category,
                        'Event_Start': event_start,
                        'Event_End': event_end,
                        'Duration_Days': event_duration,
                        'Baseline_Sales': baseline_avg,
                        'Event_Sales': event_avg,
                        'Spike_Multiplier': spike_multiplier,
                        'Total_Units_Sold': event_data['Units_Sold'].sum()
                    })
    
    sale_events_df = pd.DataFrame(sale_events)
    
    if len(sale_events_df) > 0:
        sale_events_df = sale_events_df.sort_values('Event_Start')
        print(f"\n✓ Identified {len(sale_events_df)} sale events across all categories")
        print(f"\nTop 10 Sale Events by Spike Magnitude:")
        print(sale_events_df.nlargest(10, 'Spike_Multiplier')[
            ['Category', 'Event_Start', 'Duration_Days', 'Spike_Multiplier', 'Total_Units_Sold']
        ].to_string(index=False))
    
    return sale_events_df

sale_events = identify_sale_events(df)

# Visualize sale events
def plot_sale_events(df, sale_events):
    """Create visualizations for sale events"""
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    
    for idx, category in enumerate(df['Category'].unique()):
        cat_df = df[df['Category'] == category].copy()
        daily_sales = cat_df.groupby('Date')['Units_Sold'].sum().reset_index()
        
        ax = axes[idx]
        ax.plot(daily_sales['Date'], daily_sales['Units_Sold'], 
                linewidth=1.5, alpha=0.7, label='Daily Sales')
        
        # Highlight sale events
        cat_events = sale_events[sale_events['Category'] == category]
        for _, event in cat_events.iterrows():
            ax.axvspan(event['Event_Start'], event['Event_End'], 
                      alpha=0.3, color='red', label='Sale Event' if idx == 0 else '')
        
        ax.set_title(f'{category} - Daily Sales with Sale Events Highlighted', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Units Sold', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/sale_events_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Sale events visualization saved to {OUTPUT_DIR}/sale_events_analysis.png")
    plt.close()

plot_sale_events(df, sale_events)

# ============================================================================
# SECTION 2: PRICE DISTRIBUTION AND SKU SEGMENTATION
# ============================================================================

print("\n" + "="*80)
print("SECTION 2: PRICE DISTRIBUTION AND SKU SEGMENTATION")
print("="*80)

def segment_skus(df):
    """
    Segment SKUs into 'Top Selling', 'Core', and 'Tail' subcategories.
    
    Methodology (Pareto-based segmentation):
    1. Calculate total sales volume per ASIN across entire period
    2. Sort ASINs by total sales volume (descending)
    3. Calculate cumulative sales percentage
    4. Top Selling: Top 20% of ASINs by volume (typically 80/20 rule)
    5. Core: Next 30% of ASINs (21-50%)
    6. Tail: Remaining 50% of ASINs (bottom 50%)
    
    Alternative approach considered: Revenue-based segmentation
    - Could also segment by revenue, but volume is more indicative of market share
    
    Assumptions:
    - Segmentation based on total units sold across entire period
    - Percentiles: Top 20%, Core 30%, Tail 50%
    """
    sku_segments = []
    
    for category in df['Category'].unique():
        cat_df = df[df['Category'] == category].copy()
        
        # Calculate total sales per ASIN
        asin_sales = cat_df.groupby('ASIN').agg({
            'Units_Sold': 'sum',
            'Revenue': 'sum',
            'Price': 'mean'
        }).reset_index()
        asin_sales = asin_sales.sort_values('Units_Sold', ascending=False)
        
        # Calculate cumulative percentage
        asin_sales['Cumulative_Units'] = asin_sales['Units_Sold'].cumsum()
        asin_sales['Cumulative_Pct'] = (
            asin_sales['Cumulative_Units'] / asin_sales['Units_Sold'].sum() * 100
        )
        
        # Segment based on cumulative percentage
        asin_sales['Segment'] = 'Tail'  # Default
        asin_sales.loc[asin_sales['Cumulative_Pct'] <= 20, 'Segment'] = 'Top Selling'
        asin_sales.loc[
            (asin_sales['Cumulative_Pct'] > 20) & 
            (asin_sales['Cumulative_Pct'] <= 50), 
            'Segment'
        ] = 'Core'
        
        # Add category info
        asin_sales['Category'] = category
        sku_segments.append(asin_sales)
        
        # Print summary
        print(f"\n{category} - SKU Segmentation:")
        segment_summary = asin_sales.groupby('Segment').agg({
            'ASIN': 'count',
            'Units_Sold': 'sum',
            'Revenue': 'sum'
        })
        segment_summary.columns = ['SKU_Count', 'Total_Units', 'Total_Revenue']
        segment_summary['Pct_of_SKUs'] = (
            segment_summary['SKU_Count'] / len(asin_sales) * 100
        )
        segment_summary['Pct_of_Volume'] = (
            segment_summary['Total_Units'] / asin_sales['Units_Sold'].sum() * 100
        )
        print(segment_summary)
    
    sku_segments_df = pd.concat(sku_segments, ignore_index=True)
    return sku_segments_df

sku_segments = segment_skus(df)

# Visualize price distribution and segmentation
def plot_price_distribution_and_segments(df, sku_segments):
    """Create visualizations for price distribution and SKU segments"""
    fig = plt.figure(figsize=(18, 12))
    
    # Price distribution by category
    ax1 = plt.subplot(2, 3, 1)
    for category in df['Category'].unique():
        cat_df = df[df['Category'] == category]
        ax1.hist(cat_df['Price'], bins=50, alpha=0.6, label=category, density=True)
    ax1.set_xlabel('Price ($)', fontsize=11)
    ax1.set_ylabel('Density', fontsize=11)
    ax1.set_title('Price Distribution by Category', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot of prices by category
    ax2 = plt.subplot(2, 3, 2)
    df.boxplot(column='Price', by='Category', ax=ax2)
    ax2.set_xlabel('Category', fontsize=11)
    ax2.set_ylabel('Price ($)', fontsize=11)
    ax2.set_title('Price Distribution (Box Plot)', fontsize=12, fontweight='bold')
    plt.suptitle('')  # Remove default title
    
    # Price by segment
    ax3 = plt.subplot(2, 3, 3)
    segment_price = sku_segments.groupby(['Category', 'Segment'])['Price'].mean().unstack()
    segment_price.plot(kind='bar', ax=ax3, width=0.8)
    ax3.set_xlabel('Category', fontsize=11)
    ax3.set_ylabel('Average Price ($)', fontsize=11)
    ax3.set_title('Average Price by Segment', fontsize=12, fontweight='bold')
    ax3.legend(title='Segment')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Sales volume by segment
    ax4 = plt.subplot(2, 3, 4)
    segment_volume = sku_segments.groupby(['Category', 'Segment'])['Units_Sold'].sum().unstack()
    segment_volume.plot(kind='bar', ax=ax4, width=0.8)
    ax4.set_xlabel('Category', fontsize=11)
    ax4.set_ylabel('Total Units Sold', fontsize=11)
    ax4.set_title('Total Sales Volume by Segment', fontsize=12, fontweight='bold')
    ax4.legend(title='Segment')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # SKU count by segment
    ax5 = plt.subplot(2, 3, 5)
    segment_count = sku_segments.groupby(['Category', 'Segment']).size().unstack()
    segment_count.plot(kind='bar', ax=ax5, width=0.8)
    ax5.set_xlabel('Category', fontsize=11)
    ax5.set_ylabel('Number of SKUs', fontsize=11)
    ax5.set_title('SKU Count by Segment', fontsize=12, fontweight='bold')
    ax5.legend(title='Segment')
    ax5.tick_params(axis='x', rotation=45)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # Revenue by segment
    ax6 = plt.subplot(2, 3, 6)
    segment_revenue = sku_segments.groupby(['Category', 'Segment'])['Revenue'].sum().unstack()
    segment_revenue.plot(kind='bar', ax=ax6, width=0.8)
    ax6.set_xlabel('Category', fontsize=11)
    ax6.set_ylabel('Total Revenue ($)', fontsize=11)
    ax6.set_title('Total Revenue by Segment', fontsize=12, fontweight='bold')
    ax6.legend(title='Segment')
    ax6.tick_params(axis='x', rotation=45)
    ax6.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/price_distribution_segmentation.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Price distribution and segmentation visualization saved")
    plt.close()

plot_price_distribution_and_segments(df, sku_segments)

# ============================================================================
# SECTION 3: PRICE TREND ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("SECTION 3: PRICE TREND ANALYSIS - WHICH CATEGORY IS GETTING MORE EXPENSIVE?")
print("="*80)

def analyze_price_trends(df):
    """
    Analyze price trends to determine which category is getting more expensive.
    
    Methodology:
    1. Calculate average price per category by year/month
    2. Compare price trends across time periods
    3. Distinguish between:
       - Existing SKUs getting more expensive (price inflation)
       - New SKUs being introduced at higher prices (portfolio shift)
    
    Assumptions:
    - Price changes > 5% are considered significant
    - New SKUs are those that appear for the first time in later periods
    """
    price_trends = []
    
    # Calculate monthly average prices by category
    monthly_prices = df.groupby(['Category', 'YearMonth'])['Price'].mean().reset_index()
    monthly_prices['Year'] = monthly_prices['YearMonth'].astype(str).str[:4].astype(int)
    monthly_prices['Month'] = monthly_prices['YearMonth'].astype(str).str[5:].astype(int)
    
    # Calculate year-over-year price change
    for category in df['Category'].unique():
        cat_monthly = monthly_prices[monthly_prices['Category'] == category].copy()
        cat_monthly = cat_monthly.sort_values(['Year', 'Month'])
        
        # Calculate price change
        cat_monthly['Price_Change_Pct'] = cat_monthly['Price'].pct_change() * 100
        
        # Year-over-year comparison
        for year in [2018, 2019]:
            year_data = cat_monthly[cat_monthly['Year'] == year]
            prev_year_data = cat_monthly[cat_monthly['Year'] == year - 1]
            
            if len(year_data) > 0 and len(prev_year_data) > 0:
                avg_price_current = year_data['Price'].mean()
                avg_price_previous = prev_year_data['Price'].mean()
                yoy_change = ((avg_price_current - avg_price_previous) / avg_price_previous) * 100
                
                price_trends.append({
                    'Category': category,
                    'Year': year,
                    'Avg_Price': avg_price_current,
                    'YoY_Change_Pct': yoy_change
                })
        
        print(f"\n{category} - Price Trend Summary:")
        print(f"  2017 Average Price: ${cat_monthly[cat_monthly['Year']==2017]['Price'].mean():.2f}")
        print(f"  2018 Average Price: ${cat_monthly[cat_monthly['Year']==2018]['Price'].mean():.2f}")
        print(f"  2019 Average Price: ${cat_monthly[cat_monthly['Year']==2019]['Price'].mean():.2f}")
    
    price_trends_df = pd.DataFrame(price_trends)
    
    # Analyze existing vs new SKUs
    print("\n" + "-"*80)
    print("Analyzing Existing SKUs vs New SKUs:")
    
    for category in df['Category'].unique():
        cat_df = df[df['Category'] == category].copy()
        
        # Identify SKUs that existed in 2017
        skus_2017 = set(cat_df[cat_df['Year'] == 2017]['ASIN'].unique())
        skus_2018 = set(cat_df[cat_df['Year'] == 2018]['ASIN'].unique())
        skus_2019 = set(cat_df[cat_df['Year'] == 2019]['ASIN'].unique())
        
        existing_skus_2018 = skus_2017.intersection(skus_2018)
        existing_skus_2019 = skus_2017.intersection(skus_2019)
        new_skus_2018 = skus_2018 - skus_2017
        new_skus_2019 = skus_2019 - skus_2017
        
        # Calculate average prices
        existing_2017_price = cat_df[
            (cat_df['Year'] == 2017) & (cat_df['ASIN'].isin(skus_2017))
        ]['Price'].mean()
        
        existing_2018_price = cat_df[
            (cat_df['Year'] == 2018) & (cat_df['ASIN'].isin(existing_skus_2018))
        ]['Price'].mean()
        
        existing_2019_price = cat_df[
            (cat_df['Year'] == 2019) & (cat_df['ASIN'].isin(existing_skus_2019))
        ]['Price'].mean()
        
        new_2018_price = cat_df[
            (cat_df['Year'] == 2018) & (cat_df['ASIN'].isin(new_skus_2018))
        ]['Price'].mean() if len(new_skus_2018) > 0 else 0
        
        new_2019_price = cat_df[
            (cat_df['Year'] == 2019) & (cat_df['ASIN'].isin(new_skus_2019))
        ]['Price'].mean() if len(new_skus_2019) > 0 else 0
        
        print(f"\n{category}:")
        print(f"  Existing SKUs (2017): {len(skus_2017):,}")
        print(f"  New SKUs in 2018: {len(new_skus_2018):,} (Avg Price: ${new_2018_price:.2f})")
        print(f"  New SKUs in 2019: {len(new_skus_2019):,} (Avg Price: ${new_2019_price:.2f})")
        print(f"  Existing SKU Price Change:")
        # Calculate percentage changes
        pct_change_2018 = ((existing_2018_price/existing_2017_price - 1)*100)
        pct_change_2019 = ((existing_2019_price/existing_2017_price - 1)*100)
        # Round to 0.0% if change is less than 0.1% (since prices are rounded to 2 decimals, 
        # changes < 0.1% are negligible when displayed as $X.XX)
        pct_change_2018_display = 0.0 if abs(pct_change_2018) < 0.1 else round(pct_change_2018, 1)
        pct_change_2019_display = 0.0 if abs(pct_change_2019) < 0.1 else round(pct_change_2019, 1)
        print(f"    2017 → 2018: ${existing_2017_price:.2f} → ${existing_2018_price:.2f} "
              f"({pct_change_2018_display:.1f}%)")
        print(f"    2017 → 2019: ${existing_2017_price:.2f} → ${existing_2019_price:.2f} "
              f"({pct_change_2019_display:.1f}%)")
    
    return price_trends_df, monthly_prices

price_trends_df, monthly_prices = analyze_price_trends(df)

# Visualize price trends
def plot_price_trends(monthly_prices, df):
    """Create visualizations for price trends"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Time series of average prices
    ax1 = axes[0, 0]
    for category in monthly_prices['Category'].unique():
        cat_data = monthly_prices[monthly_prices['Category'] == category].copy()
        cat_data = cat_data.sort_values(['Year', 'Month'])
        cat_data['Date'] = pd.to_datetime(cat_data['YearMonth'].astype(str))
        ax1.plot(cat_data['Date'], cat_data['Price'], marker='o', 
                linewidth=2, label=category, markersize=4)
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Average Price ($)', fontsize=12)
    ax1.set_title('Average Price Trend Over Time by Category', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Year-over-year price change
    ax2 = axes[0, 1]
    price_trends_summary = price_trends_df.groupby('Category')['YoY_Change_Pct'].mean().reset_index()
    bars = ax2.bar(price_trends_summary['Category'], price_trends_summary['YoY_Change_Pct'],
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax2.set_xlabel('Category', fontsize=12)
    ax2.set_ylabel('Average YoY Price Change (%)', fontsize=12)
    ax2.set_title('Average Year-over-Year Price Change', fontsize=13, fontweight='bold')
    ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom' if height > 0 else 'top')
    
    # Price distribution by year
    ax3 = axes[1, 0]
    years = sorted(df['Year'].unique())
    for year in years:
        year_data = df[df['Year'] == year]
        ax3.hist(year_data['Price'], bins=50, alpha=0.5, label=str(year), density=True)
    ax3.set_xlabel('Price ($)', fontsize=12)
    ax3.set_ylabel('Density', fontsize=12)
    ax3.set_title('Price Distribution Shift Over Years (All Categories)', fontsize=13, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Category comparison by year
    ax4 = axes[1, 1]
    yearly_avg = df.groupby(['Category', 'Year'])['Price'].mean().unstack()
    yearly_avg.plot(kind='bar', ax=ax4, width=0.8)
    ax4.set_xlabel('Category', fontsize=12)
    ax4.set_ylabel('Average Price ($)', fontsize=12)
    ax4.set_title('Average Price by Category and Year', fontsize=13, fontweight='bold')
    ax4.legend(title='Year')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/price_trends_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Price trends visualization saved")
    plt.close()

plot_price_trends(monthly_prices, df)

# ============================================================================
# BONUS SECTION: CONSUMER BEHAVIOR ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("BONUS SECTION: CONSUMER BEHAVIOR ANALYSIS")
print("="*80)

def analyze_consumer_behavior(df, sale_events, sku_segments):
    """
    Analyze consumer behavior patterns from the data.
    
    Key insights to explore:
    1. Price sensitivity by category
    2. Purchase timing patterns (seasonality, sale events)
    3. Brand loyalty vs price sensitivity
    4. Category-specific behaviors
    """
    print("\nConsumer Behavior Insights:")
    
    # 1. Price Elasticity Analysis
    print("\n1. Price Elasticity Analysis:")
    for category in df['Category'].unique():
        cat_df = df[df['Category'] == category].copy()
        
        # Calculate correlation between price and sales
        # Negative correlation suggests price sensitivity
        price_sales_corr = cat_df.groupby('ASIN').apply(
            lambda x: x['Price'].corr(x['Units_Sold'])
        ).mean()
        
        # Calculate average price change impact
        cat_df_sorted = cat_df.sort_values(['ASIN', 'Date'])
        cat_df_sorted['Price_Change'] = cat_df_sorted.groupby('ASIN')['Price'].pct_change()
        cat_df_sorted['Sales_Change'] = cat_df_sorted.groupby('ASIN')['Units_Sold'].pct_change()
        
        # Filter for significant price changes (>5%)
        significant_changes = cat_df_sorted[
            (cat_df_sorted['Price_Change'].abs() > 0.05) & 
            (cat_df_sorted['Sales_Change'].notna())
        ]
        
        if len(significant_changes) > 0:
            elasticity = significant_changes['Sales_Change'].mean() / significant_changes['Price_Change'].mean()
            print(f"   {category}:")
            print(f"     Average Price-Sales Correlation: {price_sales_corr:.3f}")
            print(f"     Estimated Price Elasticity: {elasticity:.2f}")
            if elasticity < -1:
                print(f"     → Highly price-sensitive (elastic)")
            elif elasticity < 0:
                print(f"     → Moderately price-sensitive")
            else:
                print(f"     → Price-insensitive (inelastic)")
    
    # 2. Sale Event Response
    print("\n2. Sale Event Response Analysis:")
    for category in df['Category'].unique():
        cat_events = sale_events[sale_events['Category'] == category]
        if len(cat_events) > 0:
            avg_spike = cat_events['Spike_Multiplier'].mean()
            print(f"   {category}:")
            print(f"     Average Sales Spike During Events: {avg_spike:.2f}x baseline")
            print(f"     → Consumers respond {'strongly' if avg_spike > 2 else 'moderately'} to promotions")
    
    # 3. Segment Behavior
    print("\n3. Segment-Specific Behavior:")
    for category in df['Category'].unique():
        cat_segments = sku_segments[sku_segments['Category'] == category]
        top_selling = cat_segments[cat_segments['Segment'] == 'Top Selling']
        tail = cat_segments[cat_segments['Segment'] == 'Tail']
        
        print(f"   {category}:")
        print(f"     Top Selling SKUs: {len(top_selling)} SKUs, "
              f"Avg Price: ${top_selling['Price'].mean():.2f}")
        print(f"     Tail SKUs: {len(tail)} SKUs, "
              f"Avg Price: ${tail['Price'].mean():.2f}")
        print(f"     → Price difference suggests {'premium positioning' if top_selling['Price'].mean() > tail['Price'].mean() else 'value positioning'} for top sellers")
    
    # 4. Seasonal Patterns
    print("\n4. Seasonal Purchase Patterns:")
    df['Month'] = df['Date'].dt.month
    monthly_sales = df.groupby(['Category', 'Month'])['Units_Sold'].sum().reset_index()
    
    for category in df['Category'].unique():
        cat_monthly = monthly_sales[monthly_sales['Category'] == category]
        peak_month = cat_monthly.loc[cat_monthly['Units_Sold'].idxmax(), 'Month']
        peak_sales = cat_monthly['Units_Sold'].max()
        avg_sales = cat_monthly['Units_Sold'].mean()
        
        print(f"   {category}:")
        print(f"     Peak Sales Month: {peak_month} ({peak_sales/avg_sales:.1f}x average)")
    
    return None

analyze_consumer_behavior(df, sale_events, sku_segments)

# ============================================================================
# ADDITIONAL DATA RECOMMENDATIONS
# ============================================================================

print("\n" + "="*80)
print("ADDITIONAL DATA RECOMMENDATIONS FOR PROMOTIONAL STRATEGY")
print("="*80)

print("""
To develop a comprehensive promotional strategy, the following additional data would be valuable:

1. COMPETITIVE DATA:
   - Competitor pricing for similar products
   - Market share data by brand/SKU
   - Competitor promotional calendars
   → Use: Benchmark pricing, identify competitive gaps, time promotions strategically

2. INVENTORY DATA:
   - Stock levels and inventory turnover
   - Warehouse capacity and fulfillment speed
   → Use: Ensure sufficient stock during promotions, avoid stockouts

3. MARKETING DATA:
   - Advertising spend and channels (PPC, display, social)
   - Promotional campaign details (discount %, duration, channels)
   - Customer acquisition cost (CAC)
   → Use: Calculate ROI of promotions, optimize marketing mix

4. CUSTOMER DATA:
   - Customer segments (new vs returning, demographics)
   - Purchase frequency and basket size
   - Customer lifetime value (CLV)
   → Use: Target promotions to high-value segments, personalize offers

5. PRODUCT ATTRIBUTES:
   - Product features, ratings, reviews
   - Brand information
   - Product lifecycle stage
   → Use: Understand which attributes drive sales, optimize product mix

6. EXTERNAL FACTORS:
   - Seasonal events, holidays, weather
   - Economic indicators
   - Industry trends
   → Use: Plan promotions around high-demand periods, adjust for external factors

7. CHANNEL DATA:
   - Sales by channel (Amazon, Walmart, etc.)
   - Channel-specific pricing and promotions
   → Use: Optimize cross-channel strategy, prevent channel conflict

8. PRICE HISTORY:
   - Historical promotional prices and discount depths
   - Price change frequency
   → Use: Understand optimal discount levels, avoid over-discounting
""")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

summary_stats = df.groupby('Category').agg({
    'ASIN': 'nunique',
    'Units_Sold': ['sum', 'mean'],
    'Revenue': ['sum', 'mean'],
    'Price': ['mean', 'std', 'min', 'max']
}).round(2)

print("\nOverall Statistics by Category:")
print(summary_stats)

# Save all results to CSV files
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

sale_events.to_csv(f'{OUTPUT_DIR}/sale_events.csv', index=False)
sku_segments.to_csv(f'{OUTPUT_DIR}/sku_segments.csv', index=False)
price_trends_df.to_csv(f'{OUTPUT_DIR}/price_trends.csv', index=False)
monthly_prices.to_csv(f'{OUTPUT_DIR}/monthly_prices.csv', index=False)

print(f"✓ Results saved to {OUTPUT_DIR}/ directory:")
print(f"  - sale_events.csv")
print(f"  - sku_segments.csv")
print(f"  - price_trends.csv")
print(f"  - monthly_prices.csv")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print("\nNext steps:")
print("1. Review the visualizations in the 'outputs' directory")
print("2. Review the supporting document for detailed findings")
print("3. Use the CSV files for further analysis if needed")

