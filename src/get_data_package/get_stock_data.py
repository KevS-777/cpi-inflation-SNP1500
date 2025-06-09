# This file contains functions and methods that are used to get the raw data
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
import os
import numpy as np

"""Parsing the list of S&P 500 companies from Wikipedia API: 
https://en.wikipedia.org/api/rest_v1/#/Page%20content/get_page_html__title_
Use the API to download the .txt file
"""

#Load the downloaded .txt file of the HTML content
def html_to_csv(data, file_name=""):
    with open(data, 'r') as file:
        html_data = file.read()
        html_file = StringIO(html_data)
    #HTML into a Panda dataframe
    dfs = pd.read_html(html_file)
    df = dfs[0]
    print(df.head())

    csv_file = f"{file_name}({datetime.today().strftime('%m-%d-%Y')}).csv"
    folder_path = 'data/raw'
    file_path = os.path.join(folder_path, csv_file)
    df.to_csv(file_path, index=False)
    print("Downloaded: ", file_path)
    return df

"""Polygon.io
Stock Data: Ticker details
ticker, name, market_cap, total_employee, share_class_shares_outstanding, weighted_shares_outstanding
1500 requests (Companies) = 5hrs"""
#Pass the API URL to the get function
api_key = os.getenv("POLYGON_API_KEY") #Replace the api_key variable with your API key string
client = RESTClient(api_key)  # POLYGON_API_KEY environment variable is used

def get_ticker_detail_from_list(csv_file, list_name=""):
    print('Ticker Detail API request started')
    count = 0
    data_frame = pd.read_csv(csv_file)
    ticker_list = data_frame['Symbol'].tolist()
    agg_dataframe = data_frame
    for ticker_symbol in ticker_list:
        try:
            ticker_details = requests.get(f"https://api.polygon.io/v3/reference/tickers/{ticker_symbol}?apiKey=QHrv703qa2x36_QjI1Igzybhv5nu9D1b")
            ticker_dict = ticker_details.json()

            for key in ['market_cap', 'share_class_shares_outstanding', 'weighted_shares_outstanding', 'total_employees', 'sic_code','description', 'list_date']:
                try: 
                    agg_dataframe.loc[agg_dataframe['Symbol'] == ticker_symbol, key] = ticker_dict['results'].get(key, np.nan)
                    
                except KeyError as e:
                    raise KeyError
            count+=1
            print(f"Requested: ticker_details; Ticker: {ticker_symbol}; Count: {count}")
        except Exception as e:
            print(f"Error: {ticker_details.status_code}, {ticker_details.text}, Ticker: {ticker_symbol}; Count: {count}")
        time.sleep(12)
     
    csv_file = f"{list_name}_ticker_details_raw({datetime.today().strftime('%m-%d-%Y')}).csv"
    folder_path = 'data/raw'
    file_path = os.path.join(folder_path, csv_file)
    agg_dataframe.to_csv(file_path, index=False)
    print(agg_dataframe)
    print("Finished all downloads for ticker detail!")
    return agg_dataframe


"""Polygon.io
Getting Grouped Daily (Bars) to see overview of 2year trend 
~520 requests at 5 requests/min = 104min = 1hrs 44min (Only weekdays)
"""
def get_grouped_daily():
    #Get the end and start range to pull the data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days =365*2 - 1)
    print(f"Start date: {start_date}; End date: {end_date}")
    #Get the list of dates from the past 2 years.
    dates =  [(start_date + timedelta(days = day)) for day in range((end_date - start_date).days + 1)]
    #Filters for only weekdays when stock market would be open
    weekdays = [date for date in dates if date.weekday() <5] #2022-12-02 to 2021-11-29,weekdays
    df = pd.DataFrame({"Date": weekdays})

    all_data = pd.DataFrame()
    count = 0
    #Loop through each date in the weekdays list
    for date in weekdays:
        grouped = client.get_grouped_daily_aggs(date)
        data = [{
            'ticker': obj.ticker,
            'open': obj.open,
            'close': obj.close,
            'high': obj.high,
            'low': obj.low,
            'volume': obj.volume,
            'vwap': obj.vwap,
            'transactions': obj.transactions,
            'timestamp': obj.timestamp
            } for obj in grouped]
        df = pd.DataFrame(data)
        # print(df)
        all_data = pd.concat([all_data,df],ignore_index=True)
        
        time.sleep(12)
        count+=1
        print("Requested: grouped_daily; Date:", date ,"Count:", count)

    csv_file = f"grouped_daily_aggs_raw({start_date} to {end_date}).csv"
    folder_path = 'data/raw'
    file_path = os.path.join(folder_path, csv_file)
    all_data.to_csv(file_path, index=False)
    print(all_data)
    print("Finished all downloads for grouped_daily_aggs!")
    return all_data


