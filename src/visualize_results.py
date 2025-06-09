# This file contains functions and methods that are used to visualize the results
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns
import analyze_data


"""Data Visualization"""
grouped_daily_aggs = pd.read_csv(f'data/enriched/grouped_daily_aggs_enriched({analyze_data.start_date} to {analyze_data.end_date}).csv')

# Create a heatmap to visualize the correlations
plt.figure(figsize=(12,12))
sns.heatmap(analyze_data.corr_matrix_stock, annot=True, cmap='coolwarm', linewidths=.5, linecolor='white', fmt='.3f')
plt.title('Correlation Heatmap of Stock Data')
plt.tight_layout()
plt.savefig('results/visualizations_png/Corr_Matrix_Stocks.png', format='png',dpi=300)
print("Downloaded: results/visualizations_png/Corr_Matrix_Stocks.png")

#Seaborn lineplot of VWAP
sns.set_theme(style='darkgrid')
plt.figure(figsize=(10,6))
# sns.lineplot(x='date', y='open', data = grouped_daily_aggs[grouped_daily_aggs['ticker'] == 'NVDA'], label ='Open', color='blue')
# sns.lineplot(x='date', y='close', data = grouped_daily_aggs[grouped_daily_aggs['ticker'] == 'NVDA'], label ='Close', color='red')
sns.lineplot(x='date', y='vwap', data = grouped_daily_aggs, hue='GICS_sector')
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Stock Prices (VWAP) by GICS Sector')
plt.xticks(rotation=90, fontsize = 2)
plt.tight_layout()
plt.savefig('results/visualizations_png/VWAP_by_Sector_Lineplot.png', format='png',dpi=300)
print('Downloaded: results/visualizations_png/VWAP_by_Sector_Lineplot.png')

#Seaborn lineplot of VWAP
sns.set_theme(style='darkgrid')
plt.figure(figsize=(10,6))
sns.lineplot(x='date', y='vwap', data = grouped_daily_aggs, hue='S&P_category')
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Stock Prices (VWAP) by S&P Category')
plt.xticks(rotation=90, fontsize = 2)
plt.tight_layout()
plt.savefig('results/visualizations_png/VWAP_by_S&P_Lineplot.png', format='png',dpi=300)
print('Downloaded: results/visualizations_png/VWAP_by_S&P_Lineplot.png')

#Volume by Sector
sns.set_theme(style='darkgrid')
plt.figure(figsize=(10,6))
sns.lineplot(x='date', y='volume', data = grouped_daily_aggs, hue='GICS_sector')
plt.xlabel('Date')
plt.ylabel('Volume')
plt.title('Stock Volume by GICS Sector')
plt.xticks(rotation=90, fontsize=2)
plt.tight_layout()
plt.savefig('results/visualizations_png/Volume_by_Sector_Lineplot.png', format='png', dpi=300)
print('Downloaded: results/visualizations_png/Volume_by_Sector_Lineplot.png')

#Volume by S&P
sns.set_theme(style='darkgrid')
plt.figure(figsize=(10,6))
sns.lineplot(x='date', y='volume', data = grouped_daily_aggs, hue='S&P_category')
plt.xlabel('Date')
plt.ylabel('Volume')
plt.title('Stock Volume by S&P Category')
plt.xticks(rotation=90, fontsize=2)
plt.tight_layout()
plt.savefig('results/visualizations_png/Volume_by_S&P_Lineplot.png', format='png', dpi=300)
print('Downloaded: results/visualizations_png/Volume_by_S&P_Lineplot.png')

# Scatter plot of VWAP vs Avg_daily_volume
plt.figure(figsize=(10, 6))
sns.scatterplot(x='average_daily_volume', y='vwap', hue='GICS_sector', size='total_volume', sizes=(50, 1500), alpha=0.5,  data=analyze_data.sector_data)

plt.title('VWAP vs Average Daily Volume by Sector', fontsize=16)
plt.xlabel('Average Daily Volume', fontsize=14)
plt.ylabel('VWAP', fontsize=14)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('results/visualizations_png/VWAP&AvgDailyVol_by_Sector_Scatterplot.png', format='png', dpi=300)
print('Downloaded: results/visualizations_png/VWAP&AvgDailyVol_by_Sector_Scatterplot.png')

