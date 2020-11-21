import subprocess
import os
import time
import json
import paho.mqtt.client as mqtt

ON = "KEY_POWERUP"
OFF = "KEY_SUSPEND"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def on_message(client, userdata, msg):
    if msg.topic == config["MQTT_BEAMER_TOPIC"]:
        if msg.payload == b"on":
            beamer_power_cmd(ON)
        if msg.payload == b"off":
            beamer_power_cmd(OFF)


def beamer_power_cmd(key):
    for l in range(1, 5):
        os.system(
            "irsend --device=/var/run/lirc/lircd-tx SEND_ONCE EPSON-TW6000 "+key)
        time.sleep(0.05)


with open("apl19config.json") as json_file:
    config = json.load(json_file)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(config["IP_MQTT"], 1883, 60)
client.subscribe(config["MQTT_BEAMER_TOPIC"])

client.loop_forever()
