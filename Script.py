import time
import json
import ssl
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import dht11
import _thread

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Read data using pin 17 for DHT11 sensor
instance = dht11.DHT11(pin=17)

def on_connect(client, userdata, flags, rc):
    print("Connected to AWS IoT: " + str(rc))

# Create secure communication
client = mqtt.Client()
client.on_connect = on_connect
client.tls_set(ca_certs='./AmazonRootCA1.pem', certfile='./certificate.pem.crt', keyfile='./private.pem.key', tls_version=ssl.PROTOCOL_SSLv23)
client.tls_insecure_set(False)
client.connect("link.amazonaws.com", 8883, 60)

# Publish data to MQTT topic
def publishData(txt):
    print(txt)
    while True:
        try:
            result = instance.read()
            if result.is_valid():
                temperature = int(result.temperature)
                humidity = int(result.humidity)
                DeviceName = "LivingRoom"
                print("------------------------")

                print("Temperature:", temperature, "°C")
                print("Humidity:", humidity, "%")
                print("DeviceName:", DeviceName)
                client.publish("raspi/tempsense", payload=json.dumps({"DeviceName": DeviceName, "Temperature": temperature, "Humidity": humidity}), qos=1, retain=False)
        except Exception as e:
            print("An error occurred:", e)
        time.sleep(5)

# Spin-up new Thread
try:
    _thread.start_new_thread(publishData, ("Spin-up new Thread...",))
    client.loop_forever()
except KeyboardInterrupt:
    print("\nScript terminated by user.")