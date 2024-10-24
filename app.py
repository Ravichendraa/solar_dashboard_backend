from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient, errors
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)

# Initialize Flask and enable CORS
app = Flask(__name__)
CORS(app)

# MongoDB connection setup
try:
    client = MongoClient("mongodb+srv://ravichendraa:n8UK9jMeTENnI7qX@ravi.jyrgg.mongodb.net/?retryWrites=true&w=majority&appName=ravi", serverSelectionTimeoutMS=5000)
    db = client['Luminous']
    predictions_collection = db['tariffs']
    predicted_collection = db['predicted_tariffs']  # New collection for predicted tariffs
    solar_prediction_collection = db['predicted_solar_energy']  # Collection for solar energy predictions
    appliance_prediction_collection = db['predicted_appliance_consumption']  # Collection for predicted appliance consumption
    logging.info("Connected to MongoDB.")
except errors.ServerSelectionTimeoutError as e:
    logging.error("MongoDB connection failed: %s", e)

# API endpoint URLs
TARIFF_API_URL = 'https://solar-dashboard-backend-1.onrender.com/api/tariffs'
ENERGY_API_URL = 'https://solar-dashboard-backend-1.onrender.com/api/energy-data'
CONSUMPTION_API_URL = 'https://solar-dashboard-backend-1.onrender.com/api/consumptions'

def fetch_tariff_data():
    """Fetch tariff data from the API and convert it into a DataFrame."""
    try:
        response = requests.get(TARIFF_API_URL)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)

        # Adjust the format for two-digit year and missing seconds, parsing as much as possible
        df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d-%m-%y %H:%M', errors='coerce')

        # Handle any rows where the date couldn't be parsed
        df = df.dropna(subset=['DateTime'])

        # Set the constant date (21st October 2024) while keeping the time part intact
        constant_date = pd.Timestamp('2024-10-21')
        df['DateTime'] = df['DateTime'].apply(lambda dt: constant_date.replace(hour=dt.hour, minute=dt.minute))

        logging.info("Tariff data fetched, parsed, and date set to 21st October 2024 successfully.")
        return df
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching data: %s", e)
        return pd.DataFrame()

def fetch_energy_data():
    """Fetch energy and solar data from the API and convert it into a DataFrame."""
    try:
        response = requests.get(ENERGY_API_URL)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        df['sendDate'] = pd.to_datetime(df['sendDate'], format='%d-%m-%y %H:%M')  # Convert sendDate to datetime
        logging.info("Energy data fetched successfully.")
        return df
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching energy data: %s", e)
        return pd.DataFrame()

def fetch_consumption_data():
    """Fetch appliance consumption data from the API and convert it into a DataFrame."""
    try:
        response = requests.get(CONSUMPTION_API_URL)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])  # Convert Date to datetime
        logging.info("Appliance consumption data fetched successfully.")
        return df
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching consumption data: %s", e)
        return pd.DataFrame()

def predict_and_store():
    """Predict next 24 hours' tariffs and store them in MongoDB."""
    df = fetch_tariff_data()
    if df.empty:
        logging.error("No data fetched. Skipping prediction.")
        return []

    # Feature engineering
    df['Hour'] = df['DateTime'].dt.hour
    df['DayOfWeek'] = df['DateTime'].dt.dayofweek
    peak_hours = list(range(6, 11)) + list(range(18, 23))  # Define peak hours
    df['IsPeak'] = df['Hour'].apply(lambda x: 1 if x in peak_hours else 0)

    # Prepare features and target
    X = df[['Hour', 'DayOfWeek', 'IsPeak']]
    y = df['Tariff (INR/kWh)']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict for the next 24 hours
    next_day_hours = pd.DataFrame({
        'Hour': list(range(24)),
        'DayOfWeek': [(df['DayOfWeek'].iloc[-1] + 1) % 7] * 24,
        'IsPeak': [1 if hour in peak_hours else 0 for hour in range(24)]
    })
    predictions = model.predict(next_day_hours)

    # Prepare data for MongoDB insertion
    today = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")  # Predict for next day (21st Oct 2024)
    prediction_data = [
        {'hour': i, 'tariff': float(predictions[i]), 'date': today} for i in range(24)
    ]

    # Store predictions in the new collection
    try:
        predicted_collection.delete_many({'date': today})  # Clear existing data for tomorrow
        predicted_collection.insert_many(prediction_data)
        logging.info("Predictions stored successfully.")
    except errors.PyMongoError as e:
        logging.error("Error storing predictions: %s", e)

    return prediction_data

