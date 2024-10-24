// models/tariff.js

const mongoose = require('mongoose');

const tariffSchema = new mongoose.Schema({
  DateTime: { type: String, required: true }, // Assuming DateTime is in string format
  'Tariff (INR/kWh)': { type: Number, required: true },
});

const Tariff = mongoose.model('Tariff', tariffSchema);

module.exports = Tariff;
