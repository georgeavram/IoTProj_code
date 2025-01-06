import os
import time
import paho.mqtt.client as mqtt
import ssl
import json
import _thread

def on_connect(client, userdata, flags, rc):
    print("Connected to AWS IOT: " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect
client.tls_set(ca_certs='./AmazonRootCA1.pem', certfile='./certificate.pem.crt', keyfile='./private.pem.key', tls_version=ssl.PROTOCOL_SSLv23)
client.tls_insecure_set(False)
client.connect("link.amazonaws.com", 8883, 60)


def read_temperature():
    try:
        # Find the DS18B20 sensor device file
        sensor_file = ''
        for device_folder in os.listdir('/sys/bus/w1/devices'):
            if device_folder.startswith('28-'):
                sensor_file = os.path.join('/sys/bus/w1/devices', device_folder, 'w1_slave')

        if not sensor_file:
            raise FileNotFoundError("DS18B20 sensor not found")

        # Read the raw temperature data from the sensor
        with open(sensor_file, 'r') as file:
            lines = file.readlines()

        # Parse the temperature value
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temperature_str = lines[1][equals_pos + 2:]
            temperature_celsius = float(temperature_str) / 1000.0
            return temperature_celsius
        else:
            raise ValueError("Error parsing temperature data")

    except Exception as e:
        print(f"Error: {e}")
        return None

def get_time():
        current_time = time.time()
        formatted_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(current_time))
        return formatted_time


def publishData(txt):
    print(txt)
    while (True):
        temperature = read_temperature()
        current_time = get_time()
        if temperature is not None:
            Temp = int(float(temperature))
        else:
            Temp = ("Failed to read temperature data")
        DeviceName = "LivingRoom"
        print(Temp)
        print(DeviceName)
        print(current_time)
        client.publish("raspi/tempsense", payload=json.dumps({"DeviceName": DeviceName, "Temp": Temp, "Time": current_time }), qos=0, retain=False)


        time.sleep(5)
_thread.start_new_thread(publishData,("Spin-up new Thread...",))

client.loop_forever()



