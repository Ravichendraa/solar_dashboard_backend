const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');

// Import Models
const Consumption = require('./models/consumption'); 
const Tariff = require('./models/tariff'); 
const EnergyData = require('./models/energyData'); 

// New models for predictions (you might need to adjust paths and model definitions)
const PredictedTariff = require('./models/predictedTariff'); 
const PredictedSolarEnergy = require('./models/predictedSolarEnergy'); 
const PredictedApplianceConsumption = require('./models/predictedApplianceConsumption'); 

dotenv.config(); // Load environment variables

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI, {
  // Removed deprecated options
})
  .then(() => console.log('MongoDB connected successfully.'))
  .catch((err) => {
    console.error('MongoDB connection failed:', err);
    process.exit(1); // Exit if connection fails
  });

// Route to get energy data
app.get('/api/energy-data', async (req, res) => {
  try {
    const energyData = await EnergyData.find({});
    console.log('Fetched Energy Data:', energyData);
    if (!energyData.length) {
      return res.status(404).json({ message: 'No energy data found' });
    }
    res.json(energyData);
  } catch (err) {
    console.error('Error fetching energy data:', err);
    res.status(500).json({ error: 'Failed to fetch energy data' });
  }
});

// Route to get consumption data
app.get('/api/consumptions', async (req, res) => {
  try {
    const consumptions = await Consumption.find({});
    console.log('Fetched Consumption Data:', consumptions);
    if (!consumptions.length) {
      return res.status(404).json({ message: 'No consumption data found' });
    }
    res.json(consumptions);
  } catch (err) {
    console.error('Error fetching consumption data:', err);
    res.status(500).json({ error: 'Failed to fetch consumption data' });
  }
});

// Route to get tariff data
app.get('/api/tariffs', async (req, res) => {
  try {
    const tariffs = await Tariff.find({});
    console.log('Fetched Tariff Data:', tariffs);
    if (!tariffs.length) {
      return res.status(404).json({ message: 'No tariff data found' });
    }
    res.json(tariffs);
  } catch (err) {
    console.error('Error fetching tariff data:', err);
    res.status(500).json({ error: 'Failed to fetch tariff data' });
  }
});

// Route to get predicted tariffs
app.get('/api/predicted_tariffs', async (req, res) => {
  try {
    const predictions = await PredictedTariff.find({ date: "21-10-2024" }); // Adjust date if necessary
    console.log('Fetched Predicted Tariffs:', predictions);
    if (!predictions.length) {
      return res.status(404).json({ message: 'No predicted tariffs found' });
    }
    res.json(predictions);
  } catch (err) {
    console.error('Error fetching predicted tariffs:', err);
    res.status(500).json({ error: 'Failed to fetch predicted tariffs' });
  }
});

// Route to get predicted solar energy
app.get('/api/predicted_solar_energy', async (req, res) => {
  try {
    const predictions = await PredictedSolarEnergy.find({ date: "21-10-2024" }); // Adjust date if necessary
    console.log('Fetched Predicted Solar Energy:', predictions);
    if (!predictions.length) {
      return res.status(404).json({ message: 'No predicted solar energy found' });
    }
    res.json(predictions);
  } catch (err) {
    console.error('Error fetching predicted solar energy:', err);
    res.status(500).json({ error: 'Failed to fetch predicted solar energy' });
  }
});

// Route to get predicted appliance consumption
app.get('/api/predicted_appliance_consumption', async (req, res) => {
  try {
    const predictions = await PredictedApplianceConsumption.find({ date: "21-10-2024" }); // Adjust date if necessary
    console.log('Fetched Predicted Appliance Consumption:', predictions);
    if (!predictions.length) {
      return res.status(404).json({ message: 'No predicted appliance consumption found' });
    }
    res.json(predictions);
  } catch (err) {
    console.error('Error fetching predicted appliance consumption:', err);
    res.status(500).json({ error: 'Failed to fetch predicted appliance consumption' });
  }
});

// Serve frontend (if in production mode)
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../frontend/build'))); // Adjusted path to serve frontend build
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/build', 'index.html'));
  });
}

// Start the server
app.listen(PORT, () =>
  console.log(`Server is running on http://localhost:${PORT}`)
);
