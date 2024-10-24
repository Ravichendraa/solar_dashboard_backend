// routes/energyConsumption.js
const express = require('express');
const EnergyConsumption = require('../models/EnergyConsumption');

const router = express.Router();

// Get all energy consumption data
router.get('/', async (req, res) => {
  try {
    const data = await EnergyConsumption.find();
    res.json(data);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// Add more routes as needed, such as for posting new data, updating, etc.

module.exports = router;
