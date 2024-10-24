from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)

# Initialize Flask and enable CORS
app = Flask(__name__)
CORS(app)

# Mock tariff data for 24 hours
def get_mock_tariff_data():
    data = [{'hour': i, 'tariff': round(5 + i * 0.1, 2)} for i in range(24)]
    return pd.DataFrame(data)

# Mock solar energy generation data for 24 hours
def get_mock_solar_data():
    data = [{'hour': i, 'solar_energy_generation': max(0, 5 - abs(i - 12))} for i in range(24)]
    return pd.DataFrame(data)

# Mock appliance consumption data (daily)
def get_mock_consumption_data():
    data = {
        'Lighting (kWh)': 1, 'Refrigerator (kWh)': 2, 'Washing Machine (kWh)': 0.5,
        'Television (kWh)': 0.7, 'Air Conditioner (kWh)': 3, 'Microwave (kWh)': 0.6,
        'Laptop (kWh)': 0.4, 'Water Heater (kWh)': 2, 'Dishwasher (kWh)': 1.5,
        'EV Charger (kWh)': 0.8, 'Other Devices (kWh)': 1.2
    }
    return pd.DataFrame([data])

@app.route('/')
def index():
    return "API is working!"

# Route for predicted tariffs
@app.route('/api/predicted_tariffs', methods=['GET'])
def predicted_tariffs():
    data = get_mock_tariff_data()
    return jsonify(data.to_dict(orient='records'))

# Route for predicted solar energy generation
@app.route('/api/predicted_solar_energy', methods=['GET'])
def predicted_solar_energy():
    data = get_mock_solar_data()
    return jsonify(data.to_dict(orient='records'))

# Route for predicted appliance consumption
@app.route('/api/predicted_appliance_consumption', methods=['GET'])
def predicted_appliance_consumption():
    data = get_mock_consumption_data()
    return jsonify(data.to_dict(orient='records'))

# Optimization logic
def optimize_appliance_schedule(tariff_data, solar_data, consumption_data, battery_capacity=10):
    total_cost_without_optimization = 0
    total_cost_with_optimization = 0
    schedule = []

    # Initialize battery status
    battery_status = 0  # in kWh

    for hour in range(24):
        hour_tariff = tariff_data.loc[hour, 'tariff']  # Get tariff for this hour
        solar_energy = solar_data.loc[hour, 'solar_energy_generation']  # Get solar energy for this hour
        appliances = consumption_data.iloc[0].to_dict()  # Get the predicted consumption for the appliances

        for appliance, consumption in appliances.items():
            if consumption == 0:
                continue
            
            # Cost without optimization
            cost_without_optimization = consumption * hour_tariff
            total_cost_without_optimization += cost_without_optimization
            
            # Determine if we can use solar energy
            if battery_status + solar_energy >= consumption:
                cost_with_optimization = 0
                battery_status += solar_energy - consumption
                optimal_source = 'Solar'
            else:
                needed_from_grid = consumption - (battery_status + solar_energy)
                if needed_from_grid < 0:
                    needed_from_grid = 0
                    battery_status += solar_energy - consumption
                else:
                    battery_status = 0  # Battery fully discharged
                
                cost_with_optimization = needed_from_grid * hour_tariff
                optimal_source = 'Grid'

            total_cost_with_optimization += cost_with_optimization
            
            schedule.append({
                'hour': hour,
                'appliance': appliance,
                'optimal_source': optimal_source,
                'consumption': consumption,
                'cost_without_optimization': cost_without_optimization,
                'cost_with_optimization': cost_with_optimization
            })

    total_savings = total_cost_without_optimization - total_cost_with_optimization
    return schedule, total_savings

# Route to get optimized schedule
@app.route('/api/optimized_schedule', methods=['GET'])
def get_optimized_schedule():
    """Calculate and return optimized schedule and savings."""
    tariff_data = get_mock_tariff_data()
    solar_data = get_mock_solar_data()
    consumption_data = get_mock_consumption_data()

    schedule, total_savings = optimize_appliance_schedule(tariff_data, solar_data, consumption_data)

    return jsonify({
        'schedule': schedule,
        'total_savings': total_savings
    })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
