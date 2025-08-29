import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define the filename of the cleaned CSV
file_path = "cleaned_historical_agmarknet_data.csv" 

try:
    df = pd.read_csv(file_path)
    # Ensure 'Date' column is in datetime format, as it might be read as object after saving/loading
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    print("Cleaned data loaded successfully for further processing.")
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found. Please check the file name and path.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred while loading the file: {e}")
    exit()

print("\n--- Checking for Missing Values ---")
print(df.isnull().sum())

# --- Handling Missing Values (Example Strategy) ---
# For time series data, common strategies include:
# 1. Forward-fill (ffill): Propagate last valid observation forward to next valid.
# 2. Backward-fill (bfill): Propagate next valid observation backward to previous valid.
# 3. Interpolation: Estimate missing values based on surrounding data.
# 4. Drop rows: If only a few rows have missing data, you can drop them.

# Let's use a combination: forward-fill for prices, then drop any remaining NaNs
# This assumes that if a price is missing, it's likely similar to the previous day.
price_cols = ['Min_Price_Rs', 'Max_Price_Rs', 'Modal_Price_Rs']
for col in price_cols:
    if col in df.columns:
        df[col] = df[col].fillna(method='ffill')

# Drop any rows where 'Date' or critical price columns are still NaN after filling
df.dropna(subset=['Date'] + price_cols, inplace=True)

print("\nMissing values after handling:")
print(df.isnull().sum())

print(f"\nDataFrame shape after handling missing values: {df.shape}")

# --- Checking for Outliers (Basic Visual Inspection) ---
print("\n--- Checking for Outliers (Descriptive Statistics & Box Plots) ---")
print(df[price_cols].describe())

# Visualize outliers using box plots
plt.figure(figsize=(15, 6))
for i, col in enumerate(price_cols):
    plt.subplot(1, 3, i + 1)
    sns.boxplot(y=df[col])
    plt.title(f'Box Plot of {col}')
plt.tight_layout()
plt.show()

# --- Saving the data after handling missing values and outliers ---
cleaned_file_path_final = "cleaned_historical_agmarknet_data_final.csv"
df.to_csv(cleaned_file_path_final, index=False)
print(f"\nFinal cleaned data saved to {cleaned_file_path_final}")

