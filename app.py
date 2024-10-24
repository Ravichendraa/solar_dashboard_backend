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
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['Luminous']
    predictions_collection = db['tariffs']
    predicted_collection = db['predicted_tariffs']  # New collection for predicted tariffs
    solar_prediction_collection = db['predicted_solar_energy']  # Collection for solar energy predictions
    appliance_prediction_collection = db['predicted_appliance_consumption']  # Collection for predicted appliance consumption
    logging.info("Connected to MongoDB.")
except errors.ServerSelectionTimeoutError as e:
    logging.error("MongoDB connection failed: %s", e)

# API endpoint URLs
TARIFF_API_URL = 'http://localhost:5000/api/tariffs'
ENERGY_API_URL = 'http://localhost:5000/api/energy-data'
CONSUMPTION_API_URL = 'http://localhost:5000/api/consumptions'

def fetch_tariff_data():
    """Fetch tariff data from the API and convert it into a DataFrame."""
    try:
        response = requests.get(TARIFF_API_URL)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d-%m-%Y %H:%M:%S')  # Convert DateTime to datetime object
        logging.info("Tariff data fetched successfully.")
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
    today ="21-10-2024"
    #for live data use today = (datetime.now()).strftime("%d-%m-%Y")  # Predict for next day (21st Oct 2024)
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
    y = df[features]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict for the next day (21st Oct 2024)
    predictions = model.predict([X.iloc[-1]])  # Predicting based on the last day's data

    # Prepare data for MongoDB insertion
    next_day ="21-10-2024"
    #for live data use next_day = (datetime.now()).strftime("%d-%m-%Y")
    appliance_prediction_data = {
        'date': next_day,
        'Lighting (kWh)': float(predictions[0][0]),
        'Refrigerator (kWh)': float(predictions[0][1]),
        'Washing Machine (kWh)': float(predictions[0][2]),
        'Television (kWh)': float(predictions[0][3]),
        'Air Conditioner (kWh)': float(predictions[0][4]),
        'Microwave (kWh)': float(predictions[0][5]),
        'Laptop (kWh)': float(predictions[0][6]),
        'Water Heater (kWh)': float(predictions[0][7]),
        'Dishwasher (kWh)': float(predictions[0][8]),
        'EV Charger (kWh)': float(predictions[0][9]),
        'Other Devices (kWh)': float(predictions[0][10])
    }

    # Store appliance consumption predictions in MongoDB
    try:
        appliance_prediction_collection.delete_many({'date': next_day})  # Clear existing data for tomorrow
        appliance_prediction_collection.insert_one(appliance_prediction_data)
        logging.info("Appliance consumption predictions stored successfully.")
    except errors.PyMongoError as e:
        logging.error("Error storing appliance consumption predictions: %s", e)

    return appliance_prediction_data

@app.route('/api/predicted_tariffs', methods=['GET'])
def get_predicted_tariffs():
    """Fetch predicted tariffs for the next day from MongoDB."""
    target_date = "21-10-2024" 
    #for live data use target_date = (datetime.now()).strftime("%d-%m-%Y")
    try:
        predictions = list(predicted_collection.find({'date': target_date}, {'_id': 0}))
        return jsonify(predictions)
    except errors.PyMongoError as e:
        logging.error("Error fetching predictions: %s", e)
        return jsonify([]), 500

@app.route('/api/predicted_solar_energy', methods=['GET'])
def get_predicted_solar_energy():
    """Fetch predicted solar energy for the next day from MongoDB."""
    target_date = "21-10-2024" 
    #for live data use target_date = (datetime.now()).strftime("%d-%m-%Y")
    try:
        predictions = list(solar_prediction_collection.find({'date': target_date}, {'_id': 0}))
        return jsonify(predictions)
    except errors.PyMongoError as e:
        logging.error("Error fetching solar predictions: %s", e)
        return jsonify([]), 500

@app.route('/api/predicted_appliance_consumption', methods=['GET'])
def get_predicted_appliance_consumption():
    """Fetch predicted appliance consumption for the next day from MongoDB."""
    target_date = "21-10-2024" 
    #for live data use target_date = (datetime.now()).strftime("%d-%m-%Y")
    try:
        predictions = appliance_prediction_collection.find_one({'date': target_date}, {'_id': 0})
        return jsonify(predictions) if predictions else jsonify({})
    except errors.PyMongoError as e:
        logging.error("Error fetching appliance consumption predictions: %s", e)
        return jsonify({}), 500
    
