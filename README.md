# E-commerce Price Elasticity Analysis

## Case Study: Conglomerate Inc - Promotional Strategy Analysis

This project analyzes price elasticity and promotional effectiveness for Conglomerate Inc across three product categories (Diapers, Headphones, and Breakfast Cereals) on Amazon from 2017-2019.

**Analysis Period:** 2017-2019  
**Categories:** Diapers, Headphones, Breakfast Cereals  
**Platform:** Amazon

## Project Structure

```
Ecommerce/
├── ecom-elasticity-data1.tsv          # Input data file
├── analysis_notebook.py                # Python script version
├── Analysis.ipynb                     # Jupyter notebook version
├── Supporting_Document.md             # Executive summary and findings
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### Step 1: Install Python Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- pandas (data manipulation)
- numpy (numerical computing)
- matplotlib (visualization)
- seaborn (statistical visualization)
- jupyter (for notebook interface)

### Step 2: Verify Installation

```bash
python -c "import pandas, numpy, matplotlib, seaborn; print('All packages installed successfully!')"
```

## Running the Analysis

### Option 1: Run Python Script (Recommended for Quick Execution)

```bash
python analysis_notebook.py
```

This will:
- Load and process the data
- Perform all analyses
- Generate visualizations in the `outputs/` directory
- Save results as CSV files

### Option 2: Use Jupyter Notebook (Recommended for Interactive Analysis)

1. **Start Jupyter Notebook:**
   ```bash
   jupyter notebook
   ```
   This will open Jupyter in your web browser.

2. **Open the Notebook:**
   - Click on `CommerceIQ_Analysis.ipynb`
   - Run cells sequentially (Shift + Enter) or run all cells

3. **Benefits of Notebook:**
   - Interactive exploration
   - Modify parameters easily
   - See results inline
   - Add your own analysis cells

## Output Files

After running the analysis, you'll find:

### Visualizations (in `outputs/` directory):
- `sale_events_analysis.png` - Sale events identified and visualized
- `price_distribution_segmentation.png` - Price analysis and SKU segmentation
- `price_trends_analysis.png` - Price trend analysis over time

### Data Files (in `outputs/` directory):
- `sale_events.csv` - All identified sale events with metrics
- `sku_segments.csv` - SKU segmentation results
- `price_trends.csv` - Price trend analysis results
- `monthly_prices.csv` - Monthly average prices by category

## Analysis Sections

The analysis covers:

1. **Section 1: Sale Events Identification**
   - Identifies promotional events
   - Calculates sales spike magnitudes
   - Visualizes sale patterns

2. **Section 2: Price Distribution & SKU Segmentation**
   - Analyzes price distributions
   - Segments SKUs into Top Selling, Core, and Tail
   - Provides methodology explanation

3. **Section 3: Price Trend Analysis**
   - Determines which category is getting more expensive
   - Distinguishes existing SKU price changes vs new SKU introductions
   - Year-over-year comparisons

4. **Bonus: Consumer Behavior Analysis**
   - Price elasticity analysis
   - Promotional response patterns
   - Seasonal purchase behaviors
   - Consumer behavior reasoning

5. **Additional Data Recommendations**
   - Suggests additional data sources
   - Explains how to use them for promotional strategy

## Customization

### Adjusting Analysis Parameters

You can modify these parameters in the code:

1. **Sale Event Detection:**
   ```python
   threshold_multiplier = 1.5  # Adjust sensitivity (default: 1.5)
   window_days = 30            # Rolling window size (default: 30)
   ```

2. **SKU Segmentation:**
   ```python
   # Modify percentiles in segment_skus() function
   # Top Selling: Cumulative_Pct <= 20
   # Core: 20 < Cumulative_Pct <= 50
   # Tail: Cumulative_Pct > 50
   ```

3. **Price Trend Analysis:**
   ```python
   # Modify significance threshold
   significant_change_threshold = 0.05  # 5% change considered significant
   ```

## Troubleshooting

### Common Issues

1. **Import Errors:**
   ```bash
   pip install --upgrade pandas numpy matplotlib seaborn jupyter
   ```

2. **File Not Found Error:**
   - Ensure `ecom-elasticity-data1.tsv` is in the same directory as the script
   - Check file name matches exactly (case-sensitive)

3. **Memory Issues (Large Dataset):**
   - The dataset has ~462,000 rows
   - If you encounter memory issues, process by category:
     ```python
     # Process one category at a time
     df_diapers = df[df['Category'] == 'Diapers']
     ```

4. **Visualization Not Displaying:**
   - Check that `outputs/` directory is created
   - Verify matplotlib backend is working:
     ```python
     import matplotlib
     print(matplotlib.get_backend())
     ```

## Understanding the Results

### Sale Events
- **Spike Multiplier:** How many times higher sales are during event vs baseline
- **Duration:** Length of promotional event in days
- **Baseline Sales:** Average sales in 30 days before event

### SKU Segmentation
- **Top Selling:** Top 20% of SKUs by volume (typically 70-80% of sales)
- **Core:** Next 30% of SKUs (steady performers)
- **Tail:** Bottom 50% of SKUs (long-tail products)

### Price Trends
- **YoY Change:** Year-over-year percentage change in average price
- **Existing SKUs:** Products present throughout the period
- **New SKUs:** Products introduced in 2018 or 2019

## Next Steps

1. **Review Visualizations:**
   - Open images in `outputs/` directory
   - Compare with findings in `Supporting_Document.md`

2. **Explore Data:**
   - Open CSV files in Excel or Python
   - Filter by category or date range
   - Create additional custom analyses

3. **Read Supporting Document:**
   - `Supporting_Document.md` contains:
     - Executive summary
     - Detailed findings
     - Methodology explanations
     - Recommendations

4. **Customize Analysis:**
   - Modify parameters for your needs
   - Add additional analysis sections
   - Create custom visualizations

## Support

For questions or issues:
1. Check the code comments (extensive documentation included)
2. Review the Supporting Document for methodology
3. Examine the output CSV files for detailed results


---

**Happy Analyzing! 🚀**

