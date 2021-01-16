import paho.mqtt.client as mqtt


class MqttWrapper:
    """ wraps the paho mqtt client so that messages are only
        sent if we are connected
    """

    def __init__(self, name, host, port, keepalive):
        self.client = mqtt.Client(name)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connect(host, port, keepalive)
        self.connected_flag = False
        self.client.loop_start()

    def on_connect(self, mqtt_client, userdata, flags, rc):
        if rc == 0:
            self.connected_flag = True
        else:
            self.connected_flag = False
        print("Connected with result code " + str(rc))

    def on_disconnect(self, mqtt_client, userdata, rc):
        print("disconnecting reason  " + str(rc))
        self.connected_flag = False

    def publish(self, topic, value):
        if self.connected_flag:
            self.client.publish(topic, value)
