import adafruit_dht
import board
from time import sleep
# from datetime import datetime
# import time

from gpiozero import LED 
# from signal import pause
# import RPi.GPIO as GPIO

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

import logging
import json
import argparse
import busio

led = LED(19)
led_green = LED(21)

# Function called when a shadow is updated
def customShadowCallback_Update(payload, responseStatus, token):

    # Display status and data from update request
    # if responseStatus == "timeout":
    #     print("Update request " + token + " time out!")

    # if responseStatus == "accepted":
    #     payloadDict = json.loads(payload)
    #     print("~~~~~~~~~~~~~~~~~~~~~~~")
    #     print("Update request with token: " + token + " accepted!")

    #     # print(payloadDict)
    #     print("moisture: " + str(payloadDict["state"]["reported"]["moisture"]))
    #     # print("temperature: " + str(payloadDict["state"]["reported"]["temp"]))
    #     print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    # if responseStatus == "rejected":
    #     print("Update request " + token + " rejected!")
    pass

# Function called when a shadow is deleted
def customShadowCallback_Delete(payload, responseStatus, token):

     # Display status and data from delete request
    # if responseStatus == "timeout":
    #     print("Delete request " + token + " time out!")

    # if responseStatus == "accepted":
    #     print("~~~~~~~~~~~~~~~~~~~~~~~")
    #     print("Delete request with token: " + token + " accepted!")
    #     print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    # if responseStatus == "rejected":
    #     print("Delete request " + token + " rejected!")
    pass


# Read in command-line parameters
def parseArgs():

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your device data endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
    parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicShadowUpdater", help="Targeted client id")

    args = parser.parse_args()
    return args


# Configure logging
# AWSIoTMQTTShadowClient writes data to the log
def configureLogging():

    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)


# Parse command line arguments
args = parseArgs()

# if not args.certificatePath or not args.privateKeyPath:
#     parser.error("Missing credentials for authentication.")
#     exit(2)

# If no --port argument is passed, default to 8883
if not args.port: 
    args.port = 8883


# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(args.clientId)
myAWSIoTMQTTShadowClient.configureEndpoint(args.host, args.port)
myAWSIoTMQTTShadowClient.configureCredentials(args.rootCAPath, args.privateKeyPath, args.certificatePath)

# AWSIoTMQTTShadowClient connection configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10) # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5) # 5 sec

# Initialize Raspberry Pi's I2C interface
# i2c_bus = busio.I2C(SCL, SDA)

# Intialize SeeSaw, Adafruit's Circuit Python library
sensor = adafruit_dht.DHT11(board.D18)

# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a device shadow handler, use this to update and delete shadow document
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(args.thingName, True)

# Delete current shadow JSON doc
deviceShadowHandler.shadowDelete(customShadowCallback_Delete, 5)

# while True:
#     moistureLevel = sensor.humidity     
#     print("현재 습도:{}%".format(moistureLevel))
#     print("-------------------------------------------------")    
#     sleep(3)

humidity_machine = False
# Read data from moisture sensor and update shadow
while True:
    
    try:
        # read moisture level through capacitive touch pad
        moistureLevel = sensor.humidity     
        
        if humidity_machine:
            if moistureLevel <= 45:
                humidity_machine = False
                led_green.off()
                print("습도조절 완료")         
                print("-------------------------------------------------")   
                sleep(5)          
            continue
        if moistureLevel >= 55:
            humidity_machine = True
            # # Display moisture
            print("현재 습도:{}%".format(moistureLevel))
            print("옷장습도가 높습니다. 제습기를 가동합니다") 
            print("-------------------------------------------------") 
        
            # Create message payload
            payload = {"state":{"reported":{"moisture":str(moistureLevel)}}}
            # payload = {"옷장습도:{}, 습도가 높습니다. 제습기를 가동합니다%".fromat(moistureLevel)}
    
            # Update shadow
            deviceShadowHandler.shadowUpdate(json.dumps(payload), customShadowCallback_Update, 5)
                           
            # while True:                
            led.on()
            sleep(0.2)
            led.off()
            sleep(0.2)
            led.on()
            sleep(0.2)
            led.off()
            sleep(0.2)
            led.on()
            sleep(0.2)
            led.off()
            sleep(0.2)
            led.on()
            sleep(0.2)
            led.off()

            sleep(2)
            led_green.on()
            sleep(5)
      
    # 예외 발생시
    except RuntimeError as e:
        # print("예외가 발생하였습니다.")
        # sleep(3)
        continue 