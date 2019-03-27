import platform
import subprocess
import os
import time
import lirc
import denonavr

IP_AUDIO = "192.168.178.35"
IP_SAT = "192.168.178.41"
denon = denonavr.DenonAVR( IP_AUDIO )

def ping(host):
    """
    Returns True if host responds to a ping request
    """
    
    # Ping parameters as function of OS
    args = "ping -c 1 -W 1 " + host
    return subprocess.call(args, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

 
sockid=lirc.init("mediacenter", blocking = True)
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
                    os.system("irsend SEND_ONCE EPSON-TW6000 KEY_POWERUP")
                    time.sleep(0.05)
                # und Denon an, wenn nicht schon an
                denon.update()
                denon.power_on()
                #os.system("irsend SEND_ONCE Denon_RC-1163 KEY_POWERCHANGE")
                time.sleep(4)
                denon.set_volume(-40)
                time.sleep(4)
                denon.set_volume(-40)
            else:
                denon.set_volume(-60)
                # war an, alles ausschalten
                for l in range(1,5):
                    os.system("irsend SEND_ONCE EPSON-TW6000 KEY_SUSPEND")
                    time.sleep(0.05)
                denon.update()
                denon.power_off()
        time.sleep(0.05)
