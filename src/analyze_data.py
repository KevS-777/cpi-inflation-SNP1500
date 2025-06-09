# This file contains functions and methods that are used to analyze data
from bs4 import BeautifulSoup
import requests
import json
from polygon import RESTClient
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time
from io import StringIO
from datetime import datetime, timedelta
import pprint
import os
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests


"""Import Stock Data"""
#Retreiving the stock data csv
start_date = '2022-12-18'#end_date - timedelta(days =365*2 - 1)
end_date = '2024-12-16'#datetime.now().date()
grouped_daily_aggs = pd.read_csv(f'data/enriched/grouped_daily_aggs_enriched({start_date} to {end_date}).csv')

"""Stock Data: Overview Descriptive Statistics"""
print(grouped_daily_aggs.describe())
grouped_daily_aggs.describe().to_csv('results/statistics/Stock_Overview_Summary_Statistics.csv')

snp500_stats = grouped_daily_aggs[grouped_daily_aggs['S&P_category'] == 'S&P500'].describe()
snp400_stats = grouped_daily_aggs[grouped_daily_aggs['S&P_category'] == 'S&P400'].describe()
snp600_stats = grouped_daily_aggs[grouped_daily_aggs['S&P_category'] == 'S&P600'].describe()
print(snp500_stats)
print(snp400_stats)
print(snp600_stats)
snp500_stats.to_csv('results/statistics/S&P500_Overview_Summary_Statistics.csv')
snp400_stats.to_csv('results/statistics/S&P400_Overview_Summary_Statistics.csv')
snp600_stats.to_csv('results/statistics/S&P600_Overview_Summary_Statistics.csv')

for sector in grouped_daily_aggs['GICS_sector'].unique():
    sector_stats = grouped_daily_aggs[grouped_daily_aggs['GICS_sector'] == sector]
    sector_stats.describe().to_csv(f'results/statistics/{sector}_Overview_Summary_Statistics.csv')
    print(sector_stats.describe())


"""Stock Data: Volume metrics"""
#Calculate the average trading volume difference between S&P500 compared to S&P400, S&P600
snp500_volume_mean = grouped_daily_aggs[grouped_daily_aggs['S&P_category'] == 'S&P500']['volume'].mean()
snp400_volume_mean = grouped_daily_aggs[grouped_daily_aggs['S&P_category'] == 'S&P400']['volume'].mean()
snp600_volume_mean = grouped_daily_aggs[grouped_daily_aggs['S&P_category'] == 'S&P600']['volume'].mean()

snp500_to_snp400_volume_ratio = round(snp500_volume_mean/snp400_volume_mean,2)
snp500_to_snp600_volume_ratio = round(snp500_volume_mean/snp600_volume_mean,2)
snp400_to_snp600_volume_ratio = round(snp400_volume_mean/snp600_volume_mean,2)

print(f"snp500_to_snp400_volume_ratio: {snp500_to_snp400_volume_ratio}")
print(f"snp500_to_snp600_volume_ratio: {snp500_to_snp600_volume_ratio}")
print(f"snp600_to_snp400_volume_ratio: {snp400_to_snp600_volume_ratio}")


#Count how many positive vs negative open_close_delta there is
pos_price_delta = grouped_daily_aggs[grouped_daily_aggs['open_close_delta']>1.0]
neg_price_delta = grouped_daily_aggs[grouped_daily_aggs['open_close_delta']<1.0]
zero_price_delta = grouped_daily_aggs[grouped_daily_aggs['open_close_delta']==1.0]

print('pos_price_delta\n', pos_price_delta.describe())
print('neg_price_delta\n', neg_price_delta.describe())
print('zero_price_delta\n', zero_price_delta.describe())

#Top 20 companies that are trading the most/least
trading_days = grouped_daily_aggs.groupby('ticker').size().reset_index(name='trading_days')
total_volume = grouped_daily_aggs.groupby('ticker').agg(total_volume = ('volume', 'sum'), GICS_sector=('GICS_sector','first'),GICS_sub_industry=('GICS_sub_industry','first'), vwap = ('vwap', 'mean'), transactions = ('transactions', 'mean')).reset_index()

normalized_data = pd.merge(total_volume, trading_days, on='ticker')
normalized_data['average_daily_volume'] = normalized_data['total_volume']/normalized_data['trading_days']
print(normalized_data)
top_25_avg_daily_volume = normalized_data.nlargest(25,'average_daily_volume')
bottom_25_avg_daily_volume = normalized_data.nsmallest(25,'average_daily_volume')
top_25_avg_daily_volume.to_csv('results/statistics/top_25_avg_daily_volume.csv')
bottom_25_avg_daily_volume.to_csv('results/statistics/bottom_25_avg_daily_volume.csv')

