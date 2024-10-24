class PredictedTariff {
    constructor(hour, tariff, date) {
        this.hour = hour;            // Hour of the day (0-23)
        this.tariff = tariff;        // Predicted tariff value
        this.date = date;            // Date of prediction
    }
}

module.exports = PredictedTariff;
