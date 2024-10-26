const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const logger = require('morgan');
const Consumption = require('./models/consumption'); 
const Tariff = require('./models/tariff'); 
const EnergyData = require('./models/energyData'); 
const PredictedTariff = require('./models/predictedTariff');
const PredictedSolarEnergy = require('./models/predictedSolarEnergy');
const PredictedApplianceConsumption = require('./models/predictedApplianceConsumption');
const Savings = require('./models/Savings');

// Initialize express app
const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(logger('dev'));

// MongoDB connection
const MONGODB_URI = 'mongodb+srv://ravichendraa:n8UK9jMeTENnI7qX@ravi.jyrgg.mongodb.net/Luminous?retryWrites=true&w=majority';
mongoose
  .connect(MONGODB_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Connected to MongoDB'))
  .catch((err) => console.error('MongoDB connection error:', err));



// Routes
app.get('/api/tariffs', async (req, res) => {
  try {
    // Fetch all tariffs
    const tariffs = await Tariff.find({});
  
    // Sort tariffs by parsing `DateTime` in `dd-mm-yy hh:mm` format to ISO date for accurate sorting
    tariffs.sort((a, b) => {
      const dateA = new Date(a.DateTime.replace(/(\d{2})-(\d{2})-(\d{2})/, '20$3-$2-$1'));
      const dateB = new Date(b.DateTime.replace(/(\d{2})-(\d{2})-(\d{2})/, '20$3-$2-$1'));
      return dateA - dateB;
    });
  
    res.json(tariffs); // Send the sorted tariffs
  } catch (error) {
    console.error('Error fetching tariffs:', error);
    res.status(500).json({ error: 'Failed to fetch tariffs' });
  }
  
  
});


app.get('/api/predicted_tariffs', async (req, res) => {
  try {
    const date = '21-10-24'; // Fixed date for the query
  
    // Query the database for tariffs matching the specified date and sort by hour
    const predictions = await PredictedTariff.find({ date }).sort({ hour: 1 });
  
    if (predictions.length === 0) {
      return res.status(404).json({ message: 'No tariff predictions found for the given date' });
    }
  
    res.json(predictions); // Send the sorted predictions
  } catch (error) {
    console.error('Error fetching predicted tariffs:', error);
    res.status(500).json({ error: 'Failed to fetch predicted tariffs' });
  }
  
});




app.get('/api/energy-data', async (req, res) => {
  try {
    // Fetch all energy data
    const energyData = await EnergyData.find({});
  
    // Sort energy data by parsing `sendDate` in `dd-mm-yy hh:mm` format to ISO date for accurate sorting
    energyData.sort((a, b) => {
      const dateA = new Date(a.sendDate.replace(/(\d{2})-(\d{2})-(\d{2})/, '20$3-$2-$1'));
      const dateB = new Date(b.sendDate.replace(/(\d{2})-(\d{2})-(\d{2})/, '20$3-$2-$1'));
      return dateA - dateB;
    });
  
    res.json(energyData); // Send the sorted data
  } catch (error) {
    console.error('Error fetching energy data:', error);
    res.status(500).json({ error: 'Failed to fetch energy data' });
  }
  
});



app.get('/api/predicted_appliance_consumption', async (req, res) => {
  try {
    const date = '21-10-24'; // Fixed date for the query

    // Query the database for records matching the specified date
    const predictions = await PredictedApplianceConsumption.find({ date });

    if (predictions.length === 0) {
      return res.status(404).json({ message: 'No predictions found for the given date' });
    }

    res.json(predictions); // Send the fetched predictions
  } catch (error) {
    console.error('Error fetching appliance consumption:', error);
    res.status(500).json({ error: 'Failed to fetch appliance consumption' });
  }
});

// Appliance Consumption Data route
app.get('/api/consumptions', async (req, res) => {
  try {
    const data = await Consumption.find({});
    res.json(data);
  } catch (error) {
    console.error('Error fetching consumption data:', error);
    res.status(500).json({ error: 'Failed to fetch consumption data' });
  }
});

// Predicted Solar Energy route
app.get('/api/predicted_solar_energy', async (req, res) => {
  try {
    const date = '21-10-2024';  // Fixed date for fetching predictions
  
    // Query the database for records matching the fixed date
    const predictions = await PredictedSolarEnergy.find({ date });
  
    if (predictions.length === 0) {
      return res.status(404).json({ message: 'No predictions found for the given date' });
    }
  
    // Sort predictions by the 'hour' field in ascending order
    predictions.sort((a, b) => a.hour - b.hour);
  
    res.json(predictions); // Send the sorted predictions
  } catch (error) {
    console.error('Error fetching predicted solar energy:', error);
    res.status(500).json({ error: 'Failed to fetch predicted solar energy' });
  }
  
});

app.get('/api/savings', async (req, res) => {
  try {
    const savingsData = await Savings.find(); // Fetch all savings data
  
    if (savingsData.length === 0) {
      return res.status(404).json({ message: 'No savings data found' });
    }
  
    // Sort savingsData by extracting the starting hour
    savingsData.sort((a, b) => {
      const hourA = parseInt(a.hour.split(':')[0]);
      const hourB = parseInt(b.hour.split(':')[0]);
      return hourA - hourB;
    });
  
    res.json(savingsData); // Send the sorted savings data
  } catch (error) {
    console.error('Error fetching savings data:', error);
    res.status(500).json({ error: 'Failed to fetch savings data' });
  }
  
});




// Handle invalid routes
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
