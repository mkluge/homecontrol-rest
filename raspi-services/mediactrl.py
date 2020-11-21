import os
import time
import subprocess
import lirc
import denonavr
import paho.mqtt.client as mqtt

IP_MQTT = "192.168.178.104"
TOPIC = "beamer/power"
IP_AUDIO = "192.168.178.35"
IP_SAT = "192.168.178.41"
denon = denonavr.DenonAVR( IP_AUDIO )

def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def ping(host):
    """
    Returns True if host responds to a ping request
    """
    
    # Ping parameters as function of OS
    args = "ping -c 1 -W 1 " + host
    return subprocess.call(args, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

client = mqtt.Client()
client.on_connect = on_connect
client.connect( IP_MQTT, 1883, 60)
sockid=lirc.init("mediacenter", blocking = True)
print("running")
while True:
    codeIR = lirc.nextcode()
    if codeIR != []:
        print(codeIR[0])
        if codeIR[0] == "KEY_POWER":
            sat_on = ping(IP_SAT)
            print("SAT: " + str(sat_on))
            # wenn Sat nicht anwar, wurde es gerade angeschaltet
            if not sat_on:
                # d.h. Beamer an
                for l in range(1,5):
                    os.system("irsend --device=/var/run/lirc/lircd-tx SEND_ONCE EPSON-TW6000 KEY_POWERUP")
                    time.sleep(0.05)
                # und Denon an, wenn nicht schon an
                denon.update()
                denon.power_on()
                time.sleep(7)
                denon.input_func="AUXB"
                time.sleep(3)
                denon.set_volume(-40)
                # noch Bescheid geben, dass der Beamer jetzt an ist
                client.publish( TOPIC, "on")
            else:
                denon.set_volume(-60)
                # war an, alles ausschalten
                for l in range(1,5):
                    os.system("irsend --device=/var/run/lirc/lircd-tx SEND_ONCE EPSON-TW6000 KEY_SUSPEND")
                    time.sleep(0.05)
                denon.update()
                denon.input_func="Spotify"
                denon.power_off()
                # noch Bescheid geben, dass der Beamer jetzt aus ist
                client.publish( TOPIC, "off")
        time.sleep(0.05)
