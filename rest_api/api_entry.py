import platform
import subprocess
import os
import time
import lirc
import denonavr
from flask import Flask
from flask_restplus import Resource, Api
import socket
import sys

IP_AUDIO = "192.168.178.35"
IP_SAT = "192.168.178.41"
PORT_SAT = 8090

def send_sat(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ( IP_SAT, PORT_SAT)
    data="failure"
    try:
        sock.sendto( bytes("<authenticationRequest pin=\"0000\" />", "utf-8"), server_address)
        data, server = sock.recvfrom(4096)
        sock.sendto( bytes("<rcuButtonRequest code=\"9\" state=\"pressed\" />", "utf-8"), server_address)
        sock.sendto( bytes("<rcuButtonRequest code=\"9\" state=\"released\" />", "utf-8"), server_address)
        sock.sendto( bytes("<rcuButtonRequest code=\"0\" state=\"pressed\" />", "utf-8"), server_address)
        sock.sendto( bytes("<rcuButtonRequest code=\"0\" state=\"released\" />", "utf-8"), server_address)
        sock.sendto( bytes("<rcuButtonRequest code=\"36\" state=\"pressed\" />", "utf-8"), server_address)
        sock.sendto( bytes("<rcuButtonRequest code=\"36\" state=\"released\" />", "utf-8"), server_address)
    finally:
        sock.close()
    return str(data)

def ping(host):
    """
    Returns True if host responds to a ping request
    """

    # Ping parameters as function of OS
    args = "ping -c 1 -W 1 " + host
    return subprocess.call(args, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

denon = denonavr.DenonAVR( IP_AUDIO )
app = Flask(__name__)
api = Api(app)

@api.route('/beamer/<string:action>')
class Beamer(Resource):
    def put(self, action):
        if action=="on":
            for l in range(1,5):
                os.system("irsend SEND_ONCE EPSON-TW6000 KEY_POWERUP")
                time.sleep(0.05)
            return {'result': "OK"}
        elif action=="off":
            for l in range(1,5):
                os.system("irsend SEND_ONCE EPSON-TW6000 KEY_SUSPEND")
                time.sleep(0.05)
            return {'result': "OK"}
        else:
            return {}, 404

@api.route('/sat/<string:action>/', defaults={'value': None})
@api.route('/sat/<string:action>/<int:value>')
class Sat(Resource):
    def put(self, action, value):
        if action=="on":
            return {'result': "OK"}
        elif action=="off":
            return {'result': "OK"}
        elif action=="channel":
            return {'result': send_sat("<authenticationRequest pin=\"0000\" />")}
        else:
            return {}, 404
    def get(self, action, value):
        if action=="power":
            sat_on = ping(IP_SAT)
            return {'result': sat_on}
        else:
            return {}, 404

@api.route('/audio/<string:action>/', defaults={'value': None})
@api.route('/audio/<string:action>/<string:value>')
class Audio(Resource):
    def put(self, action, value):
        if action=="input":
            denon.input_func = value
            return {'result': "OK"}
        elif action=="on":
            denon.power_on()
            return {'result': "OK"}
        elif action=="off":
            denon.power_off()
            return {'result': "OK"}
        elif action=="volume":
            denon.set_volume(int(value))
            return {'result': denon.volume}
        elif action=="volume_down":
            denon.volume_down()
            return {'result': denon.volume}
        elif action=="volume_up":
            denon.volume_up()
            return {'result': denon.volume}
        else:
            return {}, 404

    def get(self, action, value):
        if action=="power":
            return {'result': True if (denon.power=='ON') else False}
        elif action=="inputs":
            return {'result': denon.input_func_list}
        else:
            return {}, 404

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
