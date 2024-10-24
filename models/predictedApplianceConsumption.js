const mongoose = require('mongoose');

const predictedApplianceConsumptionSchema = new mongoose.Schema({
  date: { type: String, required: true },
  'Lighting (kWh)': { type: Number, required: true },
  'Refrigerator (kWh)': { type: Number, required: true },
  'Washing Machine (kWh)': { type: Number, required: true },
  'Television (kWh)': { type: Number, required: true },
  'Air Conditioner (kWh)': { type: Number, required: true },
  'Microwave (kWh)': { type: Number, required: true },
  'Laptop (kWh)': { type: Number, required: true },
  'Water Heater (kWh)': { type: Number, required: true },
  'Dishwasher (kWh)': { type: Number, required: true },
  'EV Charger (kWh)': { type: Number, required: true },
  'Other Devices (kWh)': { type: Number, required: true }
}, { timestamps: true });

module.exports = mongoose.model('PredictedApplianceConsumption', predictedApplianceConsumptionSchema);
