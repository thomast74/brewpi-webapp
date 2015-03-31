# Change Log for Oink Brew Web App 


v0.1
----
- receive Json Status message from oinkbrew_listener and insert new BrewPi Sparks or update them in database
- after status message from Spark received a check is executed and eventually the Spark updated with stored configuration from Web App
- receive POST spark reset request and send it over to specific Spark provided in Url
- receive POST spark set_mode and send new mode over to specific Spark provided in Url
- receive POST spark set_name and send new name over to specific Spark provided in Url
