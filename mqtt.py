import json

import paho.mqtt.client as mqtt
from modular_conf.fields import StringField, IntField

from bus.message import Message
from config import config
from log import LOG


MODULE_NAME = 'mqtt'


CONFIG_FIELDS = [
    StringField('mqtt_host', default='localhost'),
    IntField('mqtt_port', default=9000)
]


_client = None


def callback_wrapper(topic, f):
    def func(client, userdata, message):
        f(Message(topic, json.loads(message)))

    return func


class Client:
    def __init__(self, host=None, port=None, clientid=None):
        self.host = host or config.get(MODULE_NAME, 'mqtt_host')
        self.port = port or config.get(MODULE_NAME, 'mqtt_port')

        self.client = mqtt.Client(clientid)
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        LOG.info(f'MQTT client ({client}) connected')

    def on_message(self, client, userdata, msg):
        pass

    def on_publish(self, client, userdata, mid):
        pass

    def on_subscribe(self, client, userdata, mid, granted_qos):
        pass

    def on_disconnect(self, client, userdata, rc):
        pass

    def connect(self):
        self.client.connect(self.host, self.port, keepalive=60)

    def publish(self, topic, payload, qos=0, retain=False):
        self.client.publish(topic, payload, qos, retain)

    def subscribe(self, topic, callback, qos=0):
        """
        Subscribe to a certain topic. Callback will be called with messages received in that topic.
        Args:
            topic (str): mqtt topic
            callback (function): callback
            qos (int): quality of service flag for mqtt
        """
        self.client.subscribe(topic, qos)
        self.client.message_callback_add(topic, callback_wrapper(topic, callback))


def main():
    config.register_module(MODULE_NAME, CONFIG_FIELDS)

    global _client
    _client = Client(clientid='home-awareness')
    # _client.connect()
    # _client.publish('test/test', json.dumps({'testdata': 123}))
