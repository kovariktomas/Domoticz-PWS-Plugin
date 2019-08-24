# Domoticz PWS Plugin
This Domoticz Plugin allows you to get the data directly from your own personal weather station (PWS). This plugin does NOT require that you register your PWS to WeatherUnderground, Ecowitt, WeatherCloud, etc. This plugin will directly capture the data!

## Prerequisites
Your PWS needs to support WS View

Install WS View on your device
Follow the instructions from the manual to connect your PWS to internet
Click on Next untill you are on on the Customized page (Do NOT choose for WeatherUnderground, Ecowitt, WeatherCloud, etc.)
Choose `Enable`
For `Protocol Type Same As` choose `Wunderground`
For `Server IP / Hostname` enter your Domotiz Server ip address, eg. 192.168.0.10
You can leave blank `Station ID` 
You can leave blank `Station Key`
`Port` enter a free port number, eg. `5000`
`Upload Interval`, leave it `60` seconds
Click on `Save`

## Parameters
| Name                 | Description
| :---                 | :---
| Port                 | Port number as choosen in WS View, eg. 5000

## Devices
| Name                 | Description
| :---                 | :---
| Chill                | Chill
| Dew point            | Dew point
| Gust                 | Gust
| Humidity             | Humidity
| Humidity (indoor)    | Humidity (indoor)
| Protocol             | Choose protocol in WS Tools, `Wunderground` or `Ecowitt`
| Rain                 | Current rain rate and daily total
| Software             | Software used in your PWS to send the data
| Solar radiation      | Solar radiation
| Temp + Hum           | Temperature and humidity
| Temperature          | Temperature
| Temperature (indoor) | Temperature
| THB                  | Temperature, humidity and barometer (pressure and prediction)
| UVI                  | UV index
| Wind                 | Wind direction, speed and gust
| Wind                 | Wind direction, speed, gust, temperature and gust
| Wind Speed           | Wind speed
