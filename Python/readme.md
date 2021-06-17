# Python3 based MQTT to Websocket broker
## Introduction & purpose
The sole purpose of this tool is to run externally on a server, to translate the MQTT messages sent and received by The Things Network V3. 
This translation will result in a message being posted or fetched from a Websocket connection to OnlineDB.NET.
## Precautions
This script will only run properly if you have the following tables in your OnlineDB.NET database:
* id	
* received	
* temp	
* hum	
* hum_soil
* soc_batt	
* soc_solar	
* temp_water	
* dev	
* req
Please take this into account, or modify the script to your liking! 
If you modify the script I will be not held responsible or accountable for any damages caused by it or any of your modifications.
Don't forget that this script will only run on TTN/TTS V3 and will not be developed any further to include support for V2, mainly because of its deprication.
The script has been developed to be deployed on Linux distributions (e.g. Ubuntu), and other operating systems are supported too. 
While running this script on other operating systems please note that you have to fetch any SSL certificates manually for using encryption (which is advised!).
For testing purposed you can temporarily disable SSL in the configuration file, but it's ill-advised to run it permanently in that way.
## How to use
The first step is to install the required packages used by the script by running the following command:
```
pip install -r /path/to/requirements.txt
```
Now that the packages have been installed, run the script once. It should open and create a config file in the same path as the location of the script.
```
python3 /path/to/mqttbroker.py
```
After that it should exit, which is expected behaviour. Open 'config.ini' using nano:
```
nano /path/to/config.ini
```
The configuration file should look similar to this:
```
[Configuration]
username = APPLICATION@ttn
password = FILL ME IN (TTN MQTT API KEY)
region = EU1
enddevice = FILL ME IN (END DEVICE NAME)
onlinedb = FILL ME IN (API KEY)
usessl = False
```
Now fill in the configuration file with your credentials, enable the SSL if you're on Linux and save it.
Run the script again and test it! It should work now.

