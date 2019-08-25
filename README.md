# Domoticz PWS Plugin
This Domoticz Plugin allows you to get the data directly from your own personal weather station (PWS). This plugin does NOT require that you register your PWS to WeatherUnderground, Ecowitt, WeatherCloud, etc. This plugin will directly capture the data!

## Prerequisites
Your PWS needs to support WS View

1. Install WS View on your mobile device
    * [Google Play Store](https://play.google.com/store/apps/details?id=com.ost.wsview)
    * [Apple App Store](https://apps.apple.com/us/app/ws-view/id1362944193)
2. Follow the instructions from the manual to connect to your PWS
3. Click on Next untill you are on on the `Customized` page (Do NOT choose for WeatherUnderground, Ecowitt, WeatherCloud, etc.)
4. Choose `Enable`
5. For `Protocol Type Same As` choose `Wunderground`
6. For `Server IP / Hostname` enter your Domotiz Server ip address, eg. 192.168.0.10
7. If you choose for `Wunderground` protocol:
    * Fill in `Station ID` with a value
    * Fill in `Station Key` with a value
8. `Port` enter a free port number, eg. `5000`
9. `Upload Interval`, leave it `60` seconds
10. Click on `Save`

## Parameters
| Name                 | Description
| :---                 | :---
| Port                 | Port number as choosen in WS View, eg. 5000

## Devices
![Devices](/images/screendump.jpg)

| Name                 | Description
| :---                 | :---
| Chill                | Chill (calculated when `Ecowitt` protocol is used)
| Dew point            | Dew point (calculated when `Ecowitt` protocol is used)
| Gust                 | Gust
| Humidity             | Humidity
| Humidity (indoor)    | Humidity (indoor)
| Rain                 | Current rain rate and daily total
| Station              | ip adress:port from your PWS (Software): Protocol (`Wunderground` or `Ecowitt`)
| Solar radiation      | Solar radiation
| Temp + Hum           | Temperature and humidity
| Temperature          | Temperature
| Temperature (indoor) | Temperature
| THB                  | Temperature, humidity and barometer (pressure and prediction)
| UVI                  | UV index
| Wind                 | Wind direction, speed and gust
| Wind                 | Wind direction, speed, gust, temperature and gust
| Wind Speed           | Wind speed
