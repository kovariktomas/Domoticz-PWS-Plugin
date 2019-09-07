# Domoticz PWS Plugin
This Domoticz Plugin allows you to get the data directly from your own personal weather station (PWS). This plugin does NOT require that you register your PWS to WeatherUnderground, Ecowitt, WeatherCloud, etc, or use of WeeWX. This plugin will directly capture the data from your weather station!

## Prerequisites
Your PWS needs to be connected to your router by WS View (and probably also the older 'WS Tool'). With this application you can connect your PWS to the router, so that your PWS can upload weather data.

1. Install WS View on your mobile device
    * [Google Play Store](https://play.google.com/store/apps/details?id=com.ost.wsview)
    * [Apple App Store](https://apps.apple.com/us/app/ws-view/id1362944193)
1. Follow the instructions from the manual to connect your PWS to your router
1. Goto to Device List  in Menu and choose your PWS
1. Click on Next untill you are on on the `Customized` page (Do NOT choose for WeatherUnderground, Ecowitt, WeatherCloud, etc.)
1. Choose `Enable`
1. For `Protocol Type Same As` choose `Wunderground` (preferred)
1. For `Server IP / Hostname` enter your Domotiz Server ip address, eg. 192.168.0.10
1. If you choose for `Wunderground` protocol:
    * Fill in `Station ID` with a value
    * Fill in `Station Key` with a value
1. `Port` enter a free port number, eg. `5000`
1. `Upload Interval`, leave it `60` seconds
1. Click on `Save`

![Screenshot](/images/screendump2.png)

Now your PWS will start to upload its data to your Domoticz server at the specified port. Now we need to install the Domoticz plugin to created the required devices, listen to the specified port, retrieve the data and update the devices with the latest information.
Unfortunately you can connect your PWS only to one Domoticz server!

## Installation
1. Clone repository into your Domoticz plugins folder
    ```
    cd domoticz/plugins
    git clone https://github.com/Xorfor/Domoticz-PWS-Plugin.git
    ```
1. Restart domoticz
    ```
    sudo service domoticz.sh restart
    ```
1. Make sure that "Accept new Hardware Devices" is enabled in Domoticz settings
1. Go to "Hardware" page and add new hardware with Type "PWS"
1. Enter the Port number as used in WS View
1. Press Add

## Update
1. Go to plugin folder and pull new version
    ```
    cd domoticz/plugins/Domoticz-PWS-Plugin
    git pull
    ```
1. Restart domoticz
    ```
    sudo service domoticz.sh restart
    ```
If new devices are added in the plugin, you have to remove the hardware and add it again (sorry!).

## Parameters
| Name                 | Description
| :---                 | :---
| Port                 | Port number as choosen in WS View, eg. 5000 (displayed on Hardware overview as Address)

## Devices
![Devices](/images/screendump.jpg)

I have created as much devices as possible, so you can select your own favourites.

| Name                  | Description
| :---                  | :---
| Barometer (absolute)  | Pressure (absolute) in hPa
| Barometer (relative)  | Pressure (relative) in hPa
| Chill                 | Chill (calculated when `Ecowitt` protocol is used)
| Dew point             | Dew point (calculated when `Ecowitt` protocol is used)
| Gust                  | Gust
| Humidity              | Humidity
| Humidity (indoor)     | Humidity (indoor)
| Rain                  | Current rain rate and daily total
| Station               | Format: [ip adress] ([software]): [Protocol] (`Wunderground` or `Ecowitt`), from your PWS.
| Solar radiation       | Solar radiation
| Temp + Hum            | Temperature and humidity
| Temperature           | Temperature
| Temperature (indoor)  | Temperature
| THB                   | Temperature, humidity and barometer (pressure and prediction)
| UVI                   | UV index
| UV Alert              | UV index + warning level (calculated)
| Wind                  | Wind direction, speed and gust
| Wind                  | Wind direction, speed, gust, temperature and gust
| Wind Speed            | Wind speed

## Protocols
WS View supports 2 protocols for `Customized` upload: `Wunderground` or `Ecowitt`. My information about the data to be uploaded is based on my own experience and information from:

### Wunderground
Information can be found at: https://feedback.weather.com/customer/en/portal/articles/2924682-pws-upload-protocol?b_id=17298.

#### Not supported (yet)
| Name                  |
| :---                  |
| weather               |
| soiltempf             |
| soilmoisture          |
| leafwetness           |
| visibility            |
| Aq* (like AqNO, AqBC )|

### Ecowitt
Information not found yet.

## Supported devices
In general, if the station is supplied with 'EasyWeather' software, it is likely that the station will work with this Domoticz plugin!

### Ventus 
Ventus W830