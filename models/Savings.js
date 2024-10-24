// models/Savings.js
const mongoose = require('mongoose');

const savingsSchema = new mongoose.Schema({
  hour: { type: String, required: true }, // "0:00 - 1:00"
  current_mode: { type: String, required: true }, // "Solar", "Normal", etc.
  battery_level: { type: Number, required: true }, // Battery level in percentage
  scheduled_device: { type: String, default: 'None' }, // Device scheduled, if any
  savings: { type: Number, required: true }, // Savings in INR
  remaining_battery: { type: Number, required: true }, // Remaining battery in kWh
});

const Savings = mongoose.model('Savings', savingsSchema);

module.exports = Savings;
