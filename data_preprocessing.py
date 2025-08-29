import pandas as pd

# Define the filename of the CSV you just created
# IMPORTANT: Ensure this matches the exact name of your saved CSV file.
file_path = "historical_crop_data_wheat_madhay_pradesh_ratlam.csv" 

# Load the data into a Pandas DataFrame
try:
    # When reading CSV, Pandas might infer some columns as objects (strings)
    # We'll explicitly handle date and price conversions in the next step.
    df = pd.read_csv(file_path)
    print("Data loaded successfully! Here's the initial information:")
    print(df.info())
    print("\nFirst 5 rows of the DataFrame:")
    print(df.head())
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found. Please check the file name and path.")
except Exception as e:
    print(f"An unexpected error occurred while loading the file: {e}")

# --- Week 2, Day 2: Data Type Conversion ---
print("\n--- Starting Data Type Conversion ---")

# Convert 'Date' column to a proper datetime format
# The format from Agmarknet is "DD-Mon-YYYY" (e.g., 25-Aug-2025)
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y', errors='coerce')
    print(f"Converted 'Date' column. First 5 dates:\n{df['Date'].head()}")
else:
    print("Warning: 'Date' column not found for conversion.")

# Convert price columns to numeric
# These are the expected price columns based on Agmarknet's table headers
price_cols_to_convert = ['Min_Price_Rs', 'Max_Price_Rs', 'Modal_Price_Rs']

for col in price_cols_to_convert:
    if col in df.columns:
        # First, ensure the column is a string type to use .str accessor
        df[col] = df[col].astype(str)
        # Remove commas and any leading/trailing spaces
        df[col] = df[col].str.replace(',', '', regex=False).str.strip()
        # Convert to a numeric type, setting any errors to NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
        print(f"Converted '{col}' column. First 5 values:\n{df[col].head()}")
    else:
        print(f"Warning: Price column '{col}' not found for conversion.")

print("\nData types after conversion:")
print(df.info())

# --- Save the cleaned data (optional, but good practice) ---
cleaned_file_path = "cleaned_historical_agmarknet_data.csv"
df.to_csv(cleaned_file_path, index=False)
print(f"\nCleaned data saved to {cleaned_file_path}")