def predict_solar_energy_and_store():
    """Predict next 24 hours' solar energy generation and store them in MongoDB."""
    df = fetch_energy_data()
    if df.empty:
        logging.error("No data fetched. Skipping prediction.")
        return []

    # Feature engineering
    df['Hour'] = df['sendDate'].dt.hour
    df['DayOfWeek'] = df['sendDate'].dt.dayofweek

    # Prepare features and target for solar energy generation
    X = df[['Hour', 'DayOfWeek']]
    y = df['solarEnergyGeneration']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict for the next 24 hours
    next_day_hours = pd.DataFrame({
        'Hour': list(range(24)),
        'DayOfWeek': [(df['DayOfWeek'].iloc[-1] + 1) % 7] * 24
    })
    predictions = model.predict(next_day_hours)

    # Prepare data for MongoDB insertion
    today = "21-10-2024"
    # for live data use today = (datetime.now()).strftime("%d-%m-%Y")
    solar_prediction_data = [
        {'hour': i, 'solar_energy_generation': float(predictions[i]), 'date': today} for i in range(24)
    ]

    # Store solar predictions in MongoDB
    try:
        solar_prediction_collection.delete_many({'date': today})  # Clear existing data for tomorrow
        solar_prediction_collection.insert_many(solar_prediction_data)
        logging.info("Solar energy predictions stored successfully.")
    except errors.PyMongoError as e:
        logging.error("Error storing solar predictions: %s", e)

    return solar_prediction_data

def predict_appliance_consumption_and_store():
    """Predict next day's appliance consumption and store it in MongoDB."""
    df = fetch_consumption_data()
    if df.empty:
        logging.error("No data fetched. Skipping appliance consumption prediction.")
        return []

    # Prepare features and target for appliance consumption
    features = ['Lighting (kWh)', 'Refrigerator (kWh)', 'Washing Machine (kWh)', 'Television (kWh)',
                'Air Conditioner (kWh)', 'Microwave (kWh)', 'Laptop (kWh)', 'Water Heater (kWh)',
                'Dishwasher (kWh)', 'EV Charger (kWh)', 'Other Devices (kWh)']

    X = df[features]
    y = df['Total (kWh)']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict the appliance consumption for tomorrow
    predictions = model.predict(X_test)

    # Prepare data for MongoDB insertion
    today = "21-10-2024"
    # for live data use today = (datetime.now()).strftime("%d-%m-%Y")
    appliance_prediction_data = [
        {'appliance_consumption': float(prediction), 'date': today} for prediction in predictions
    ]

    # Store appliance consumption predictions in MongoDB
    try:
        appliance_prediction_collection.delete_many({'date': today})  # Clear existing data for tomorrow
        appliance_prediction_collection.insert_many(appliance_prediction_data)
        logging.info("Appliance consumption predictions stored successfully.")
    except errors.PyMongoError as e:
        logging.error("Error storing appliance predictions: %s", e)

    return appliance_prediction_data

@app.route('/api/predicted_tariffs', methods=['GET'])
def get_predicted_tariffs():
    """Fetch predicted tariffs for the next day from MongoDB."""
    target_date = "21-10-2024"  # Static target date (You can modify this as needed)
    try:
        predictions = list(predicted_collection.find({'date': target_date}, {'_id': 0}))
        if predictions:
            logging.info(f"Fetched predictions for {target_date}: {predictions}")
        else:
            logging.info(f"No predictions found for {target_date}.")
        return jsonify(predictions)
    except errors.PyMongoError as e:
        logging.error("Error fetching predictions: %s", e)
        return jsonify([]), 500

# You can define similar routes for solar energy and appliance consumption if needed

if __name__ == '__main__':
    # Bind the Flask app to 0.0.0.0 to allow external requests
    app.run(host='0.0.0.0', port=5000, debug=True)






