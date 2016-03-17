# Change Log for Oink Brew Web App 


## v0.2

### Stories
OB-48 	Receive new Device message from BrewPi and add device to database  
OB-38 	Receive Calibration request for a specific BrewPi and a list of sensors and mark them for calibration  
OB-40 	Create a task that is called after 2 minutes to calculate the offset and send to BrewPi  
OB-42 	Verify the calibration offset values 2 minutes after offset was calculated  
OB-39 	Receive Device value data and save it into calibration data for 2 minutes  
OB-59 	Send offset stored in database to temp sensors on provided BrewPi  
  
### Improvements
OB-43 	Deleting device should not delete the device from database, just unlink from BrewPi if device is a OneWire device  
OB-41 	Make sure that request device list and single device does not update the offset  
  
### Bugs
OB-57 	Devices, especially Actuators have same PIN NR and HW ADDRESS and should not be deleted once they have been created and never unassigned from a BrewPi  
OB-54 	Receive disconnect Device message from BrewPi and unallocated device from BrewPi and configuration  
  

## v0.1
- receive Json Status message from oinkbrew_listener and insert new BrewPi BrewPis or update them in database
- after status message from BrewPi received a check is executed and eventually the BrewPi updated with stored configuration from Web App
- receive POST BrewPi reset request and send it over to specific BrewPi provided in Url
- receive POST BrewPi set_mode and send new mode over to specific BrewPi provided in Url
- receive POST BrewPi set_name and send new name over to specific BrewPi provided in Url
- Request a list of all BrewPis with result in Json format
- Delete an existing BrewPi with resetting the BrewPi first
- receive device(actuator/sensor) list from BrewPi specified in URL and store in database
- Receive the BrewPi date time setting and store in the database
- Send the web server date time as part of the BrewPi Info message
- Toggle Device Actuator on a specific BrewPi provided in URL and return new state, for PWM you need to provide a value
- Request Sensor/Actuator status from a specific BrewPi provided URL
- Delete a Sensor/Actuator from local database and remotely from BrewPi
- Receive Sensor/Actuator log data from BrewPi and save in InfluxDB
- List all log data entries for a specific BrewPi and configuration, allows to filter data with limit=m result by minutes or limit=ALL for everything