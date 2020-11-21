import subprocess
import os
import time
import paho.mqtt.client as mqtt

IP_MQTT = "192.168.178.104"
ON = "KEY_POWERUP"
OFF = "KEY_SUSPEND"
TOPIC = "beamer/power"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def on_message(client, userdata, msg):
    print(msg.topic)
    if msg.topic == TOPIC:
        if msg.payload == b"on":
            beamer_power_cmd(ON)
        if msg.payload == b"off":
            beamer_power_cmd(OFF)


def beamer_power_cmd(key):
    for l in range(1, 5):
        os.system(
            "irsend --device=/var/run/lirc/lircd-tx SEND_ONCE EPSON-TW6000 "+key)
        time.sleep(0.05)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(IP_MQTT, 1883, 60)
client.subscribe(TOPIC)

client.loop_forever()
