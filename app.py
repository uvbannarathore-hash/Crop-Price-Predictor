from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from prophet import Prophet
import joblib
from datetime import datetime, timedelta
import os

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app) # Allow CORS for all routes and all origins for local development

# --- Load all trained Prophet models ---
TRAINED_MODELS = {}
MODEL_DIR = "." # Assuming models are in the current directory

print("Loading Prophet models...")
for filename in os.listdir(MODEL_DIR):
    if filename.startswith('prophet_model_') and filename.endswith('.pkl'):
        try:
            # Remove prefix and suffix to get the core parameters string
            params_str = filename.replace('prophet_model_', '').replace('.pkl', '')
            
            # Split by underscore. This will give parts like ['Wheat', 'Uttar', 'Pradesh', 'Varanasi', 'Varanasi']
            parts = params_str.split('_')
            
            # We know the structure is generally: Commodity_State(can be multi-word)_District_Market
            # So, the last two parts are District and Market.
            # The first part is Commodity.
            # The parts in between form the State.

            if len(parts) >= 4: # Ensure there are enough parts to parse
                commodity_raw = parts[0]
                market_raw = parts[-1]
                district_raw = parts[-2]
                
                # Reconstruct the state name by joining the middle parts
                # This handles states like "Uttar_Pradesh" correctly
                state_parts_raw = parts[1:-2]
                state_raw = '_'.join(state_parts_raw)

                # Format for display (replace underscores with spaces and title case)
                commodity = commodity_raw.replace('_', ' ').title()
                state = state_raw.replace('_', ' ').title()
                district = district_raw.replace('_', ' ').title()
                market = market_raw.replace('_', ' ').title()
                
                model_key = (commodity, state, district, market)
                model = joblib.load(os.path.join(MODEL_DIR, filename))
                TRAINED_MODELS[model_key] = model
                print(f"  Loaded model for {model_key}")
            else:
                print(f"  Skipping '{filename}': filename format not recognized for parsing parameters.")

        except Exception as e:
            print(f"  Error loading model '{filename}': {e}")

if not TRAINED_MODELS:
    print("No Prophet models found or loaded. Please ensure models are saved as 'prophet_model_*.pkl'.")
    # For a production app, you might want to exit here: exit() 

# --- Root route for server status check ---
@app.route('/', methods=['GET'])
def server_status():
    """
    A simple endpoint to confirm the Flask server is running.
    Used by the frontend's checkServerStatus() function.
    """
    return jsonify({"status": "Flask server is running!"}), 200

# --- API Endpoint for Predictions ---
@app.route('/predict', methods=['GET'])
def predict():
    """
    API endpoint to get future crop price predictions.
    Expects 'days', 'commodity', 'state', 'district', 'market' as query parameters.
    """
    try:
        days_str = request.args.get('days', '7')
        commodity_param = request.args.get('commodity')
        state_param = request.args.get('state')
        district_param = request.args.get('district')
        market_param = request.args.get('market')

        if not all([commodity_param, state_param, district_param, market_param]):
            return jsonify({"error": "Missing commodity, state, district, or market parameter."}), 400

        model_key = (commodity_param, state_param, district_param, market_param)
        
        if model_key not in TRAINED_MODELS:
            return jsonify({"error": f"No model found for {model_key}. Please train a model for this combination."}), 404

        m = TRAINED_MODELS[model_key] # Select the correct model

        days = int(days_str)
        if days <= 0:
            return jsonify({"error": "Number of days must be a positive integer."}), 400

        future = m.make_future_dataframe(periods=days)
        forecast = m.predict(future)

        last_historical_date = m.history['ds'].max()
        future_forecast = forecast[forecast['ds'] > last_historical_date]

        predictions = []
        for index, row in future_forecast.iterrows():
            predictions.append({
                "date": row['ds'].strftime('%Y-%m-%d'),
                "predicted_price": round(row['yhat'], 2),
                "lower_bound": round(row['yhat_lower'], 2),
                "upper_bound": round(row['yhat_upper'], 2)
            })

        return jsonify(predictions)

    except ValueError:
        return jsonify({"error": "Invalid 'days' parameter. Must be an integer."}), 400
    except Exception as e:
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500

# --- API Endpoint for getting available options ---
@app.route('/options', methods=['GET'])
def get_options():
    """
    API endpoint to return available commodity, state, district, market options
    based on the loaded models.
    """
    print("Frontend requested /options endpoint.") # Debugging print
    commodities = sorted(list(set(k[0] for k in TRAINED_MODELS.keys())))
    states = sorted(list(set(k[1] for k in TRAINED_MODELS.keys())))
    districts = sorted(list(set(k[2] for k in TRAINED_MODELS.keys())))
    markets = sorted(list(set(k[3] for k in TRAINED_MODELS.keys())))

    return jsonify({
        "commodities": commodities,
        "states": states,
        "districts": districts,
        "markets": markets
    })


# --- Run the Flask App ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
