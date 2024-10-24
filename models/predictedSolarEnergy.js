class PredictedSolarEnergy {
    constructor(hour, solarEnergyGeneration, date) {
        this.hour = hour;                     // Hour of the day (0-23)
        this.solarEnergyGeneration = solarEnergyGeneration; // Predicted solar energy value
        this.date = date;                     // Date of prediction
    }
}

module.exports = PredictedSolarEnergy;
