""" Inflation data
https://www.bls.gov/developers/, https://www.bls.gov/help/hlpforma.htm#AP 
"""

import requests
import json
import pandas as pd
import os
import matplotlib.pyplot as plt


#API endpoint
api_key = "API_KEY_HERE"

def get_bls_data(series_id, csv_file_name =''):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    
    #Payload
    payload = {
        "seriesid": series_id,  # List of one or more time series IDs
        "startyear": "2005",          # Start year for the data
        "endyear": "2025",            # End year for the data
        "catalog": False,              # Include metadata about the series
        "calculations": True,         # Include additional calculations
        "annualaverage": False,        # Include annual averages
        "aspects": False,              # Include aspects data
        "registrationkey": api_key    # Your unique API key
    }
    
    response = requests.post(url, headers={"Content-type": "application/json"}, data=json.dumps(payload))

    if response.status_code == 200:
        inflation_data = response.json()
        print("Request succeeded")
    else:
        print(f"Error: {response.status_code}, {response.text}")


    #Pandas data frame
    results_data = inflation_data['Results']['series'][0]['data']
    df = pd.DataFrame(results_data)

    #Download to CSV (raw data)
    csv_file = csv_file_name + '_raw.csv'
    folder_path = 'data/raw'
    file_path = os.path.join(folder_path, csv_file)
    df.to_csv(file_path, index=False)
    print(f"raw data file downloaded: {file_path}")
    return df