#Stack bar plot of count of Sectors in each S&P
grouped_df = grouped_daily_aggs.groupby(['GICS_sector', 'S&P_category'])['ticker'].nunique().unstack(fill_value=0)
grouped_df['total_counts'] = grouped_df['S&P500'] + grouped_df['S&P400']+grouped_df['S&P600']
grouped_df = grouped_df[['S&P500', 'S&P400', 'S&P600', 'total_counts']]
grouped_df = grouped_df.sort_values(by='total_counts', ascending=False)
grouped_df.to_csv('results/statistics/Count_of_Companies_bySector&S&P.csv')
print(grouped_df)
grouped_df = grouped_df.drop(columns=['total_counts'])
ax = grouped_df.plot(kind='bar', stacked=True, figsize=(14, 10))
plt.title('Compositional Breakdown of GICS by S&P Category')
plt.xlabel('GCIS Sector')
plt.ylabel('Number of Companies')
plt.xticks(rotation=45, ha ='right')
plt.legend(title='S&P Category')

# Add labels for each bar
for i, p in enumerate(ax.patches):
    count = int(p.get_height())  # Get the number of tickers (count) in each section
    x_center = p.get_x() + p.get_width() / 2
    y_center = p.get_y() + p.get_height() / 2
    
    ax.text(x_center, y_center, f'{count}', ha='center', va='center', fontsize=8, color='black')
plt.tight_layout()
plt.savefig('results/visualizations_png/Num_of_Companies_by_SectorS&P_(Stacked_Barplot).png', format='png', dpi=300)
print('Downloaded: results/visualizations_png/Num_of_Companies_by_SectorS&P_(Stacked_Barplot).png')


"""INFLATION DATA"""
#Seaborn lineplot of Core CPI Inflation
sns.set_theme(style='darkgrid')
plt.figure(figsize=(10,6))
sns.lineplot(x='date', y='value', data = analyze_data.merged_df, color = 'orange')
plt.xlabel('Date')
plt.ylabel('CPI')
plt.title('Core CPI Inflation (Less Food&Energy)')
plt.xticks(rotation=90, fontsize = 3)
plt.tight_layout()
plt.savefig('results/visualizations_png/Core_CPI_Inflation(Lineplot).png', format='png',dpi=300)
print('Downloaded: results/visualizations_png/Core_ CPI_Inflation(Lineplot).png')

#Seaborn lineplot of CPI Inflation all
sns.set_theme(style='darkgrid')
plt.figure(figsize=(10,6))
sns.lineplot(x='date', y='value', data = analyze_data.merged_df_all, color = 'blue')
plt.xlabel('Date')
plt.ylabel('CPI')
plt.title('CPI Inflation')
plt.xticks(rotation=90, fontsize = 3)
plt.tight_layout()
plt.savefig('results/visualizations_png/CPI_Inflation_all(Lineplot).png', format='png',dpi=300)
print('Downloaded: results/visualizations_png/CPI_Inflation_all(Lineplot).png')

#Seaborn lineplot of CPI Inflation all and Core CPI Inflation
sns.set_theme(style='darkgrid')
plt.figure(figsize=(10,6))
sns.lineplot(x='date', y='value', data = analyze_data.merged_df, color = 'orange', label='CPI Inflation Core')
sns.lineplot(x='date', y='value', data = analyze_data.merged_df_all, color = 'blue', label='CPI Inflation All')
plt.xlabel('Date')
plt.ylabel('CPI')
plt.title('Core & All CPI Inflation')
plt.xticks(rotation=90, fontsize = 3)
plt.tight_layout()
plt.savefig('results/visualizations_png/Core&All_CPI_Inflation(Lineplot).png', format='png',dpi=300)
print('Downloaded: results/visualizations_png/Core&All_CPI_Inflation_all(Lineplot).png')


