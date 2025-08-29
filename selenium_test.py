from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os

# --- Configuration ---
# Updated path to your ChromeDriver executable
# This now points directly to the chromedriver.exe inside the 'chromedriver-win64' subfolder.
CHROMEDRIVER_PATH = r"C:\Users\uvban\Crop_Rate_Predictor\chromedriver-win64\chromedriver.exe"
AGMARKNET_URL = "https://agmarknet.gov.in/PriceAndArrivals/CommodityDailyStateWise.aspx"

print(f"Attempting to open {AGMARKNET_URL} using ChromeDriver from {CHROMEDRIVER_PATH}")

try:
    # Set up the Chrome service
    service = Service(executable_path=CHROMEDRIVER_PATH)
    
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=service)
    
    # Open the Agmarknet URL
    driver.get(AGMARKNET_URL)
    
    print("Agmarknet website opened successfully! ✅")
    print(f"Current page title: {driver.title}")
    
    # Keep the browser open for a few seconds to verify
    time.sleep(5) 

except Exception as e:
    print(f"An error occurred: {e} ❌")
    print("Please ensure:")
    print("1. The path to chromedriver.exe is absolutely correct.")
    print("2. Your Chrome browser is updated and matches the ChromeDriver version.")
    print("3. Your virtual environment is active.")

finally:
    # Close the browser
    if 'driver' in locals() and driver:
        driver.quit()
        print("Browser closed. 🌐")
