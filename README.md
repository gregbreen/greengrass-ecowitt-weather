# greengrass-ecowitt-weather

AWS IoT Greengrass component for publishing Ecowitt weather data to AWS IoT Core

## Compatibility

Gets the Ecowitt weather "live data". This is command `0x27` in the EcoWitt Data Exchange TCP Protocol document.

This component should be generally suitable for GW1000, 1100, 1900, 2000, 2001, 2680, 2650. However, it currently only parses and supports the live data items that are returned by the GW2000 (firmware V3.0.9) in my house. Trivial to modify it to suit your needs. This has been tested with 4xWH31, 1xWN36 and 3xWH51.

## MQTT Messages

Publishes once per minute to AWS IoT Core using the [AWS IoT Greengrass IPC mechanism](https://docs.aws.amazon.com/greengrass/v2/developerguide/ipc-iot-core-mqtt.html). Example message:

```
{
  "Indoor Temperature": 27.2,
  "Indoor Humidity": 46,
  "Absolute Pressure": 1008.2,
  "Relative Pressure": 1008.2,
  "Outdoor Temperature": 32.5,
  "Outdoor Humidity": 43,
  "Wind Direction": 74,
  "Wind Speed": 0.5,
  "Gust Speed": 0.9,
  "Light": 59800.0,
  "UV": 1400,
  "UV Index": 4,
  "Soil Moisture 1": 35,
  "Soil Moisture 3": 4,
  "Temperature 1": 26.5,
  "Humidity 1": 54,
  "Temperature 2": 28.4,
  "Humidity 2": 46,
  "Temperature 3": 27.4,
  "Humidity 3": 50,
  "Temperature 4": 26.8,
  "Humidity 4": 45,
  "Temperature 5": 31.1,
  "Maximum Wind Speed": 5.9
}
```

## Repository Contents

| Item                          | Description                                                         |
| ----------------------------- | ------------------------------------------------------------------- |
| gdk-config.json               | Configuration for the Greengrass Development Kit (GDK) - Command Line Interface.                      |
| main.py                       | Greengrass component artifact source code.                          |
| recipe.yaml                   | Greengrass component recipe.                                        |

## Configuration

The component supports the following [component configuration](https://docs.aws.amazon.com/greengrass/v2/developerguide/update-component-configurations.html) options.

| Name              | Default                                              | Description |
| ----------------- | ---------------------------------------------------- | ----------- |
| gatewayAddress    | 0.0.0.0                                              | The IP address of the Ecowitt gateway. |
