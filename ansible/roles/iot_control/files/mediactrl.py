import os
import time
import subprocess
import json
import lirc
import denonavr
from mqttw import MqttWrapper


def ping(host):
    """
    Returns True if host responds to a ping request
    """

    # Ping parameters as function of OS
    args = "ping -c 1 -W 1 " + host
    return subprocess.call(args, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


with open("apl19config.json") as json_file:
    config = json.load(json_file)

denon = denonavr.DenonAVR(config["IP_AUDIO"])

client = MqttWrapper("mediacenter", config["IP_MQTT"], 1883, 60)
sockid = lirc.init("mediacenter", blocking=True)
print("running")
while True:
    codeIR = lirc.nextcode()
    if codeIR != []:
        print(codeIR[0])
        if codeIR[0] == "KEY_POWER":
            sat_on = ping(config["IP_SAT"])
            print("SAT: " + str(sat_on))
            # wenn Sat nicht anwar, wurde es gerade angeschaltet
            if not sat_on:
                # Beamer an
                client.publish(config["MQTT_BEAMER_TOPIC"], "on")
                # und Denon an, wenn nicht schon an
                denon.update()
                denon.power_on()
                time.sleep(7)
                denon.input_func = "AUXB"
                time.sleep(3)
                denon.set_volume(-40)
            else:
                # Denon Lautstärke runter und aus
                denon.set_volume(-60)
                denon.update()
                denon.input_func = "Spotify"
                denon.power_off()
                # Beamer aus
                client.publish(config["MQTT_BEAMER_TOPIC"], "off")
        time.sleep(0.05)
