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
app = Flask(_name_)
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

# Additional energy and appliance prediction code (same as before)

# Incorporating energy optimization code
def energy_optimization():
    """Optimizes energy consumption based on predicted solar and tariff data."""
    predicted_appliance_consumption_df = pd.read_csv('predicted_appliance_consumption().csv')
    predicted_solar_energy_df = pd.read_csv('predicted_solar_energy.csv')
    predicted_tariffs_df = pd.read_csv('predicted_tariffs.csv')

    # Set up constants
    battery_capacity_kwh = 10
    battery_threshold = 0.2 * battery_capacity_kwh
    battery_level = battery_capacity_kwh
    high_consumption_devices = ["Washing Machine (kWh)", "Laptop (kWh)", "Dishwasher (kWh)", "EV Charger (kWh)"]
    scheduled_hours = {device: False for device in high_consumption_devices}
    non_scheduled_devices = predicted_appliance_consumption_df.columns.difference(high_consumption_devices)
    non_scheduled_hourly_consumption = predicted_appliance_consumption_df[non_scheduled_devices].sum(axis=1) / 24

    # Determine the best hours to schedule high-consumption devices based on the lowest tariff
    tariff_sorted_idx = predicted_tariffs_df.sort_values(by='tariff').index

    # Prepare a list to store hourly data
    hourly_status = []

    # Loop through each hour
    for hour in range(24):
        solar_energy = predicted_solar_energy_df.loc[hour, 'solar_energy_generation']
        tariff = predicted_tariffs_df.loc[hour, 'tariff']

        # Add solar energy to the battery
        battery_level = min(battery_level + solar_energy, battery_capacity_kwh)

        # Switch to solar mode when battery is available, regardless of tariff
        in_solar_mode = tariff > 5
        scheduled_device = None
        if hour in tariff_sorted_idx[:len(high_consumption_devices)]:
            for device in high_consumption_devices:
                if not scheduled_hours[device]:
                    scheduled_device = device
                    scheduled_hours[device] = True
                    break

        # If a device is scheduled, do not use solar mode
        if scheduled_device:
            in_solar_mode = False

        # Calculate non-scheduled devices’ consumption for the hour
        non_scheduled_consumption = non_scheduled_hourly_consumption[0]

        # If in solar mode, use battery, otherwise, consume from the grid
        if in_solar_mode:
            battery_level = max(battery_level - non_scheduled_consumption, 0)

        # Calculate savings when using solar mode
        total_consumption = non_scheduled_consumption + (predicted_appliance_consumption_df[scheduled_device] if scheduled_device else 0)
        non_solar_cost = total_consumption * tariff
        solar_savings = non_solar_cost if in_solar_mode else 0

        # Store hourly status
        hourly_status.append({
            "hour": f"{hour}:00 - {hour + 1}:00",
            "current_mode": "Solar" if in_solar_mode else "Normal",
            "battery_level (%)": (battery_level / battery_capacity_kwh) * 100,
            "solar_savings (INR)": solar_savings,
            "device_scheduled": scheduled_device,
        })

    return hourly_status

# Flask routes
@app.route('/api/predict', methods=['GET'])
def predict():
    predictions = predict_and_store()
    return jsonify(predictions), 200

@app.route('/api/energy-optimization', methods=['GET'])
def get_optimized_energy_data():
    optimized_energy = energy_optimization()
    return jsonify(optimized_energy), 200

if _name_ == '_main_':
    app.run(debug=True)