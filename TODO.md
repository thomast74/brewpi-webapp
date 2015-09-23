# To do list

## Tasks

* **send delete device request to BrewPi**  
  return error if device is part of a configuration  
    

* **Receive log messages**  
  receive request from BrewPi  
  identify BrewPi  
  identify device  
  identify configuration if assigned to configuration  
  save in graph database with all information [BrewPi,device,configuration]  
  
  
* **API request for log message should return message to be used in JavaScript charting**  
  filter by configuration  
  filter by device  
  return all data including all devices  
  
  
* **Firmware upload:**  
   use a special folder within web app for storing firmware binaries  
   part of the web app allows download of new firmware from github  
   user selects which firmware to upload  
  



## Ideas

* create webapp with basic design (header)
* shows a portlet all registered BrewPis with link to BrewPi main page
* BrewPi main page, list on top of page and on the bottom the details with something to list actions
* detail page should have tabs: Details, Devices, Action Stream
* detail page Details allows to name a BrewPi

* BrewPi connector to send data to BrewPi
* task to check BrewPis configuration version. If no configuration or older one, contact BrewPi and transfer config

* detail page Devices, lists all connected sensors and actuators
* detail page to tag a sensor or Actuator
* detail page set BrewPi mode (MANUAL, LOGGING)



* home page to list active fermentation
* home page to list Activity stream
* home page to start a new brew
* home page to start to show if a brew is active

* chart need to be able to turn on/off lines belonging to one configuration
* configuration dashboard needs to show chart from all configuration seperatly
