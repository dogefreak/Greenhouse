#!/usr/bin/python3

#Imports:
try:
        import paho.mqtt.client as mqtt
        import websocket
        import json, csv, base64, sys, logging, time, os
        from datetime import datetime
        from threading import Thread 
        from configparser import ConfigParser
        
except:
        print("Missing critical package, or maybe you forgot to run 'pip install requirements.txt'")

VER  = "2021-05-24 v1.3"
print(os.path.basename(__file__) + " " + VER)

#Global variables
User = "APPLICATION@ttn"
Password = "FILL ME IN (TTN MQTT API KEY)"
Region = "EU1"
nodeName = "FILL ME IN (END DEVICE NAME)"
topic  = "v3/" + User + "/devices/" + nodeName +"/down/push"
OnlineDB = "FILL ME IN (API KEY)"
UseSSL = False #Use True while using Linux or fetch certs yourself

wsMessage = ""
here = os.path.dirname(os.path.abspath(__file__))
configpath = os.path.join(here, 'config.ini')

#Read settings from config file, or create file
def settings():   
    config = ConfigParser()
    
    #Create config file if it doesn't exist
    def checkcreate(message):
        global User, Password, Region, nodeName, OnlineDB, UseSSL
        if not os.path.exists('config.ini'):
            config['Configuration'] = {'Username': str(User),
                                       'Password': str(Password),
                                       'Region': str(Region),
                                       'EndDevice': str(nodeName),
                                       'OnlineDB': str(OnlineDB),
                                       'UseSSL': str(UseSSL)
                                       }
            with open(configpath, 'w') as configfile:
                config.write(configfile)
                print(message)
        

    checkcreate("Config file was written in same path as this script!\n")

    #Read config file and assign variables
    def readconfig():
        global User, Password, Region, nodeName, OnlineDB, UseSSL
        config.read(configpath)

        User = config.get('Configuration', 'Username')
        Password = config.get('Configuration', 'Password')
        Region = config.get('Configuration', 'Region')
        nodeName = config.get('Configuration', 'EndDevice')
        OnlineDB = config.get('Configuration', 'OnlineDB')
        UseSSL = config.getboolean('Configuration', 'UseSSL')
        topic  = "v3/" + User + "/devices/" + nodeName +"/down/push"

    #Try to read config, if exception: remove config and create new one and read it again
    try: readconfig()
    except:
        os.remove('config.ini')
        checkcreate("Corrupted file detected, created new config!\n\n")
        readconfig()

# MQTT event functions
def on_connect_mqtt(mqttc, obj, flags, rc):
        #print("\nConnect: rc = " + str(rc))
        pass

def on_message_mqtt (mqttc, obj, msg):
        global uplink, ws, wsMessage
        parsedJSON = json.loads(msg.payload)
        
        #print("\nMessage: " + msg.topic + " " + str(msg.qos)) # + " " + str(msg.payload))
        #print(parsedJSON)
        #print(json.dumps(parsedJSON, indent=4))	# Uncomment this to fill your terminal screen with JSON
        
        uplink =  "uplink_message" in parsedJSON
        if uplink:
                temperature = parsedJSON['uplink_message']['decoded_payload']['Temperature']
                humidity = parsedJSON['uplink_message']['decoded_payload']['Humidity']
                battery = parsedJSON['uplink_message']['decoded_payload']['Battery']
                solar = parsedJSON['uplink_message']['decoded_payload']['Solar']
                water = parsedJSON['uplink_message']['decoded_payload']['Water']
                soil0 = parsedJSON['uplink_message']['decoded_payload']['Soil0']
                soil1 = parsedJSON['uplink_message']['decoded_payload']['Soil1']
                soil2 = parsedJSON['uplink_message']['decoded_payload']['Soil2']
                soil3 = parsedJSON['uplink_message']['decoded_payload']['Soil3']
                
                if soil0 != "NaN" or "":
                        soilAvg = (soil0 + soil1 + soil2 + soil3) / 4
                        soilPerc = (soilAvg / 1023) * 100
                else: soilPerc = 0
                
                print("\nMQTT:", parsedJSON['received_at'],"- Temperature:", temperature, "Humidity:", humidity, "Battery:", battery, "Solar:", solar)
                
                wsMessage = '{"temp": "' + str(temperature) + '", "hum": "' + str(humidity) + '", "soc_batt": "' + str(battery) + '", "soc_solar": "' + str(solar) +'", "hum_soil":"' + str(soilPerc) + '", "temp_water":"' + str(water) +'"}'

                ws.send(wsMessage)

                uplink = False

