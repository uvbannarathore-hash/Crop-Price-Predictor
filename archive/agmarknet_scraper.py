import pandas as pd
import numpy as np

# Define the filename of the CSV you just created
file_path = "historical_agmarknet_data.csv" 

try:
    # Read the CSV without specifying a header initially
    # This reads the entire file, treating all rows as data.
    df = pd.read_csv(file_path, header=None)
    print("Initial raw data loaded. First 5 rows:")
    print(df.head())

    # --- Manually identify and set headers ---
    # The actual column headers are in the second row (index 1) of the CSV.
    # The first row (index 0) contains metadata.
    
    # Get the actual headers from the second row (index 1)
    new_columns = df.iloc[1] 
    
    # Set these as the DataFrame's column names
    df.columns = new_columns
    
    # Drop the first two rows (original metadata and the row that became headers)
    df = df.iloc[2:].reset_index(drop=True)

    print("\nData loaded with corrected headers! Here's the initial information:")
    print(df.info())
    print("\nFirst 5 rows of the DataFrame (after header correction):")
    print(df.head())

except FileNotFoundError:
    print(f"Error: The file {file_path} was not found. Please check the file name and path.")
except Exception as e:
    print(f"An unexpected error occurred while loading the file: {e}")

# --- Clean column names for easier use ---
# This step is crucial before attempting to rename specific columns
df.columns = df.str.strip().str.replace(' ', '_', regex=False)
df.columns = df.columns.str.replace('[^a-zA-Z0-9_]', '', regex=True)
print("\nCleaned column names after initial cleanup:")
print(df.columns.tolist()) # Print as list for better readability

# --- Data Type Conversion ---
print("\n--- Starting Data Type Conversion ---")

# Define a mapping from expected raw headers to desired clean headers
# This mapping should use the *cleaned* column names as keys.
column_rename_map = {
    'Sl_no': 'Sl_No',
    'District_Name': 'District',
    'Market_Name': 'Market',
    'Commodity': 'Commodity',
    'Variety': 'Variety',
    'Grade': 'Grade',
    'Min_Price_RsQuintal': 'Min_Price_Rs',
    'Max_Price_RsQuintal': 'Max_Price_Rs',
    'Modal_Price_RsQuintal': 'Modal_Price_Rs',
    'Price_Date': 'Date', # This is the crucial one for date conversion
    'State': 'State' # Ensure State column is consistent (assuming it was 'State' or 'State_Name' after cleanup)
}

# Apply renaming only for columns that actually exist in the DataFrame
df = df.rename(columns={k: v for k, v in column_rename_map.items() if k in df.columns})
print("\nColumn names after renaming:")
print(df.columns.tolist())

# Ensure 'Date' column is present and convert to datetime objects
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d-%b-%Y') # Format updated to match "dd-Mon-yyyy"
    df = df.dropna(subset=['Date'])
    df = df.sort_values(by='Date').reset_index(drop=True)
    print(f"Converted 'Date' column. First 5 dates:\n{df['Date'].head()}")
else:
    print("Warning: 'Date' column not found for conversion. Check scraped headers and rename map.")

# Convert price columns to numeric
price_cols = [col for col in ['Min_Price_Rs', 'Max_Price_Rs', 'Modal_Price_Rs'] if col in df.columns]
for col in price_cols:
    if col in df.columns:
        df[col] = df[col].astype(str)
        df[col] = df[col].str.replace(',', '', regex=False).str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')
        print(f"Converted '{col}' column. First 5 values:\n{df[col].head()}")
    else:
        print(f"Warning: Price column '{col}' not found for conversion. Check scraped headers and rename map.")

# Drop any rows where critical price data is missing after conversion
df = df.dropna(subset=price_cols)

print("\nData types after conversion:")
print(df.info())

# --- Save the cleaned data (optional, but good practice) ---
cleaned_file_path = "cleaned_historical_agmarknet_data.csv"
df.to_csv(cleaned_file_path, index=False)
print(f"\nCleaned data saved to {cleaned_file_path}")
