import asyncio
import json

import aiomqtt
from modular_conf.fields import StringField, IntField

from bus.events import Event
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
        f(Event(json.loads(message)))

    return func


class Client:
    def __init__(self, host=None, port=None, clientid=None):
        self.host = host or config.get(MODULE_NAME, 'mqtt_host')
        self.port = port or config.get(MODULE_NAME, 'mqtt_port')

        self.client = aiomqtt.Client(clientid)
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

    async def connect(self):
        await self.client.connect(self.host, self.port, keepalive=60)

    async def publish(self, topic, payload, qos=0, retain=False):
        message_info = self.client.publish(topic, payload, qos, retain)
        await message_info.wait_for_publish()

    async def subscribe(self, topic, callback, qos=0):
        """
        Subscribe to a certain topic. Callback will be called with messages received in that topic.
        Args:
            topic (str): mqtt topic
            callback (function): callback
            qos (int): quality of service flag for mqtt
        """
        await self.client.subscribe(topic, qos)
        await self.client.message_callback_add(topic, callback_wrapper(topic, callback))


async def main(shutdown_signal: asyncio.Event):
    config.register_module(MODULE_NAME, CONFIG_FIELDS)

    global _client
    _client = Client(clientid='home-awareness')

    await shutdown_signal.wait()
    # _client.connect()
    # _client.publish('test/test', json.dumps({'testdata': 123}))