def on_publish_mqtt(mqttc, obj, mid):
        print("\nMQTT: Message published to TTN...")
        pass

def on_subscribe_mqtt(mqttc, obj, mid, granted_qos):
    #print("\nSubscribe: " + str(mid) + " " + str(granted_qos))
        pass

def on_log_mqtt(mqttc, obj, level, string):
    print("\nLog: "+ string)
    logging_level = mqtt.LOGGING_LEVEL[level]
    logging.log(logging_level, string)

def MQTT(threadname):
    #Init mqtt client
    global UseSSL, uri, ws, wsMessage
    mqttc = mqtt.Client()

    #Assign callbacks
    mqttc.on_connect = on_connect_mqtt
    mqttc.on_subscribe = on_subscribe_mqtt
    mqttc.on_message = on_message_mqtt
    mqttc.on_publish = on_publish_mqtt
    #mqttc.on_log = on_log_mqtt		# Logging for debugging OK, waste

    #Connect to TTN and OnlineDB
    mqttc.username_pw_set(User, Password)

    if UseSSL:
            # IMPORTANT - this enables the encryption of messages
            mqttc.tls_set()	# default certification authority of the system

            #mqttc.tls_set(ca_certs="mqtt-ca.pem") # Use this if you get security errors
            # It loads the TTI security certificate. Download it from their website from this page: 
            # https://www.thethingsnetwork.org/docs/applications/mqtt/api/index.html
            # This is normally required if you are running the script on Windows
            port = 8883         
    else: port = 1883


    mqttc.connect(Region.lower() + ".cloud.thethings.network", port, 60)

    #Subscribe all device uplinks
    mqttc.subscribe("#", 0)
    
    #Run infinitely
    try:    
            run = True
            while run:
                    mqttc.loop(1) # seconds timeout / blocking time
                    #print("#", end="\n", flush=True)	# feedback to the user that something is actually happening
                    
                    if "dev" in wsMessage:
                        downlink = "";
                        if "pump" in wsMessage:
                                if "start" in wsMessage: downlink = "AA==" #0
                                if "stop" in wsMessage: downlink = "AQ==" #1
                        if "tank" in wsMessage:
                                if "start" in wsMessage: downlink = "AA==" #0
                                if "stop" in wsMessage: downlink = "AQ==" #1
                        if "plants" in wsMessage:
                                if "start" in wsMessage: downlink = "Ag==" #2
                                if "stop" in wsMessage: downlink = "Aw==" #3
                        if "all" in wsMessage: toEncode = "BA==" #4
   
                        message  = '{"downlinks":[{"f_port": 1,"frm_payload":"' + downlink + '","priority": "NORMAL"}]}'
                        mqttc.publish(topic,message)
                        wsMessage = "0"
        
    except KeyboardInterrupt:
        print("Exit")
        sys.exit(0)

#---------------------------------------------------------------------------------------------------------------------------


def on_message_ws(ws, message):
    global wsMessage
    wsMessage = message
    print(f"OnlineDB: {wsMessage}")
    if "Sorry" in message:
            time.sleep(2)
            exit()
        

def on_error_ws(ws, error):
    print(error)

def on_close_ws(ws):
    print("### WebSocket closed ###")

def on_open_ws(ws):
    print("### WebSocket opened ###")


def websocket_thread(threadname):
    global ws, UseSSL, test
    if UseSSL: uri = "wss://onlinedb.net/" + OnlineDB + "/socket"
    else: uri = "ws://onlinedb.net/" + OnlineDB + "/socket"
    while 1:
        ws = websocket.WebSocketApp(str(uri),
                                  on_message = on_message_ws,
                                  on_error = on_error_ws,
                                  on_close = on_close_ws)
        ws.on_open = on_open_ws
        ws.run_forever()
        time.sleep(10)
        print("Reconnecting to websocket...");

def main():
        settings()
        try:          
                thread1 = Thread( target=MQTT, args=("MQTT Thread", ) )
                thread1.start()

                thread2 = Thread( target=websocket_thread, args=("WebSocket Thread", ) )
                thread2.start()

                thread1.join()
                thread2.join()
        except:
                pass

main()        
