# This file contains functions and methods that are used to clean and preprocess your raw data
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
import ast


"""STOCK DATA: S&P 1500 Composite"""
#S&P1500 Data (Wikipedia)
snp500df = pd.read_csv('data/raw/List_of_S&P_500_companies(LargeCap)(12-11-2024).csv')
snp500df['S&P_category'] = 'S&P500'
snp400df = pd.read_csv('data/raw/List_of_S&P_400_companies(MidCap)(12-11-2024).csv')
snp400df['S&P_category'] = 'S&P400'
snp600df = pd.read_csv('data/raw/List_of_S&P_600_companies(SmallCap)(12-11-2024).csv')
snp600df['S&P_category'] = 'S&P600'

snp1500df = pd.concat([snp500df, snp400df,snp600df], ignore_index=True)
snp1500df.to_csv('data/cleaned/List_of_S&P1500_companies.csv')
print(snp1500df)

"""STOCK DATA: grouped_daily_aggs"""
start_date = '2022-12-18' #end_date - timedelta(days =365*2 - 1)
end_date = '2024-12-16' #datetime.now().date()
grouped_agg_df = pd.read_csv(f'data/raw/grouped_daily_aggs_raw({start_date} to {end_date}).csv')

#Data Transformation of "timestamp" into date
grouped_agg_df['date'] = pd.to_datetime(grouped_agg_df['timestamp'], unit='ms')
print(grouped_agg_df.head())
print(grouped_agg_df.dtypes)

# Merge the two datasets based on matching 'Symbol' and 'ticker'
merged_df = pd.merge(grouped_agg_df, snp1500df, how="left", left_on="ticker", right_on="Symbol")

snp500df_set = set(snp500df['Symbol'])
snp400df_set = set(snp400df['Symbol'])
snp600df_set = set(snp600df['Symbol'])

def categorize_ticker(ticker):
    if ticker in snp500df_set:
        return 'S&P500'
    elif ticker in snp400df_set:
        return 'S&P400'
    elif ticker in snp600df_set:
        return 'S&P600'
    else:
        return np.nan

merged_df['S&P_category'] = merged_df['ticker'].apply(categorize_ticker)

#drop the NaN rows of companies not in the S&P1500
filtered_merged_df = merged_df.dropna(axis='index', how='any', subset=['S&P_category'.strip()])

#Re-naming column names
filtered_merged_df = filtered_merged_df.rename(columns={'GICS Sector': 'GICS_sector', 'GICS Sub-Industry': 'GICS_sub_industry', 'Date added': 'date_added', 'Founded':'founded'} )

# Keep only relevant columns
result = filtered_merged_df[[
    "ticker", "date", "open", "close", "high", "low", "volume", "vwap", "transactions",
    "GICS_sector", "GICS_sub_industry", "S&P_category" #, "date_added", "founded"
]]

print(result)

csv_file = f"grouped_daily_aggs_cleaned({start_date} to {end_date}).csv"
folder_path = 'data/cleaned'
file_path = os.path.join(folder_path, csv_file)
result.to_csv(file_path, index=False)
print(f'Downloaded: {file_path}')


"""Stock Data: Enriching data with Calculations"""
grouped_daily_aggs = pd.read_csv(f'data/cleaned/grouped_daily_aggs_cleaned({start_date} to {end_date}).csv')

#Add a calculation column of the price differences between open and close
grouped_daily_aggs['open_close_delta'] = round(grouped_daily_aggs['close']/grouped_daily_aggs['open'],4)

#Add a calculation column of the price differences between high and low
grouped_daily_aggs['price_daily_range'] = round(grouped_daily_aggs['high']-grouped_daily_aggs['low'],4)

#Average volume of shares per transaction
grouped_daily_aggs['volume_per_transaction'] = grouped_daily_aggs['volume']/grouped_daily_aggs['transactions']

#Average price per transaction
grouped_daily_aggs['price_per_transaction'] = grouped_daily_aggs['vwap']*grouped_daily_aggs['volume_per_transaction']

#Simple Moving Average
def add_sma(data, window_size: int):
    data = data.sort_values(by=['ticker','date'], ascending=True)
    data[f'vwap_sma_{window_size}'] = data.groupby('ticker')['vwap'].rolling(window=window_size, min_periods=1).mean().reset_index(level=0, drop=True)
    return data

grouped_daily_aggs = add_sma(grouped_daily_aggs, 5)
grouped_daily_aggs = add_sma(grouped_daily_aggs, 30)
grouped_daily_aggs = add_sma(grouped_daily_aggs, 100)

#Exponential Moving Average
def add_ema(data, window_size: int):
    data = data.sort_values(by=['ticker','date'], ascending=True)
    data[f'vwap_ema_{window_size}'] = data.groupby('ticker')['vwap'].ewm(span=window_size, min_periods=1, adjust=False).mean().reset_index(level=0, drop=True)
    return data

grouped_daily_aggs = add_ema(grouped_daily_aggs, 5)
grouped_daily_aggs = add_ema(grouped_daily_aggs, 30)
grouped_daily_aggs = add_ema(grouped_daily_aggs, 100)

#Download final enriched data 
csv_file = f"grouped_daily_aggs_enriched({start_date} to {end_date}).csv"
folder_path = 'data/enriched'
file_path = os.path.join(folder_path, csv_file)
grouped_daily_aggs.to_csv(file_path, index=False)
print(f'Downloaded: {file_path}')


"""INFLATION DATA"""
#DATA CLEANING
def clean_inflation_data(csv, csv_file_name):
    df = pd.read_csv(csv)

    #Sort by date chronologically
    df = df.sort_values(by=['year', 'period'], ascending=[True,True])

    df['calculations'] = df['calculations'].apply(ast.literal_eval)
    for key in df['calculations'][0]['pct_changes'].keys():
        df[f'pct_{key}_month'] = df['calculations'].apply(lambda x: float(x['pct_changes'][key]))

    #remove the non-essential columns
    df = df.drop(columns=['latest','footnotes', 'calculations'])

    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    #Introduces the "date" column of Month-Year
    df["date"] = pd.to_datetime(df["period"].str[1:]+"-01-"+ df["year"].astype(str), format="%m-%d-%Y")
    #Download to CSV (cleaned data)
    csv_file = csv_file_name + '_cleaned.csv'
    folder_path = 'data/cleaned'
    file_path = os.path.join(folder_path, csv_file)
    os.makedirs(folder_path, exist_ok = True)
    df.to_csv(file_path, index=False)
    print(f"cleaned data file downloaded: {csv_file}")

    return df

#All items in U.S. city average, all urban consumers, not seasonally adjusted
series_id = ["CUUR0000SA0"]
#All items less food and energy in U.S. city average, all urban consumers, not seasonally adjusted
series_id2 = ["CUUR0000SA0L1E"]

bls_data_cleaned = clean_inflation_data('data/raw/inflation_data_all_raw.csv', 'inflation_data_all')
bls_data2_cleaned = clean_inflation_data('data/raw/inflation_data_less_food&energy_raw.csv', 'inflation_data_less_food&energy')
