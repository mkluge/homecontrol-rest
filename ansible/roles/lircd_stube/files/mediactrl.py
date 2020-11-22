import os
import time
import subprocess
import lirc
import json
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
                # d.h. Beamer an
                for l in range(1, 5):
                    os.system(
                        "irsend --device=/var/run/lirc/lircd-tx SEND_ONCE EPSON-TW6000 KEY_POWERUP")
                    time.sleep(0.05)
                # und Denon an, wenn nicht schon an
                denon.update()
                denon.power_on()
                time.sleep(7)
                denon.input_func = "AUXB"
                time.sleep(3)
                denon.set_volume(-40)
                # noch Bescheid geben, dass der Beamer jetzt an ist
                client.publish(config["MQTT_BEAMER_TOPIC"], "on")
            else:
                denon.set_volume(-60)
                # war an, alles ausschalten
                for l in range(1, 5):
                    os.system(
                        "irsend --device=/var/run/lirc/lircd-tx SEND_ONCE EPSON-TW6000 KEY_SUSPEND")
                    time.sleep(0.05)
                denon.update()
                denon.input_func = "Spotify"
                denon.power_off()
                # noch Bescheid geben, dass der Beamer jetzt aus ist
                client.publish(config["MQTT_BEAMER_TOPIC"], "off")
        time.sleep(0.05)
