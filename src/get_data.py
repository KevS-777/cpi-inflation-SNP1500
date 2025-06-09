# This file contains functions and methods that are used to get the raw data
from polygon import RESTClient
from get_data_package.get_stock_data import html_to_csv, get_ticker_detail_from_list, get_grouped_daily
from get_data_package.get_inflation_data import get_bls_data

#Gets the S&P 1500 data details: GICS sector, GICS Sub-Industry
#.txt files requested from Wikipedia API
snp500_df = html_to_csv('data/raw/List_of_S&P_500_companies(LargeCap).txt','List_of_S&P_500_companies(LargeCap)')
snp400_df = html_to_csv('data/raw/List_of_S&P_400_companies(MidCap).txt','List_of_S&P_400_companies(MidCap)')
snp600_df = html_to_csv('data/raw/List_of_S&P_600_companies(SmallCap).txt','List_of_S&P_600_companies(SmallCap)')

#Gets the overall stock market daily data -> Grouped Daily (Bars) to see overview of 2year trend 
#~520 requests at 5 requests/min = 104min = 1hrs 44min
grouped_daily_data = get_grouped_daily()

#Gets the individual details for S&P 1500 (Future Work)
# snp500_ticker_details = get_ticker_detail_from_list('data/raw/List_of_S&P_500_companies(LargeCap)(12-11-2024).csv','S&P500')
# snp400_ticker_details = get_ticker_detail_from_list('data/raw/List_of_S&P_400_companies(MidCap)(12-11-2024).csv','S&P400')
# snp600_ticker_details = get_ticker_detail_from_list('data/raw/List_of_S&P_600_companies(SmallCap)(12-11-2024).csv','S&P600')


"""Inflation data"""
#All items in U.S. city average, all urban consumers, not seasonally adjusted
series_id = ["CUUR0000SA0"]
#All items less food and energy in U.S. city average, all urban consumers, not seasonally adjusted
series_id2 = ["CUUR0000SA0L1E"]

bls_data = get_bls_data(series_id, 'inflation_data_all')
bls_data2 = get_bls_data(series_id2, 'inflation_data_less_food&energy')
#Resources
#CPI Concepts: https://www.bls.gov/opub/hom/cpi/concepts.htm#structure-and-classification 
#CPI Series ID codes: https://www.bls.gov/cpi/factsheets/cpi-series-ids.htm
#CPI DataFinder: https://data.bls.gov/dataQuery/find?fq=survey:%5Bcu%5D&s=popularity:D
#Calculating percentage changes: https://www.bls.gov/cpi/factsheets/calculating-percent-changes.htm 