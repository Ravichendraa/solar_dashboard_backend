const mongoose = require('mongoose');

// Define the schema with the correct structure
const consumptionSchema = new mongoose.Schema({
  date: { type: Date, required: true }, // Date in ISO format
  'Lighting (kWh)': { type: Number, default: 0 },
  'Refrigerator (kWh)': { type: Number, default: 0 },
  'Washing Machine (kWh)': { type: Number, default: 0 },
  'Television (kWh)': { type: Number, default: 0 },
  'Air Conditioner (kWh)': { type: Number, default: 0 },
  'Microwave (kWh)': { type: Number, default: 0 },
  'Laptop (kWh)': { type: Number, default: 0 },
  'Water Heater (kWh)': { type: Number, default: 0 },
  'Dishwasher (kWh)': { type: Number, default: 0 },
  'EV Charger (kWh)': { type: Number, default: 0 },
  'Other Devices (kWh)': { type: Number, default: 0 },
});

const Consumption = mongoose.model('Consumption', consumptionSchema);

module.exports = Consumption;
