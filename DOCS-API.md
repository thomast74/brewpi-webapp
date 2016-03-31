Documentation about API Entry Points
====================================

BrewPi
------
Impl | Entry Point                | METHOD | Description
-----|----------------------------|--------|----------------------------------------------------------------------------
Y    | /api/brewpis/              | GET    | List all registered BrewPi's
Y    | /api/brewpis/              | POST   | Create a new BrewPi from json request
Y    | /api/brewpis/{device_id}/  | GET    | List details of BrewPi with device_id
Y    | /api/brewpis/{device_id}/  | PUT    | Update BrewPi with device_id from json request, sends message to BrewPi device
Y    | /api/brewpis/{device_id}/  | DELETE | Deletes BrewPi with device_id including actuators but excludes all OneWrite devices

Sample Json Update Request:
```
{  
  "command": "[status|update|reset]",  
  "device_id": "54ff6c066678574929420565",  
  "name": "Chamber 1",  
  "firmware_version": "0.3",  
  "ip_address": "192.168.1.11",  
  "web_address": "192.168.1.3",  
  "web_port": "80",  
  "brewpi_time": "0"  
}  
```

Logs
----
Impl | Entry Point                           | METHOD | Description
-----|---------------------------------------|--------|-----------------------------------------------------------------
Y    | /api/logs/{device_id}/                | POST   | Receive actuator and sensor value data from BrewPi with device_id
Y    | /api/logs/{device_id}/{config_id}/    | GET    | List logged data for a specific configuration and BrewPi with device_id
Y    | /api/logs/{device_id}/{config_id}/    | DELETE | Deletes the Sensors/Actuators log data for a config_id and for BrewPi with device_id

Sample Json Log Data Request:
```
{  
 "temperatures": [  
    {"pin_nr":"10","hw_address":"0000000000000000","value":200.000000},   
    {"pin_nr":"11","hw_address":"0000000000000000","value":0.000000},  
    {"pin_nr":"16","hw_address":"0000000000000000","value":0.000000},  
    {"pin_nr":"0","hw_address":"28107974060000AC","value":23.625000},  
    {"pin_nr":"0","hw_address":"280AA3730600005D","value":10.500000},  
    {"pin_nr":"0","hw_address":"2886927306000083","value":13.250000}  
  ],  
  "targets": [  
    {"config_id":2,"temperature":4.000000, "output": 23.09}  
  ]  
}  
```

Devices
-------
Impl | Entry Point                           | METHOD | Description
-----|---------------------------------------|--------|-----------------------------------------------------------------
Y    | /api/devices/                         | GET    | List sensor/actuator from database that are not attached to a BrewPi
Y    | /api/devices/{device_id}/             | GET    | List sensor/actuator from database attached to BrewPi with device_id
Y    | /api/devices/{device_id}/             | DELETE | Delete a sensor that was disconnected from BrewPi with device_id
Y    | /api/devices/{device_id}/             | PUT    | Receives a already or newly connected device from BrewPi with device_id
Y    | /api/devices/{device_id}/             | POST   | Updates device from json request attached to BrewPi with device_id
Y    | /api/devices/{device_id}/offset/      | POST   | Send offset of temp sensors to BrewPi
Y    | /api/devices/{device_id}/calibration/ | POST   | Start calibration process for provided sensors

Sample json request data:
```
{  
  "brewpi_id": "",  
  "device_type": 1,  
  "function": 1,  
  "value": 12.98,  
  "pin_nr": 0,  
  "hw_address": "00000000",  
  "offset": 1.20,  
  "offset_from_brewpi": 0.0,  
  "is_deactivate": false  
}
```


Configurations
--------------
Impl | Entry Point                           | METHOD | Description
-----|---------------------------------------|--------|-----------------------------------------------------------------
Y    | /api/configs/                         | GET    | List all configurations
Y    | /api/configs/{device_id}/             | GET    | List all configurations for a BrewPi with device_id
Y    | /api/configs/{device_id}/             | POST   | Creates a new configuration and sends it to the BrewPi
Y    | /api/configs/{device_id}/{config_id}/ | GET    | List the configuration requested by config_id
Y    | /api/configs/{device_id}/{config_id}/ | PUT    | Updates an existing configuration and sends new configuration to the BrewPi with device_id
Y    | /api/configs/{device_id}/{config_id}/ | DELETE | Deletes a configuration and sends delete request to BrewPi with device_id
Y    | /api/configs/{device_id}/request      | GET    | Device requests all stored configurations to be sent

Sample json request for a new configuration:
```
{  
  "name":"Barbatos",  
  "type":"Fermentation",  
  "fan_actuator": "Fridge Fan Actuator",  
  "cool_actuator": "Fridge Cooling Actuator",  
  "heat_actuator":"Fridge Heating Actuator",
  "pump_1_actuator": "Pump 1 Actuator",
  "pump_2_actuator": "Pump 2 Actuator",
  "temp_sensor": "Fridge Beer 1 Temp Sensor",  
  "function": {  
    "Fridge Fan Actuator": 1,  
    "Fridge Cooling Actuator": 2,  
    "Fridge Heating Actuator": 3,  
    "Outside Fridge Temp Sensor": 4,  
    "Fridge Inside Temp Sensor": 5,  
    "Fridge Beer 1 Temp Sensor": 6, 
    "Pump 1 Actuator": 7, 
    "Pump 2 Actuator": 8, 
  },  
  "phase": {  
    "temperature": 21.0,  
    "heat_pwm": 0.0,  
    "fan_pwm": 100.0,  
    "pump_1_pwm": 100.0,
    "pump_2_pwm": 0.0,
    "heating_period": 4000,
    "cooling_period": 1200000,
    "cooling_on_time": 600000,
    "cooling_off_time": 180000,
    "p": 5.0,  
    "i": 0.01,  
    "d": -3.0  
  }  
}  
```

Activities
----------
Impl | Entry Point                     | METHOD | Description
-----|---------------------------------|--------|-----------------------------------------------------------------------
N    | /api/activities/                | GET    | List recent activities from all BrewPis
N    | /api/activities/{device_id}/    | GET    | List recent activities from a specific BrewPi
