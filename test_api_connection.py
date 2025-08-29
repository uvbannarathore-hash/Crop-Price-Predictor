
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get your API key
api_key = os.getenv("API_KEY")

if not api_key:
    print("Error: API_KEY not found in .env file.")
    exit()

# The specific OGD API endpoint for crop prices
base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

# Parameters for the API request
params = {
    "api-key": api_key,
    "format": "json",
    "offset": 0,
    "limit": 10
}

try:
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # This will raise an exception for bad responses (4xx or 5xx)

    data = response.json()
    print("API connection successful! Data received:")
    print(data)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")