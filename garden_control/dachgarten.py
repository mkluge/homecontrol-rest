#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Dachgarten

"""

import time
import yaml
import sys
from iot_control.iot_devices import iotbme280
from iot_control.iot_devices import iotads1115
from iot_control.iot_devices import iotbh1750
from iot_control.iot_devices import iotraspigpio
import iot_control.backends.mqtthass
from iot_control.iotfactory import IoTFactory


class Dachgarten:

    backends = []
    devices = []
    update_intervall = 60

    def __init__(self, configfile: str):
        with open(configfile, 'r') as stream:
            try:
                self.conf = yaml.load(stream, Loader=yaml.SafeLoader)
            except yaml.YAMLError as exc:
                print(exc)
                print("Unable to parse configuration file {}".format(configfile))
                sys.exit(1)
        # first: build backends
        for backend in self.conf["backends"]:
            backend_cfg = self.conf["backends"][backend]
            self.backends.append(IoTFactory.create_backend(
                backend, config=backend_cfg))
        sys.stdout.flush()
        # second: register devices with backend
        for device in self.conf["devices"]:
            device_cfg = self.conf["devices"][device]
            print(device_cfg)
            try:
                real_device = IoTFactory.create_device(
                    device, config=device_cfg)
            except:
                e = sys.exc_info()[0]
                print("Error: {}".format(e))
            print(real_device)
            self.devices.append(real_device)
            for backend in self.backends:
                backend.register_device(real_device)
        sys.stdout.flush()
        for backend in self.backends:
            backend.announce()
        sys.stdout.flush()

    def set_intervall(self, new_intervall: int):
        self.update_intervall = new_intervall

    def loop_forever(self):
        while True:
            for device in self.devices:
                data = device.read_data()
                for backend in self.backends:
                    backend.workon(device, data)
            time.sleep(self.update_intervall)


if __name__ == '__main__':

    # Creates a local executor
    runtime = Dachgarten("setup.yaml")
    runtime.set_intervall(60)
    runtime.loop_forever()