@app.route('/api/schedule', methods=['GET'])
def get_optimized_schedule():
    """API endpoint to get optimized appliance schedule."""
    tariff_data = fetch_tariff_data()
    solar_data = fetch_energy_data()
    
    # Fetch predicted appliance consumption from the database
    appliance_prediction = appliance_prediction_collection.find_one({'date': "21-10-2024"})  # Use your desired date
    if appliance_prediction is None:
        return jsonify({"error": "No appliance consumption data found."}), 400
    
    # Convert the appliance prediction to a DataFrame for processing
    consumption_data = pd.DataFrame([appliance_prediction])

    if tariff_data.empty or solar_data.empty or consumption_data.empty:
        return jsonify({"error": "Insufficient data for optimization."}), 400

    schedule, total_savings = optimize_appliance_schedule(tariff_data, solar_data, consumption_data)
    return jsonify({"schedule": schedule, "total_savings": total_savings}), 200

import random


def optimize_appliance_schedule(tariff_data, solar_data, consumption_data):
    """Optimize appliance schedule based on tariff and solar generation data."""
    total_savings = 0
    schedule = []
    battery_capacity = 10  # kWh
    current_battery = random.uniform(0, battery_capacity)  # Random initial battery charge

    # Extract consumption for specific appliances
    appliances = {
        'Laptop': consumption_data['Laptop (kWh)'].values[0],
        'Dishwasher': consumption_data['Dishwasher (kWh)'].values[0],
        'EV Charger': consumption_data['EV Charger (kWh)'].values[0],
        'Washing Machine': consumption_data['Washing Machine (kWh)'].values[0],
    }

    # Track scheduled appliances to avoid scheduling them multiple times
    scheduled_appliances = set()
    emergency_threshold = 2  # Minimum battery level to keep for emergencies
    current_mode = 'normal'  # Default mode
    threshold_tariff = 5  # Example threshold for tariff to switch modes

    # Loop through each hour to optimize the schedule
    for hour in range(24):
        hour_tariff = tariff_data.loc[hour, 'Tariff (INR/kWh)']
        solar_energy = solar_data.loc[hour, 'solarEnergyGeneration']

        # If it's solar generation time, add solar energy to the current battery capacity
        if solar_energy > 0:
            current_battery = min(battery_capacity, current_battery + solar_energy)

        hour_schedule = {}
        current_savings = 0

        # Determine the operating mode based on tariff
        if hour_tariff > threshold_tariff:
            current_mode = 'solar'
        else:
            current_mode = 'normal'

        # Schedule appliances based on the current mode and tariff conditions
        if current_mode == 'normal':
            # Schedule devices in normal mode (low tariff)
            for appliance, consumption in appliances.items():
                if appliance not in scheduled_appliances and consumption <= current_battery:
                    hour_schedule[appliance] = {
                        "status": "Run",
                        "start_hour": hour,
                        "end_hour": hour + 1,
                        "consumption": consumption
                    }
                    total_savings += (hour_tariff * consumption)  # Saving calculation
                    current_battery -= consumption  # Update battery charge
                    scheduled_appliances.add(appliance)
                    break  # Schedule only one appliance per hour

        elif current_mode == 'solar':
            # In solar mode, use solar energy and schedule devices if they can be powered
            for appliance, consumption in appliances.items():
                if appliance not in scheduled_appliances and consumption <= current_battery - emergency_threshold:
                    hour_schedule[appliance] = {
                        "status": "Run",
                        "start_hour": hour,
                        "end_hour": hour + 1,
                        "consumption": consumption
                    }
                    current_battery -= consumption  # Update battery charge
                    scheduled_appliances.add(appliance)
                    # Add savings from using solar energy instead of grid
                    current_savings += (hour_tariff * consumption)  # Cost of using grid power
                    break  # Schedule only one appliance per hour

        # Calculate the current battery charge percentage for the hour
        current_battery_percentage = (current_battery / battery_capacity) * 100

        # Store hourly schedule details
        schedule.append({
            "hour": hour,
            "current_mode": current_mode,
            "current_savings": current_savings,
            "current_battery_charge_percentage": current_battery_percentage,
            "hour_schedule": hour_schedule,
            "remaining_battery_capacity": current_battery
        })

    return schedule, total_savings




if __name__ == '__main__':
    # Predict and store tariffs, solar energy, and appliance consumption when the server starts
    predict_and_store()
    predict_solar_energy_and_store()
    predict_appliance_consumption_and_store()
    app.run(debug=True)