print("Top 25 Average Daily Volume\n", top_25_avg_daily_volume)
print("Bottom 25 Average Daily Volume\n", bottom_25_avg_daily_volume)

#Analyzing based on sectors
sector_data = normalized_data
sector_data = sector_data.groupby('GICS_sector').agg(total_companies = ('ticker', 'nunique'), total_volume = ('total_volume', 'sum'), average_daily_volume = ('average_daily_volume', 'mean'),vwap = ('vwap', 'mean'), transactions = ('transactions', 'mean')).reset_index()
sector_data = sector_data.sort_values(by='average_daily_volume',ascending=False)
sector_data.to_csv('results/statistics/VWAP&Avg_Daily_Volume_per_Company_bySector.csv', index = True)
print(sector_data)

def corr_heatmap(dataframe, title, file_path=''):
    plt.figure(figsize=(10, 8))
    sns.heatmap(dataframe, annot=True, cmap='coolwarm', fmt='.3f', linewidths=.5)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(file_path, format='png', dpi=300)
    print(f'Downloaded: {file_path}')
    plt.show()

#Correlation for Stock Data
corr_matrix_stock = grouped_daily_aggs.corr(numeric_only=True)
print(corr_matrix_stock)

#Pivot table of Sectors in each S&P
grouped_df = grouped_daily_aggs.groupby(['GICS_sector', 'GICS_sub_industry','S&P_category'])['ticker'].nunique().unstack(fill_value=0)
pivot_df = grouped_daily_aggs.pivot_table(
    index=['GICS_sector', 'GICS_sub_industry'],  # Rows
    columns='S&P_category',                      # Columns
    values='ticker',                             # Values (count of unique tickers)
    aggfunc='nunique',                           # Aggregate function (count unique values)
    fill_value=0                                 # Fill missing values with 0
)
pivot_df.to_csv('results/pivot_table/Sector_SubIndustry_S&P_count.csv', index = True)
print(pivot_df)

"""INFLATION/STOCK DATA TIMESERIES"""
bls_data_cleaned = pd.read_csv('data/cleaned/inflation_data_all_cleaned.csv')
bls_data2_cleaned = pd.read_csv('data/cleaned/inflation_data_less_food&energy_cleaned.csv')
print(bls_data_cleaned.describe())
print(bls_data2_cleaned.describe())


#Stock data transformed to a monthly aggregation
stock_df_monthly = grouped_daily_aggs
stock_df_monthly['returns'] = stock_df_monthly['vwap'].pct_change()
stock_df_monthly['date'] = pd.to_datetime(stock_df_monthly['date'])
print(stock_df_monthly.columns)
print(stock_df_monthly.dtypes)
stock_df_monthly = stock_df_monthly.groupby(by=['date']).agg(total_volume = ('volume', 'sum'),total_transactions = ('transactions', 'sum'), total_companies = ('ticker', 'nunique'), vwap = ('vwap', 'mean'), returns = ('returns', 'mean')).reset_index()
print(stock_df_monthly)
stock_df_monthly = stock_df_monthly.resample('ME', on='date').mean()
print(stock_df_monthly)
stock_df_monthly.index = stock_df_monthly.index.strftime('%Y-%m')
print(stock_df_monthly)

"""Core CPI Inflation (less food and energy)"""
#CPI inflation cleaning
inflation_df_monthly = pd.read_csv(f'data/cleaned/inflation_data_less_food&energy_cleaned.csv')
inflation_df_monthly['date'] = pd.to_datetime(inflation_df_monthly['date'])
print(inflation_df_monthly)
print(inflation_df_monthly.dtypes)
inflation_df_monthly['date'] = inflation_df_monthly['date'].dt.strftime('%Y-%m')
print(inflation_df_monthly)

#Merge the stock and CPI inflation data
merged_df = pd.merge(stock_df_monthly, inflation_df_monthly, how='outer', left_on='date', right_on='date')
print(merged_df)
correlation = merged_df['value'].corr(merged_df['vwap'])
print(correlation)

correlation_matrix = merged_df.corr(numeric_only=True)
print(correlation_matrix)
corr_heatmap(correlation_matrix, 'Correlation Matrix of Stock & CPI', 'results/visualizations_png/Corr_Matrix_Stock_CPI_Core(Heatmap).png')

#Lagging Correlation
lags = [1, 3, 6, 12]  # Lag periods you want to test
lagged_correlations = {}

for lag in lags:
    merged_df['value_lagged'] = merged_df['value'].shift(lag)  # Shift 'value' to create a lagged series
    print(merged_df['value_lagged'])
    df_lagged = merged_df.dropna(how='any').reset_index(drop=True)
    print("df_lagged", df_lagged)
    corr_matrix = df_lagged.corr(numeric_only=True)  # Drop NaN values due to shift
    lagged_correlations[lag] = corr_matrix['value_lagged']

