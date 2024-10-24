const mongoose = require('mongoose');

const predictedSolarEnergySchema = new mongoose.Schema({
  hour: { type: Number, required: true },
  solar_energy_generation: { type: Number, required: true },
  date: { type: String, required: true }
}, { timestamps: true });

module.exports = mongoose.model('PredictedSolarEnergy', predictedSolarEnergySchema);
