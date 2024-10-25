These are our api endpoints :

For recent-tariffs: 
endpoint is api/tariff 
link is https://solar-dashboard-backend-1.onrender.com/api/tariffs.

For energy-data this have solarenergygeneration ,solar intensity hourly : 
endpoint is /api/energy-data  
link is https://solar-dashboard-backend-1.onrender.com/api/energy-data.

for consumptions this have appliances usage per day wise : 
endpoint is /api/consumptions  
link https://solar-dashboard-backend-1.onrender.com/api/consumptions.

//  All Predictions are made based on considering the past 30 days data from 20 sept 2024 - 20 oct 2024 and predicted for date 21 oct 2024



for predicted_tariff was based on recent-tariffs considering the tariff_rates field we predicted hourly data:  
endpoint is /api/predicted_tariffs 
Link https://solar-dashboard-backend-1.onrender.com/api/predicted_tariffs .

for predicted_solar_energy prediction was based on solar energy generation based from energy_data solarenergy generation field  we predicted hourly data :   
endpoint is /api/predicted_solar_energy 
Link https://solar-dashboard-backend-1.onrender.com/api/predicted_solar_energy

for predicted_appliances_usage prediction was based on consumptions data we predicted day wise appliances usage : endpoint /api/predicted_appliance_consumption and the Link https://solar-dashboard-backend-1.onrender.com/api/predicted_appliance_consumption

for prediction of savings and hourly scheduling  we have used  predicted_tariff , predicted_solarenergygeneration,predicted_appliances_consumption  :  
endpoint /api/savings
Link https://solar-dashboard-backend-1.onrender.com/api/savings




    
