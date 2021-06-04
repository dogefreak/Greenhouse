#!/usr/bin/python3

User = "APPLICATION@ttn" #Fill in Application
Password = "NNSXS.5UPER.5ECRET.APIKEY" #Fill in MQTT API key/password
Region = "EU1" #Or US, AU...
topic  = "APPID" + "/devices/" + "DEVICEID" + "/down" #Fill in TTN APPID and DEVID
OnlineDB = "9URUQbhWBglBLnP" #Fill in OnlineDB API key
UseSSL = False

wsMessage = ""

VER  = "2021-05-24 v1.0"
import os, sys, logging, time
print(os.path.basename(__file__) + " " + VER)

#Imports:
import paho.mqtt.client as mqtt
import json
import csv
from datetime import datetime
import websocket
from threading import Thread
#import ssl


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
                
                print("\nMQTT:", parsedJSON['received_at'],"- Temperature:", temperature, "Humidity:", humidity)
                
                wsMessage = '{"temp": "' + str(temperature) + '", "hum": "' + str(humidity) + '"}'

                ws.send(wsMessage)

                uplink = False

def on_publish_mqtt(mqttc, obj, mid):
    print("\nMQTT: Message published to TTN...")

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
                    if "dev" in wsMessage:
                        mqttc.publish(topic, wsMessage)
                        wsMessage = "0"
                    #print("#", end="\n", flush=True)	# feedback to the user that something is actually happening	
        
    except KeyboardInterrupt:
        print("Exit")
        sys.exit(0)

#---------------------------------------------------------------------------------------------------------------------------


def on_message_ws(ws, message):
    global wsMessage
    wsMessage = message
    print(f"OnlineDB: {wsMessage}")
        

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
            
thread1 = Thread( target=MQTT, args=("MQTT Thread", ) )
thread1.start()

thread2 = Thread( target=websocket_thread, args=("WebSocket Thread", ) )
thread2.start()

thread1.join()
thread2.join()
