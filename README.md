[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/7A__rrid)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=17100116&assignment_repo_type=AssignmentRepo)
# Tracking Inflation’s Impact on the S&P1500
This guide will walkthrough how to collect the data from the various sources and how to run the code.
The final report can be found [here](https://drive.google.com/file/d/11lCGiNewTaIcPMLgA5LfXQaYbnT2EfLJ/view?usp=drive_link) | Final Project Google drive can be found [here](https://drive.google.com/drive/folders/1UD2iVDtP-BZ1qiWx2lI_Wzdq15ZfsP8b?usp=drive_link)


# Quick Start Guide
## Pre-loaded Data
The research data is readily available for download at this [Google Drive](https://drive.google.com/drive/folders/1E0GSEokzQHyBK_ihJaulpP_-m3YPIYnu?usp=sharing). Download the whole "data" folder and place it on your local device in the same folder as the rest of the project. The python files will be reading and importing data from this "data" folder that contains the raw/cleaned/enriched.

The data cleaning, analysis, and visualization will be based on the dates between 2022-12-18 to 2024-12-16. The dates are currently hard coded to parse the already downloaded data. This code could re-run with fresh data in the future, but for the scope of this project, the report is being set to a consistent date range

## Running the Code
Within the local folder path, You can run the "src/get_data.py" > "src/clean_data.py" > "src/analyze_data.py" > "src/visualize_results.py" in sequential order to process the data. A majority of the relevant data (in various forms raw/cleaned/enriched), statistics, visualization will be downloaded within the "data" file. 

```
python src/get_data.py
python src/clean_data.py
python src/analyze_data.py
python src/visualize_results.py
```

The "get_data_package" contains the under the hood functions that the "get_data.py" code imports and runs. I did this mainly to declutter the get_data.py and to separate out the stock data collection from the CPI inflation data collection. Each can be run independently if needed.


# DIY API Request
If you would like to run the API requests, you will need to sign up for accounts at Polygon.io and USBureauOfLaborStatistics to get an API key.
Both of these are free, but Polygon.io has different tiers of plans with impact how much and how quickly you can make API requests. This is a notice that the Polygon.io free plan throttles the API request to 5requests/minute. So to download 2 years worth of data, it would take approximately 2 hours to download. By going forward with the DIY approach, the numbers and analysis will invariably change because the dataset pulled will contain newer data than what I analyzed.
## Polygon.io Stock Data
[Polygon.io API](https://polygon.io/docs/stocks/getting-started) has a free plan to [sign up](https://polygon.io/pricing). Once you have access to the API key, go into the "get_data_package/get_stock_data.py" and input your API key in the "api_key" variable.

## Wikipedia S&P Data
[Wikipedia API](https://en.wikipedia.org/api/rest_v1/#/Page%20content/get_page_html__title_) doesn't require an account and you can download the .txt file with the titles.
These are the 3 title you want to request HTML from: "List of S&P 500 companies", "List of S&P 400 companies", "List of S&P 600 companies". It will return a .txt file.
The .txt file should be renamed and placed in the "data/raw" folder as such: "List_of_S&P_500_companies(LargeCap).txt", "List_of_S&P_400_companies(MidCap).txt", "List_of_S&P_600_companies(SmallCap).txt"

## US Bureau of Labor Statistics
[USBureauofLaborStatistics API](https://www.bls.gov/developers/api_python.htm#python2) has a free account wher you can [sign up](https://www.bls.gov/developers/) and create a [Public Data API Account](https://data.bls.gov/registrationEngine/). Once you have access to the API key, go into the "get_data_package/get_inflation_data.py" and input your API key in the "api_key" variable. This will download quickly as the data is public.