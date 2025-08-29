import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# --- Configuration ---
# Your final cleaned dataset
file_path = "cleaned_historical_agmarknet_data_final_up.csv"
#file_path ="cleaned_historical_agmarknet_data_mp_ratlam.csv"

# --- Data Loading and Preparation ---
try:
    df = pd.read_csv(file_path)
    # Ensure 'Date' column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    
    print("Data loaded successfully! Initial DataFrame head:")
    print(df.head())
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found. Please check the file name and path.")
    exit()

# Prepare the DataFrame for Prophet: it needs columns named 'ds' and 'y'
df_prophet = df[['Date', 'Modal_Price_Rs']].copy()
df_prophet = df_prophet.rename(columns={'Date': 'ds', 'Modal_Price_Rs': 'y'})

# Ensure the ds column is a datetime type for Prophet
df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

print("\nDataFrame prepared for Prophet:")
print(df_prophet.head())
print(df_prophet.info())

# --- Basic Visualization of the Time Series ---
# A simple plot helps us see trends and seasonality in our data.
plt.figure(figsize=(15, 6))
plt.plot(df_prophet['ds'], df_prophet['y'])
plt.title('Historical Modal Price of Wheat over Time', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Modal Price (Rs./Quintal)', fontsize=12)
plt.grid(True)
plt.show()

# --- Optional: Save the Prophet-ready DataFrame ---
df_prophet.to_csv("prophet_ready_data.csv", index=False)
print("\nProphet-ready data saved to prophet_ready_data.csv")

# --- Continue in your model_development.py file ---

# Initialize the Prophet model
# We can include seasonality for weekly and yearly patterns, common in commodity prices.
m = Prophet(seasonality_mode='multiplicative', yearly_seasonality=True, weekly_seasonality=True)

# Fit the model to your historical data
print("\nFitting Prophet model to historical data...")
m.fit(df_prophet)

# --- Create a DataFrame for future predictions ---
# We'll create a DataFrame for the next 30 days to forecast.
future = m.make_future_dataframe(periods=30)
print("\nCreated future DataFrame for 30 days:")
print(future.tail())

# --- Make the forecast ---
print("\nGenerating forecast...")
forecast = m.predict(future)

# Display the forecast for the next 30 days
print("\nForecast for the next 30 days:")
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30))

# --- Visualize the forecast ---
# Prophet has a built-in function to plot the forecast, which is very convenient.
print("\nDisplaying forecast plot...")
fig1 = m.plot(forecast)
plt.title('Prophet Forecast for Wheat Prices', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Modal Price (Rs./Quintal)', fontsize=12)
plt.show()

# You can also plot the components (trend, weekly, yearly seasonality)
print("\nDisplaying forecast components plot...")
fig2 = m.plot_components(forecast)
plt.show()
# --- Save the trained Prophet model ---
import joblib # A library to save and load Python objects

model_filename = 'prophet_model_Wheat_Uttar Pradesh_Varansi_Varansi.pkl'
#model_filename = 'prophet_model_Wheat_Madhya Pradesh_Ratlam_Ratlam.pkl'
joblib.dump(m, model_filename)
print(f"\nProphet model saved to {model_filename}")