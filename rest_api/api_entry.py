import platform
import subprocess
import os
import time
import lirc
import denonavr
from flask import Flask
from flask_restplus import Resource, Api

def ping(host):
    """
    Returns True if host responds to a ping request
    """

    # Ping parameters as function of OS
    args = "ping -c 1 -W 1 " + host
    return subprocess.call(args, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

IP_AUDIO = "192.168.178.35"
IP_SAT = "192.168.178.41"
denon = denonavr.DenonAVR( IP_AUDIO )

app = Flask(__name__)
api = Api(app)

@api.route('/beamer/<action:string>')
class Beamer(Resource):
    def get(self, action):
        return {'get': action}


@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')


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
    denon.update()
    denon.power_off()