def inflation_line_chart(df, file_name ="", file_name2 = ""):
    # Plot 'value' and percentage changes over time
    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], df["pct_1_month"], label="1-Month % Change", marker="o")
    plt.plot(df["date"], df["pct_3_month"], label="3-Month % Change", marker="o")
    plt.plot(df["date"], df["pct_6_month"], label="6-Month % Change", marker="o")
    plt.plot(df["date"], df["pct_12_month"], label="12-Month % Change", marker="o")

    # Customize plot
    plt.title("CPI Value and Percentage Changes Over Time")
    plt.xlabel("Date")
    plt.ylabel("Value / % Change")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=90, fontsize=2)
    plt.tight_layout()
    plt.savefig(file_name, format='png',dpi=300)
    print(f'Downloaded: {file_name}')
    plt.show()

    #Histogram for frequency of bins
    df['pct_1_month'].plot(kind='hist', bins=[-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1])
    plt.title("CPI Value (1-month-percentage change) Historgram")
    plt.xlabel("CPI index")
    plt.ylabel("Frequency")
    plt.legend()
    plt.savefig(file_name2, format='png',dpi=300)
    print(f'Downloaded: {file_name2}')
    plt.show()

bls_data_cleaned = pd.read_csv('data/cleaned/inflation_data_all_cleaned.csv')
bls_data2_cleaned = pd.read_csv('data/cleaned/inflation_data_less_food&energy_cleaned.csv')
inflation_line_chart(bls_data_cleaned, 'results/visualizations_png/CPI_percentage_change(Lineplot).png', 'results/visualizations_png/CPI_percentage_change(historgram).png')
inflation_line_chart(bls_data2_cleaned, 'results/visualizations_png/CPI_Core_percentage_change(Lineplot).png', 'results/visualizations_png/CPI_Core_percentage_change(historgram).png')


# Create a dual y-axis plot (Core CPI)
fig, ax1 = plt.subplots(figsize=(10, 6))

stock_cpi_df = analyze_data.merged_df
stock_cpi_df = stock_cpi_df.dropna(how='any')
# Plot CPI on the primary y-axis
sns.lineplot(x='date', y='value', data=stock_cpi_df, ax=ax1, color='orange', label='Core CPI Inflation', legend=False)
ax1.set_ylabel('CPI Inflation', color='orange')
ax1.tick_params(axis='y', labelcolor='orange')
plt.xticks(rotation=90, fontsize = 6)

# Create a second y-axis
ax2 = ax1.twinx()

# Plot VWAP on the secondary y-axis
sns.lineplot(x='date', y='vwap', data=stock_cpi_df, ax=ax2, color='green', label='VWAP', legend=False)
ax2.set_ylabel('VWAP (Volume Weighted Average Price)', color='green')
ax2.tick_params(axis='y', labelcolor='green')
plt.title('Core CPI Inflation vs VWAP')

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles = handles1 + handles2
labels = labels1 + labels2
ax1.legend(handles, labels, loc="upper left")

plt.savefig('results/visualizations_png/Stock&CPI_Inflation_core(DualPlot).png', format='png',dpi=300)
print('Downloaded: results/visualizations_png/Stock&CPI_Inflation_core(DualPlot).png')
plt.show()


# Create a dual y-axis plot (CPI all)
fig, ax1 = plt.subplots(figsize=(10, 6))

stock_cpi_df = analyze_data.merged_df_all
stock_cpi_df = stock_cpi_df.dropna(how='any')
# Plot CPI on the primary y-axis
sns.lineplot(x='date', y='value', data=stock_cpi_df, ax=ax1, color='blue', label='CPI Inflation', legend=False)
ax1.set_ylabel('CPI Inflation', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
plt.xticks(rotation=90, fontsize = 6)

# Create a second y-axis
ax2 = ax1.twinx()

# Plot VWAP on the secondary y-axis
sns.lineplot(x='date', y='vwap', data=stock_cpi_df, ax=ax2, color='green', label='VWAP', legend=False)
ax2.set_ylabel('VWAP (Volume Weighted Average Price)', color='green')
ax2.tick_params(axis='y', labelcolor='green')
plt.title('CPI Inflation vs VWAP')

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles = handles1 + handles2
labels = labels1 + labels2
ax1.legend(handles, labels, loc="upper left")

plt.savefig('results/visualizations_png/Stock&CPI_Inflation_all(DualPlot).png', format='png',dpi=300)
print('Downloaded: results/visualizations_png/Stock&CPI_Inflation_all(DualPlot).png')
plt.show()

