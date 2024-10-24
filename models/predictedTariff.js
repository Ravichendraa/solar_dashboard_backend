const mongoose = require('mongoose');

const predictedTariffSchema = new mongoose.Schema({
  hour: { type: Number, required: true },
  tariff: { type: Number, required: true },
  date: { type: String, required: true }
}, { timestamps: true });

module.exports = mongoose.model('PredictedTariff', predictedTariffSchema);
