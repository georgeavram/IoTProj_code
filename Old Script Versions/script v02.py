import os
import time
import paho.mqtt.client as mqtt
import ssl
import json
import _thread
import dht11
import RPi.GPIO as GPIO

# Starts GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# read data using pin 17 for DHT11 sensor
instance = dht11.DHT11(pin=17)

def on_connect(client, userdata, flags, rc):
    print("Connected to AWS IoT: " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect
client.tls_set(ca_certs='./AmazonRootCA1.pem', certfile='./certificate.pem.crt', keyfile='./private.pem.key', tls_version=ssl.PROTOCOL_SSLv23)
client.tls_insecure_set(False)
client.connect("a1a1qi25dvl0jn-ats.iot.us-east-1.amazonaws.com", 8883, 60)

def get_time():
    current_time = time.time()
    formatted_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(current_time))
    return formatted_time

def publishData(txt):
    print(txt)
    while True:
        try:
            result = instance.read()
            if result.is_valid():
                temperature = int(result.temperature)
                humidity = int(result.humidity)
                DeviceName = "LivingRoom"
                current_time = get_time()

                print("Temperature:", temperature, "°C")
                print("Humidity:", humidity, "%")
                print("DeviceName:", DeviceName)
                print("------------------------")

                client.publish("raspi/tempsense", payload=json.dumps({"DeviceName": DeviceName, "Temperature": temperature, "Humidity": humidity, "Time": current_time}), qos=1, retain=False)
            else:
                raise ValueError("Failed to read temperature and humidity data from DHT11 sensor")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(5)
_thread.start_new_thread(publishData, ("Spin-up new Thread...",))
client.loop_forever()

