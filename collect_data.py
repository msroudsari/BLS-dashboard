import os
import requests
import json
import pandas as pd
from datetime import datetime

def collect_bls_data(api_key):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    series_ids = [
        "LNS11000000",  # Civilian Labor Force (Seasonally Adjusted)
        "LNS12000000",  # Civilian Employment (Seasonally Adjusted)
        "LNS13000000",  # Civilian Unemployment (Seasonally Adjusted)
        "LNS14000000",  # Unemployment Rate (Seasonally Adjusted)
        "CES0000000001",  # Total Nonfarm Employment - Seasonally Adjusted
        "CES0500000002",  # Total Private Average Weekly Hours of All Employees - Seasonally Adjusted
        "CES0500000007",  # Total Private Average Weekly Hours of Prod. and Nonsup. Employees - Seasonally Adjusted
        "CES0500000003",  # Total Private Average Hourly Earnings of All Employees - Seasonally Adjusted
        "CES0500000008"   # Total Private Average Hourly Earnings of Prod. and Nonsup. Employees - Seasonally Adjusted
    ]
    payload = {
        "seriesid": series_ids,
        "startyear": "2020",
        "endyear": str(datetime.now().year),
        "registrationkey": api_key
    }
    response = requests.post(url, json=payload)
    data = response.json()

    if response.status_code == 200 and 'Results' in data:
        records = []
        for series in data['Results']['series']:
            for item in series['data']:
                records.append({
                    "series_id": series['seriesID'],
                    "year": item['year'],
                    "period": item['period'],
                    "value": item['value'],
                    "period_name": item['periodName']
                })
        df = pd.DataFrame(records)
        return df
    else:
        raise ValueError("Error retrieving data: " + data.get('message', 'Unknown error'))

def save_data(df, file_path='bls_data.csv'):
    try:
        existing_data = pd.read_csv(file_path)
        combined_data = pd.concat([existing_data, df]).drop_duplicates()
        combined_data.to_csv(file_path, index=False)
    except FileNotFoundError:
        df.to_csv(file_path, index=False)

if __name__ == "__main__":
    api_key = os.getenv("BLS_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Set the BLS_API_KEY environment variable.")
    
    df = collect_bls_data(api_key)
    save_data(df)
