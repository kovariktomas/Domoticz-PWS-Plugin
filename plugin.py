#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Personal Weather Station
#
# Author: Xorfor
#

"""
<plugin key="xfr_pws" name="PWS" author="Xorfor" version="1.0.8" wikilink="https://github.com/Xorfor/Domoticz-PWS-Plugin">
    <params>
        <param field="Address" label="Port" width="40px" required="true" default="5000"/>
        <param field="Mode6" label="Debug" width="100px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
from enum import IntEnum, unique  # , auto


@unique
class unit(IntEnum):
    """
        Device Unit numbers

        Define here your units numbers. These can be used to update your devices.
        Be sure the these have a unique number!
    """

    TEMP_IND = 1
    THB = 2
    HUMIDITY = 3
    WIND1 = 4
    TEMP_HUM = 5
    RAIN = 6
    SOLAR = 7
    UVI = 8
    DEWPOINT = 9
    WIND2 = 10
    CHILL = 11
    WINDSPEED = 12
    GUST = 13
    TEMP = 14
    HUMIDITY_IND = 15
    UV_ALERT = 16
    WIND_DIRECTION = 17
    STATION = 20
    BARO_REL = 21
    BARO_ABS = 22
    RAIN_RATE = 23


@unique
class used(IntEnum):
    """
        Constants which can be used to create the devices. Look at onStart where 
        the devices are created.
            used.NO, the user has to add this device manually
            used.YES, the device will be directly available
    """

    NO = 0
    YES = 1


class BasePlugin:
    #
    # Devices

    __UNITS = [
        # id, name, type, subtype, options, used
        [unit.TEMP_IND, "Temperature (indoor)", 80, 5, {}, used.YES],
        [unit.TEMP, "Temperature", 80, 5, {}, used.YES],
        [unit.DEWPOINT, "Dew point", 80, 5, {}, used.YES],
        [unit.CHILL, "Chill", 80, 5, {}, used.YES],
        [unit.HUMIDITY, "Humidity", 81, 1, {}, used.YES],
        [unit.HUMIDITY_IND, "Humidity (indoor)", 81, 1, {}, used.YES],
        [unit.TEMP_HUM, "Temp + Hum", 82, 1, {}, used.YES],
        [unit.THB, "THB", 84, 1, {}, used.YES],
        [unit.RAIN, "Rain", 85, 1, {}, used.YES],
        [unit.WIND1, "Wind", 86, 1, {}, used.YES],
        [unit.WIND2, "Wind", 86, 4, {}, used.YES],
        [unit.UVI, "UVI", 87, 1, {}, used.YES],
        [unit.UV_ALERT, "UV Alert", 243, 22, {}, used.YES],
        [unit.SOLAR, "Solar radiation", 243, 2, {}, used.YES],
        [unit.WINDSPEED, "Wind speed", 243, 31, {"Custom": "0;m/s"}, used.YES],
        [unit.WIND_DIRECTION, "Wind direction", 243, 31, {"Custom": "0;°"}, used.YES],
        [unit.GUST, "Gust", 243, 31, {"Custom": "0;m/s"}, used.YES],
        [unit.STATION, "Station", 243, 19, {}, used.YES],
        [unit.BARO_REL, "Barometer (relative)", 243, 26, {}, used.YES],
        [unit.BARO_ABS, "Barometer (absolute)", 243, 26, {}, used.YES],
        [unit.RAIN_RATE, "Rain rate", 243, 31, {"Custom": "0;mm/h"}, used.YES],
    ]

    def __init__(self):
        self.enabled = False
        self.httpServerConn = None
        self.httpServerConns = {}
        self.raincounter = None
        self.prev_dailyrainin = None

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug(
            "onConnect {}={}:{} {}-{}".format(
                Connection.Name,
                Connection.Address,
                Connection.Port,
                Status,
                Description,
            )
        )
        Domoticz.Debug(str(Connection))
        self.httpServerConns[Connection.Name] = Connection

    def onDisconnect(self, Connection):
        Domoticz.Debug(
            "onDisconnect {}={}:{}".format(
                Connection.Name, Connection.Address, Connection.Port
            )
        )
        if Connection.Name in self.httpServerConns:
            del self.httpServerConns[Connection.Name]

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat")

    def onMessage(self, Connection, Data):
        Domoticz.Debug(
            "onMessage {}={}:{}".format(
                Connection.Name, Connection.Address, Connection.Port
            )
        )
        DumpHTTPResponseToLog(Data)
        dataIsValid = False
        # Incoming Requests
        if "Verb" in Data:
            strVerb = Data["Verb"]
            strURL = Data["URL"]
            Domoticz.Debug("Request {}".format(strVerb))
            if strVerb == "GET":
                protocol = "Wunderground"
                strData = strURL.split("?")[1]
                Domoticz.Debug("strData: {}".format(strData))
                # Convert URL parameters to dict for generic update of the devices
                data = dict(item.split("=") for item in strData.split("&"))
                Domoticz.Debug("data: {}".format(data))
                if len(data) > 0:
                    dataIsValid = True
                    # Get data
                    temp = temperature_f2iso(float_or_none(data.get("tempf")))
                    tempin = temperature_f2iso(float_or_none(data.get("indoortempf")))
                    humidity = int_or_none(data.get("humidity"))
                    humidityin = int_or_none(data.get("indoorhumidity"))
                    dewpt = temperature_f2iso(float_or_none(data.get("dewptf")))
                    windchill = temperature_f2iso(float_or_none(data.get("windchillf")))
                    windspeedms = speed_mph2iso(float_or_none(data.get("windspeedmph")))
                    windgustms = speed_mph2iso(float_or_none(data.get("windgustmph")))
                    winddir = int_or_none(data.get("winddir"))
                    solarradiation = float_or_none(data.get("solarradiation"))
                    uv = float_or_none(data.get("UV"))
                    softwaretype = data.get("softwaretype")
                    baromrel = pressure_inches2iso(float_or_none(data.get("baromin")))
                    baromabs = pressure_inches2iso(
                        float_or_none(data.get("absbaromin"))
                    )
                    rainmm = 10 * distance_inch2iso(float_or_none(data.get("rainin")))
                    dailyrainmm = 10.0 * distance_inch2iso(
                        float_or_none(data.get("dailyrainin"))
                    )
            elif strVerb == "POST":
                protocol = "Ecowitt"
                Domoticz.Debug("Ecowitt protocol")
                strData = Data["Data"].decode("utf-8")
                data = dict(item.split("=") for item in strData.split("&"))
                Domoticz.Debug("data: {}".format(data))
                if len(data) > 0:
                    dataIsValid = True
                    # Get data
                    temp = temperature_f2iso(float_or_none(data.get("tempf")))
                    tempin = temperature_f2iso(float_or_none(data.get("tempinf")))
                    humidity = int_or_none(data.get("humidity"))
                    humidityin = int_or_none(data.get("humidityin"))
                    windspeedms = speed_mph2iso(float_or_none(data.get("windspeedmph")))
                    windgustms = speed_mph2iso(float_or_none(data.get("windgustmph")))
                    winddir = int_or_none(data.get("winddir"))
                    baromrel = pressure_inches2iso(
                        float_or_none(data.get("baromrelin"))
                    )
                    baromabs = pressure_inches2iso(
                        float_or_none(data.get("baromabsin"))
                    )
                    rainmm = 10 * distance_inch2iso(float_or_none(data.get("rainin")))
                    dailyrainmm = 10 * distance_inch2iso(
                        float_or_none(data.get("dailyrainin"))
                    )
                    softwaretype = data.get("stationtype")
                    solarradiation = float_or_none(data.get("solarradiation"))
                    uv = float_or_none(data.get("uv"))
                    # dewpt not reported in Ecowitt
                    dewpt = (
                        dew_point(temp, humidity)
                        if data.get("dewptf") is None
                        else temperature_f2iso(float_or_none(data.get("dewptf")))
                    )
                    # windchill not reported in Ecowitt
                    windchill = (
                        wind_chill(temp, windspeedms)
                        if data.get("windchillf") is None
                        else temperature_f2iso(float_or_none(data.get("windchillf")))
                    )
            else:
                Domoticz.Error("Unknown protocol")
                dataIsValid = False
            #
            if dataIsValid:
                Domoticz.Debug("Protocol: {}".format(protocol))
                # Reset counters
                if self.raincounter is None:  # Domoticz (re)started.
                    # Try to get the original counter
                    old_values = Devices[unit.RAIN].sValue.split(";")
                    # Set Domoticz counter to 0
                    UpdateDevice(unit.RAIN, 0, "{};{}".format(0, 0))
                    if len(old_values[0]) == 0:
                        # Hardware first time
                        self.raincounter = 0
                    else:
                        # Hardware exists so get old value
                        self.raincounter = float(old_values[1]) - dailyrainmm
                    self.prev_dailyrainin = dailyrainmm
                if dailyrainmm < self.prev_dailyrainin:
                    self.raincounter += self.prev_dailyrainin
                self.prev_dailyrainin = dailyrainmm
                # Calculate statuses
                humiditystatus = humidity2status_outdoor(humidity)
                indoorhumiditystatus = humidity2status_indoor(humidityin, tempin)
                pressurestatus = pressure2status(baromrel)
                # Round calculated values for presentation
                temp = round(temp, 1) if temp is not None else None
                tempin = round(tempin, 1) if tempin is not None else None
                windspeedms = round(windspeedms, 1) if windspeedms is not None else None
                dewpt = round(dewpt, 1) if dewpt is not None else None
                windchill = round(windchill, 1) if windchill is not None else None
                windgustms = round(windgustms, 1) if windgustms is not None else None
                baromrel = round(baromrel) if baromrel is not None else None
                baromabs = round(baromabs) if baromabs is not None else None
                rainmm = round(rainmm, 2) if rainmm is not None else None
                dailyrainmm = round(dailyrainmm, 2) if dailyrainmm is not None else None
                solarradiation = round(solarradiation, 1) if solarradiation is not None else None
                # Update devices
                UpdateDevice(unit.TEMP_IND, 0, "{}".format(tempin))
                UpdateDevice(unit.TEMP, 0, "{}".format(temp))
                UpdateDevice(unit.HUMIDITY, int(humidity) if humidity is not None else 0, "{}".format(humiditystatus))
                UpdateDevice(
                    unit.HUMIDITY_IND,
                    int(humidityin) if humidityin is not None else 0,
                    "{}".format(indoorhumiditystatus),
                )
                UpdateDevice(unit.DEWPOINT, 0, "{}".format(dewpt))
                UpdateDevice(unit.CHILL, 0, "{}".format(windchill))
                UpdateDevice(
                    unit.TEMP_HUM, 0, "{};{};{}".format(temp, humidity, humiditystatus)
                )
                UpdateDevice(
                    unit.WIND1,
                    0,
                    "{};{};{};{};{};{}".format(
                        winddir,
                        bearing2status(winddir) if winddir is not None else None,
                        windspeedms * 10 if windspeedms is not None else None,
                        windgustms * 10 if windgustms is not None else None,
                        temp,
                        windchill,
                    ),
                )
                UpdateDevice(
                    unit.WIND2,
                    0,
                    "{};{};{};{};{};{}".format(
                        winddir,
                        bearing2status(winddir) if winddir is not None else None,
                        windspeedms * 10 if windspeedms is not None else None,
                        windgustms * 10 if windgustms is not None else None,
                        temp,
                        windchill,
                    ),
                )
                # Custom device, so we have to handle the alternative windspeed units
                windunit = int(Settings["WindUnit"])
                Domoticz.Debug("WindUnit: {}".format(windunit))
                UpdateDeviceOptions(unit.WINDSPEED, Options=speed2options(windunit))
                UpdateDevice(
                    unit.WINDSPEED, 0, "{}".format(speed2unit(windspeedms, windunit))
                )
                # Custom device, so we have to handle the alternative windspeed units
                UpdateDeviceOptions(unit.GUST, Options=speed2options(windunit))
                UpdateDevice(
                    unit.GUST, 0, "{}".format(speed2unit(windgustms, windunit))
                )
                UpdateDevice(unit.GUST, 0, "{}".format(windgustms))
                UpdateDevice(unit.WIND_DIRECTION, 0, "{}".format(winddir))
                UpdateDevice(
                    unit.SOLAR, int(solarradiation) if solarradiation is not None else 0, "{}".format(solarradiation)
                )
                UpdateDevice(unit.UVI, int(uv) if uv is not None else 0, "{};{}".format(uv, temp))
                UpdateDevice(unit.UV_ALERT, uv2status(uv) if uv is not None else 0, "{} UVI".format(uv))
                UpdateDevice(
                    unit.STATION,
                    0,
                    "{} ({}): {}".format(Connection.Address, softwaretype, protocol),
                )
                UpdateDevice(
                    unit.THB,
                    0,
                    "{};{};{};{};{}".format(
                        temp, humidity, humiditystatus, baromrel, pressurestatus
                    ),
                )
                UpdateDevice(unit.BARO_REL, 0, "{};{}".format(baromrel, pressurestatus))
                UpdateDevice(
                    unit.BARO_ABS,
                    0,
                    "{};{}".format(baromabs, pressure2status(baromabs)),
                )
                UpdateDevice(
                    unit.RAIN,
                    0,
                    "{};{}".format(
                        rainmm * 100, round(self.raincounter + dailyrainmm, 3)
                    ),
                    AlwaysUpdate=True,
                )
                UpdateDevice(unit.RAIN_RATE, 0, "{}".format(rainmm))

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        else:
            Domoticz.Debugging(0)
        Domoticz.Debug("onStart")
        # Devices
        for unit in self.__UNITS:
            if unit[0] not in Devices:
                Domoticz.Device(
                    Unit=unit[0],
                    Name=unit[1],
                    Type=unit[2],
                    Subtype=unit[3],
                    Options=unit[4],
                    Used=unit[5],
                ).Create()
        # Connections
        self.httpServerConn = Domoticz.Connection(
            Name="Server",
            Transport="TCP/IP",
            Protocol="HTTP",
            Port=Parameters["Address"],
        )
        self.httpServerConn.Listen()
        Domoticz.Debug("Listening to port: {}".format(Parameters["Address"]))


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


################################################################################
# Generic helper functions
################################################################################
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: {}".format(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           {} - {}".format(x, Devices[x]))
        Domoticz.Debug("Device ID:        {}".format(Devices[x].ID))
        Domoticz.Debug("Device Name:     '{}'".format(Devices[x].Name))
        Domoticz.Debug("Device nValue:    {}".format(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '{}'".format(Devices[x].sValue))
        Domoticz.Debug("Device LastLevel: {}".format(Devices[x].LastLevel))


def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Debug("HTTP Details ({}):".format(len(httpDict)))
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Debug("    '{}' ({}):".format(x, len(httpDict[x])))
                for y in httpDict[x]:
                    Domoticz.Debug("        '{}': '{}'".format(y, httpDict[x][y]))
            else:
                Domoticz.Debug("    '{}: '{}'".format(x, httpDict[x]))


def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Unit in Devices:
        if (
            Devices[Unit].nValue != nValue
            or Devices[Unit].sValue != sValue
            or Devices[Unit].TimedOut != TimedOut
            or AlwaysUpdate
        ):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug(
                "Update {}: {} - {} - {}".format(
                    Devices[Unit].Name, nValue, sValue, TimedOut
                )
            )


def UpdateDeviceOptions(Unit, Options={}):
    if Unit in Devices:
        if Devices[Unit].Options != Options:
            Devices[Unit].Update(
                nValue=Devices[Unit].nValue,
                sValue=Devices[Unit].sValue,
                Options=Options,
            )
            Domoticz.Debug(
                "Device Options update: {}={}".format(Devices[Unit].Name, Options)
            )


################################################################################
# Plugin functions
################################################################################
HUMIDITY_NORMAL = 0
HUMIDITY_COMFORTABLE = 1
HUMIDITY_DRY = 2
HUMIDITY_WET = 3

# Based on Mollier diagram (simplified)
def humidity2status_indoor(hlevel, temperature):
    if hlevel is None or temperature is None:
        return None
    if hlevel <= 30:
        return HUMIDITY_DRY
    if 35 <= hlevel <= 65 and 18 <= temperature <= 22:
        return HUMIDITY_COMFORTABLE
    if hlevel >= 70:
        return HUMIDITY_WET
    return HUMIDITY_NORMAL


def humidity2status_outdoor(value):
    if value is None:
        return None
    if value < 25:
        return HUMIDITY_DRY
    if 25 <= value <= 60:
        return HUMIDITY_COMFORTABLE
    if value > 60:
        return HUMIDITY_WET
    return HUMIDITY_NORMAL


def temperature_f2iso(value):
    """Temperature conversion from Fahrenheit to ISO (Celsius)
    Args:
        value (float): temperature in Fahrenheit
    Returns:
        temperature in Celsius
    """
    if value is None:
        return None
    else:
        return (value - 32) / 1.8


def speed_mph2iso(value):
    """Speed conversion from mp/h to ISO (m/s)
    Args:
        value (float): speed in mp/h
    Returns:
        speed in m/s
    """
    if value is None:
        return None
    else:
        return value * 0.44704


def bearing2status(d):
    """
    Based on https://gist.github.com/RobertSudwarts/acf8df23a16afdb5837f
    """
    dirs = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    count = len(dirs)  # Number of entries in list
    step = 360 / count  # Wind direction is in steps of 22.5 degrees (360/16)
    ix = int((d + (step / 2)) / step)  # Calculate index in the list
    return dirs[ix % count]


BARO_FORECAST_NOINFO = 0
BARO_FORECAST_SUNNY = 1
BARO_FORECAST_PARTLYCLOUDY = 2
BARO_FORECAST_CLOUDY = 3
BARO_FORECAST_RAIN = 4
BARO_FORECAST_UNKNOWN = 5
BARO_FORECASTS = {
    BARO_FORECAST_NOINFO,
    BARO_FORECAST_SUNNY,
    BARO_FORECAST_PARTLYCLOUDY,
    BARO_FORECAST_CLOUDY,
    BARO_FORECAST_RAIN,
}


def pressure2status(value):
    if value is None:
        return None
    if value < 1000:
        return BARO_FORECAST_RAIN
    elif value < 1020:
        return BARO_FORECAST_CLOUDY
    elif value < 1030:
        return BARO_FORECAST_PARTLYCLOUDY
    else:
        return BARO_FORECAST_SUNNY


def uv2status(value):
    if value is None:
        return None
    if value < 3:
        return 0
    elif value < 6:
        return 1
    elif value < 8:
        return 2
    elif value < 11:
        return 3
    else:
        return 4


def pressure_inches2iso(value):
    """Pressure conversion from inches Hg to ISO (hPa)
    Args:
        value (float): pressure in inches Hg
    Returns:
        pressure in hPa
    """
    if value is None:
        return None
    else:
        return value * 33.86


def distance_inch2iso(value):
    """Distance conversion from inches to ISO (cm)
    Args:
        value (float): Distance in inches
    Returns:
        Distance in cm
    """
    if value is None:
        return None
    else:
        return value * 2.54


def dew_point(t, h):
    """Calculate dewpoint
    Args:
        t (float): temperature in °C
        h (float): relative humidity in %
    Returns:
        calculated dewpoint in °C
    Ref:
        https://www.ajdesigner.com/phphumidity/dewpoint_equation_dewpoint_temperature.php
    """
    return round((h / 100) ** (1 / 8) * (112 + 0.9 * t) + 0.1 * t - 112, 2)


def wind_chill(t, v):
    """ Windchill temperature is defined only for temperatures at or below 10 °C 
    and wind speeds above 4.8 kilometres per hour.
    Args:
        t: temperature in °C
        v: wind speed in m/s
    Returns:
        calculated windchill temperature in °C
    Ref: 
        https://en.wikipedia.org/wiki/Wind_chill
    """
    # Calculation expects km/h instead of m/s, so
    v = v * 3.6
    if t < 10 and v > 4.8:
        v = v ** 0.16
        return round(13.12 + 0.6215 * t - 11.37 * v + 0.3965 * t * v, 1)
    else:
        return t


WIND_SPEED_MS = 0
WIND_SPEED_KMH = 1
WIND_SPEED_MPH = 2
WIND_SPEED_KNOTS = 3
WIND_SPEED_BEAUFORT = 4
WIND_SPEED_ISO = WIND_SPEED_MS
WIND_SPEEDS = {
    WIND_SPEED_MS,
    WIND_SPEED_KMH,
    WIND_SPEED_MPH,
    WIND_SPEED_KNOTS,
    WIND_SPEED_BEAUFORT,
}


def speed2unit(speed, unit):
    """Convert the windspeed (in m/s) to the given unit
    Args:
        speed: windspeed in m/s
        unit: the new unit for windspeed
    Returns:
        calculated windspeed for the given unit
    """
    if unit in WIND_SPEEDS:
        if unit == WIND_SPEED_ISO:
            return speed
        elif unit == WIND_SPEED_KMH:
            return round(speed * 3.60000000, 1)
        elif unit == WIND_SPEED_MPH:
            return round(speed * 2.23693629, 1)
        elif unit == WIND_SPEED_KNOTS:
            return round(speed * 1.94384449, 1)
        elif unit == WIND_SPEED_BEAUFORT:
            if 0 <= speed < 0.3:
                return 0
            elif 0.3 <= speed < 1.6:
                return 1
            elif 1.6 <= speed < 3.4:
                return 2
            elif 3.4 <= speed < 5.5:
                return 3
            elif 5.5 <= speed < 8.0:
                return 4
            elif 8.0 <= speed < 10.8:
                return 5
            elif 10.8 <= speed < 13.9:
                return 6
            elif 13.9 <= speed < 17.2:
                return 7
            elif 17.2 <= speed < 20.8:
                return 8
            elif 20.8 <= speed < 24.5:
                return 9
            elif 24.5 <= speed < 28.5:
                return 10
            elif 28.5 <= speed < 32.7:
                return 11
            elif 32.7 <= speed:
                return 12
        else:
            return None
    else:
        return None


def speed2options(unit):
    if unit in WIND_SPEEDS:
        if unit == WIND_SPEED_ISO:
            return {"Custom": "0;m/s"}
        elif unit == WIND_SPEED_KMH:
            return {"Custom": "0;km/h"}
        elif unit == WIND_SPEED_MPH:
            return {"Custom": "0;mph"}
        elif unit == WIND_SPEED_KNOTS:
            return {"Custom": "0;kn"}
        elif unit == WIND_SPEED_BEAUFORT:
            return {"Custom": "0;bf"}
        else:
            return {}
    else:
        return {}


def float_or_none(value):
    try:
        return float(value)
    except:
        return None


def int_or_none(value):
    try:
        return int(value)
    except:
        return None
