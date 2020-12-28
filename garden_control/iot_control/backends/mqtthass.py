#!/usr/bin/python3

# install packages:
# sudo apt install python3-influxdb python3-yaml
# pip3 install paho-mqtt

import json
from typing import Dict, List
from iot_control.iotbackendbase import IoTBackendBase
from iot_control.iotdevicebase import IoTDeviceBase
from iot_control.iotfactory import IoTFactory

import paho.mqtt.client as mqtt


@IoTFactory.register_backend("mqtt_hass")
class BackendMqttHass(IoTBackendBase):

    avail_topics = []
    state_topics = {}
    devices = []

    def __init__(self, **kwargs):
        super().__init__()
        config = kwargs.get("config", None)
        self.config = config
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.mqtt_callback_connect
        self.mqtt_client.on_message = self.mqtt_callback_message
        self.mqtt_client.on_disconnect = self.mqtt_callback_disconnect

#        if config['user'] and config['password']:
#            self.mqtt_client.username_pw_set(
#                username=config['user'], password=config['password'])

    def start(self) -> None:
        self.mqtt_client.connect(
            self.config['server'], self.config['port'], 60)
        self.mqtt_client.loop_start()

    def register_device(self, device: IoTDeviceBase) -> None:
        self.devices.append(device)

    def shutdown(self):
        for avail_topic in self.avail_topics:
            self.mqtt_client.publish(avail_topic, self.config.offline_payload)
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()

    def workon(self, thing: IoTDeviceBase, data: Dict):
        for entry in data:
            if entry in self.state_topics:
                val = {entry: data[entry]}
                state_topic = self.state_topics[entry]
                self.mqtt_client.publish(state_topic, json.dumps(val))

    def announce(self):
        for device in self.devices:
            print(device)
            # get list of sensors on device
            sensors = device.list_sensors()
            # create a state topic for everyone
            for sensor in sensors:
                config_topic = "{}/sensor/{}/{}/config".format(
                    self.config.hass_discovery_prefix, sensor.unique_id, sensor)
                state_topic = "{}/sensor/{}/state".format(
                    self.config.hass_discovery_prefix, sensor.unique_id)
                avail_topic = "{}/sensor/{}/avail".format(
                    self.config.hass_discovery_prefix, sensor.unique_id)
                self.avail_topics.append(avail_topic)
                self.state_topics[sensor] = state_topic
                conf_dict = {
                    "device_class": sensor.device_class,
                    "name": sensor.name,
                    "unique_id": sensor.unique_id,
                    "state_topic": state_topic,
                    "availability_topic": avail_topic,
                    "unit_of_measurement": sensor.unit_of_measurement,
                    "value_template": sensor.value_template,
                    "expire_after": sensor.expire_after,
                    "payload_available": self.config.online_payload,
                    "payload_not_available": self.config.offline_payload
                }
                payload = json.dumps(conf_dict)

                print("publishing: {}".format(payload))
                result = self.mqtt_client.publish(config_topic, payload)
                result.wait_for_publish()
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    print("unable to publish")

                self.mqtt_client.publish(
                    avail_topic, self.config.online_payload)

    # The callback for when the client receives a CONNACK response from the server.
    def mqtt_callback_connect(self, client, userdata, flags, rc):

        (result, mid) = self.mqtt_client.subscribe("homeassistant/status")
        print("Got subscription result for " +
              "homeassistant/status"+":"+str(result))
        self.announce()

    # The callback for when a PUBLISH message is received from the server.
    def mqtt_callback_message(self, client, userdata, msg):

        # ignore retained messages
        if 1 == msg.retain:
            return

        if "homeassistant/status" == msg.topic:
            print("home assistant status message:", msg.topic)
            # report ourselves as available to home assistant

            if b'online' == msg.payload:
                # re-report ourselves available to home assistant and report current state
                self.announce()

    def mqtt_callback_disconnect(self, client, userdata, rc):

        if rc != 0:
            print("Unexpected disconnection.")
