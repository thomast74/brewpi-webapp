Documentation about API Entry Points
====================================

Requests
--------

Impl | Entry Point | METHOD | Description
-----|-------------|--------|------------
N | /api/spark                          | GET    | Request a list of all registered Sparks
N | /api/spark/{device_id}              | GET    | Request details of one Spark
N | /api/spark/{device_id}/events       | GET    | Lists activities of a specific Spark
N | /api/spark/{device_id}/devices      | GET    | Request sensor/actuator list from Spark
N | /api/spark/{device_id}/devices/{id} | GET    | Request sensor/actuator details with current value/status
N | /api/spark/{device_id}/logs/{id}    | GET    | Lists logged data for a specific sensor/actuator

Inserts
-------

Impl | Entry Point | METHOD | Description
-----|-------------|--------|------------
N | /api/spark/{device_id}/devices/{id}/save  | PUT   | Receive for a specific Sensor/Actuator data and store in database

Updates
-------

Impl | Entry Point | METHOD | Description
-----|-------------|--------|------------
Y | /api/spark/status                          | POST   | Receive Spark status updates and check in Spark
N | /api/spark/{device_id}/config              | POST   | Updates Sparks Sensor/Actuator configuration
Y | /api/spark/{device_id}/name                | POST   | Change name of spark, used as alias
Y | /api/spark/{device_id}/mode                | POST   | Change mode to either [MANUAL,LOGGING,AUTOMATIC]
- | /api/spark/{device_id}/firmware            | POST   | Updates Spark with latest firmware
Y | /api/spark/{device_id}/reset               | POST   | Force Spark to reset/clear all settings
N | /api/spark/{device_id}/devices/{id}/toggle | POST   | In case device is an Actuator or PWM device change the state

Deletes
-------

Impl | Entry Point | METHOD | Description
-----|-------------|--------|------------
N | /api/spark/{device_id}/delete              | DELETE | Deletes a Spark and all its data from database
N | /api/spark/{device_id}/devices/{id}/delete | DELETE | Deletes the Sensor/Actuator from this Sparks configuration
N | /api/spark/{device_id}/logs/{id}/delete    | DELETE | Deletes the Sensors/Actuators log data