lagged_correlations_df = pd.DataFrame.from_dict(lagged_correlations, orient='index')
print(lagged_correlations_df)
lag_corr_matrix = corr_heatmap(lagged_correlations_df, f'Lagged CPI Inflation Value (1/3/6/12 months)', 'results/visualizations_png/Lagged_Corr_Core(Heatmap).png')

#Granger Causality test. (Dependent variable, Independent variable)
granger_df = pd.merge(stock_df_monthly, inflation_df_monthly, how='inner', left_on='date', right_on='date')
print(granger_df.shape)
print("Granger Causality: Core CPI Inflation -> VWAP")
grangercausalitytests(granger_df[['vwap', 'value']], maxlag=6, verbose=True)
print("Granger Causality: VWAP -> Core CPI Inflation")
grangercausalitytests(granger_df[['value', 'vwap']], maxlag=6, verbose=True)
print("Granger Causality: Core CPI Inflation -> Total Volume")
grangercausalitytests(granger_df[['total_volume', 'value']], maxlag=6, verbose=True)
print("Granger Causality: Total Volume -> Core CPI Inflation")
grangercausalitytests(granger_df[['value', 'total_volume']], maxlag=6, verbose=True)
print("Granger Causality: Core CPI Inflation -> Total Transactions")
grangercausalitytests(granger_df[['total_transactions', 'value']], maxlag=6, verbose=True)
print("Granger Causality: Total Transactions -> Core CPI Inflation")
grangercausalitytests(granger_df[['value', 'total_transactions']], maxlag=6, verbose=True)



"""CPI Inflation (all)"""
#CPI inflation cleaning
inflation_df_monthly = pd.read_csv(f'data/cleaned/inflation_data_all_cleaned.csv')
inflation_df_monthly['date'] = pd.to_datetime(inflation_df_monthly['date'])
print(inflation_df_monthly)
print(inflation_df_monthly.dtypes)
inflation_df_monthly['date'] = inflation_df_monthly['date'].dt.strftime('%Y-%m')
print(inflation_df_monthly)

#Merge the stock and CPI inflation data
merged_df_all = pd.merge(stock_df_monthly, inflation_df_monthly, how='outer', left_on='date', right_on='date')
print(merged_df_all)
correlation = merged_df_all['value'].corr(merged_df_all['vwap'])
print(correlation)

correlation_matrix = merged_df_all.corr(numeric_only=True)
print(correlation_matrix)
corr_heatmap(correlation_matrix, 'Correlation Matrix of Stock & CPI', 'results/visualizations_png/Corr_Matrix_Stock_CPI_all(Heatmap).png')

#Lagging Correlation
lags = [1, 3, 6, 12]  # Lag periods you want to test
lagged_correlations = {}

for lag in lags:
    merged_df_all['value_lagged'] = merged_df_all['value'].shift(lag)  # Shift 'value' to create a lagged series
    print(merged_df_all['value_lagged'])
    df_lagged = merged_df_all.dropna(how='any').reset_index(drop=True)
    print("df_lagged", df_lagged)
    corr_matrix = df_lagged.corr(numeric_only=True)  # Drop NaN values due to shift
    lagged_correlations[lag] = corr_matrix['value_lagged']

lagged_correlations_df = pd.DataFrame.from_dict(lagged_correlations, orient='index')
print(lagged_correlations_df)
lag_corr_matrix = corr_heatmap(lagged_correlations_df, f'Lagged CPI Inflation Value (1/3/6/12 months)', 'results/visualizations_png/Lagged_Corr_All(Heatmap).png')


granger_df = pd.merge(stock_df_monthly, inflation_df_monthly, how='inner', left_on='date', right_on='date')
print(granger_df)
print("Granger Causality: CPI Inflation -> VWAP")
grangercausalitytests(granger_df[['vwap', 'value']], maxlag=6, verbose=True)
print("Granger Causality: VWAP -> CPI Inflation")
grangercausalitytests(granger_df[['value', 'vwap']], maxlag=6, verbose=True)
print("Granger Causality: CPI Inflation -> Total Volume")
grangercausalitytests(granger_df[['total_volume', 'value']], maxlag=6, verbose=True)
print("Granger Causality: Total Volume -> CPI Inflation")
grangercausalitytests(granger_df[['value', 'total_volume']], maxlag=6, verbose=True)
print("Granger Causality: CPI Inflation -> Total Transactions")
grangercausalitytests(granger_df[['total_transactions', 'value']], maxlag=6, verbose=True)
print("Granger Causality: Total Transactions -> CPI")
grangercausalitytests(granger_df[['value', 'total_transactions']], maxlag=6, verbose=True)
