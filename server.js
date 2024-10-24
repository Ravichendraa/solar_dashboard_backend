const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');

// Import Models
const Consumption = require('./models/consumption'); 
const Tariff = require('./models/tariff'); 
const EnergyData = require('./models/energyData'); 

dotenv.config(); // Load environment variables

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
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

// Serve frontend (if in production mode)
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, 'client/build')));
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'client/build', 'index.html'));
  });
}

// Start the server
app.listen(PORT, () =>
  console.log(`Server is running on http://localhost:${PORT}`)
);
