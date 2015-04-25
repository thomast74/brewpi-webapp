# Change Log for Oink Brew Web App 


v0.2
----
- Receive new Device message from Spark and add device to database
- Receive disconnect Device message from Spark and unallocated device from Spark and configuration


v0.1
----
- receive Json Status message from oinkbrew_listener and insert new BrewPi Sparks or update them in database
- after status message from Spark received a check is executed and eventually the Spark updated with stored configuration from Web App
- receive POST spark reset request and send it over to specific Spark provided in Url
- receive POST spark set_mode and send new mode over to specific Spark provided in Url
- receive POST spark set_name and send new name over to specific Spark provided in Url
- Request a list of all Sparks with result in Json format
- Delete an existing Spark with resetting the Spark first
- receive device(actuator/sensor) list from Spark specified in URL and store in database
- Receive the Spark date time setting and store in the database
- Send the web server date time as part of the Spark Info message
- Toggle Device Actuator on a specific Spark provided in URL and return new state, for PWM you need to provide a value
- Request Sensor/Actuator status from a specific Spark provided URL
- Delete a Sensor/Actuator from local database and remotely from spark
- Receive Sensor/Actuator log data from Spark and save in InfluxDB
- List all log data entries for a specific Spark and configuration, allows to filter data with limit=m result by minutes or limit=ALL for everything