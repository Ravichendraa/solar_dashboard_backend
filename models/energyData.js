const mongoose = require('mongoose');

// Define the schema for solar and consumption data
const energySchema = new mongoose.Schema({
  sendDate: { type: String, required: true }, // Date in 'DD-MM-YYYY' format
  temperature: { type: Number, required: true }, // Temperature in Celsius
  solarPower: { type: Number, default: 0 }, // Power in kW
  solarEnergyGeneration: { type: Number, default: 0 }, // Energy in kWh
  consumptionValue: { type: Number, default: 0 }, // Consumption in kW
}, {
  timestamps: true, // Automatically adds createdAt and updatedAt
});

const EnergyData = mongoose.model('EnergyData', energySchema);

module.exports = EnergyData;
