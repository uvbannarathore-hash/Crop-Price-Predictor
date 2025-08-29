import requests
import os
import pandas as pd
from dotenv import load_dotenv
import time

# --- Configuration ---
load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    print("Error: API_KEY not found in .env file. Please check your .env file.")
    exit()

BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

# Target crop and state for data collection
# We will use these to filter the data AFTER fetching it
TARGET_CROP = "Wheat"  
TARGET_STATE = "Uttar Pradesh" 

LIMIT_PER_REQUEST = 500
TOTAL_RECORDS_TO_FETCH = 10000 

all_records = []
offset = 0

print(f"Starting unfiltered data collection...")
print(f"Fetching up to {TOTAL_RECORDS_TO_FETCH} records, {LIMIT_PER_REQUEST} per request.")

# --- Data Fetching Loop (UNFILTERED) ---
while offset < TOTAL_RECORDS_TO_FETCH:
    params = {
        "api-key": api_key,
        "format": "json",
        "offset": offset,
        "limit": LIMIT_PER_REQUEST,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status() 
        
        data = response.json()
        records = data.get('records', [])

        if not records:
            print(f"No more records found or end of data at offset {offset}. Stopping.")
            break

        all_records.extend(records)
        print(f"Fetched {len(records)} records. Total collected: {len(all_records)}. Current offset: {offset}")

        offset += LIMIT_PER_REQUEST
        time.sleep(0.5) 

    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected request error occurred: {req_err}")
        break
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        break

print(f"\nFinished fetching raw data. Total records collected: {len(all_records)}")

# --- Data Processing and Filtering with Pandas ---
if all_records:
    df = pd.DataFrame(all_records)
    print("\nInitial DataFrame shape (before filtering):", df.shape)

    # Filter the DataFrame to get only the target crop and state
    # We are now doing the filtering ourselves
    df_filtered = df[(df['state'] == TARGET_STATE) & (df['commodity'] == TARGET_CROP)]
    
    # Standardize column names for easier use
    column_mapping = {
        'state': 'State',
        'district': 'District',
        'market': 'Market',
        'commodity': 'Commodity',
        'variety': 'Variety',
        'arrival_date': 'Date',
        'min_price': 'Min_Price_Rs',
        'max_price': 'Max_Price_Rs',
        'modal_price': 'Modal_Price_Rs',
    }
    df_filtered = df_filtered.rename(columns=column_mapping)
    
    # Convert date column to datetime objects
    if 'Date' in df_filtered.columns:
        df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], errors='coerce', format='%d/%m/%Y')
        df_filtered = df_filtered.dropna(subset=['Date'])
        df_filtered = df_filtered.sort_values(by='Date').reset_index(drop=True)

    # Convert price columns to numeric
    price_cols = ['Min_Price_Rs', 'Max_Price_Rs', 'Modal_Price_Rs']
    for col in price_cols:
        if col in df_filtered.columns:
            df_filtered[col] = df_filtered[col].astype(str).str.replace(',', '', regex=False)
            df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')
    df_filtered = df_filtered.dropna(subset=price_cols)

    print("\nProcessed and Filtered DataFrame head:")
    print(df_filtered.head())
    print(f"\nFinal DataFrame shape (after filtering): {df_filtered.shape}")

    # --- Save to CSV ---
    output_filename = f"historical_crop_data_{TARGET_CROP.lower().replace(' ', '_')}_{TARGET_STATE.lower().replace(' ', '_')}.csv"
    df_filtered.to_csv(output_filename, index=False)
    print(f"\nData successfully saved to {output_filename}")
else:
    print("No records were collected to process.")