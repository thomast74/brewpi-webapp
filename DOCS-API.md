Documentation about API Entry Points
====================================

Requests
--------

Impl | Entry Point | METHOD | Description
-----|-------------|--------|------------
Y | /api/spark/                                 | GET    | List all registered Sparks
N | /api/activity/                              | GET    | List recent activities from all Sparks
Y | /api/spark/{device_id}/                     | GET    | List details of one Spark
N | /api/spark/{device_id}/activity/            | GET    | List recent activities from a specific Spark
Y | /api/spark/{device_id}/devices/             | GET    | List sensor/actuator list from Spark (including remote)
Y | /api/spark/{device_id}/devices/{sensor_id}/ | GET    | List sensor/actuator details for a specific device (including remote)
Y | /api/spark/{device_id}/logs/{config_id}/    | GET    | List logged data for a specific configuration

Inserts
-------
Impl | Entry Point | METHOD | Description
-----|-------------|--------|------------
N | /api/spark/{device_id}/config               | PUT    | Creates a new configuration and sends it to the Spark
Y | /api/spark/{device_id}/devices/             | PUT    | Receives a newly connected device from Spark
Y | /api/spark/{device_id}/logs/                | PUT    | Receive actuator and sensor value data


Updates
-------

Impl | Entry Point | METHOD | Description
-----|-------------|--------|------------
Y | /api/spark/status/                                   | POST   | Receive Spark status updates and check in Spark
N | /api/spark/{device_id}/config/{config_id}            | POST   | Updates an existing configuration and sends it to the Spark
Y | /api/spark/{device_id}/name/                         | POST   | Change name of spark, used as alias
Y | /api/spark/{device_id}/mode/                         | POST   | Change mode to either [MANUAL,LOGGING,AUTOMATIC]
? | /api/spark/{device_id}/firmware/                     | POST   | Updates Spark with latest firmware
Y | /api/spark/{device_id}/reset/                        | POST   | Force Spark to reset/clear all settings
Y | /api/spark/{device_id}/devices/{actuator_id}/toggle/ | POST   | In case device is an Actuator or PWM device change the state

Deletes
-------

Impl | Entry Point | METHOD | Description
-----|-------------|--------|------------
Y | /api/spark/{device_id}/delete/                     | DELETE | Deletes a Spark and all its data from database
Y | /api/spark/{device_id}/devices/delete/             | DELETE | Deletes the Sensor that was disconnected from Spark
Y | /api/spark/{device_id}/devices/{sensor_id}/delete/ | DELETE | Deletes the Sensor/Actuator from this Sparks configuration
N | /api/spark/{device_id}/logs/{config_id}/delete/    | DELETE | Deletes the Sensors/Actuators log data
