from modular_conf.fields import StringField, IntField

MODULE_NAME = 'light'


CONFIG_FIELDS = [
    StringField('mqtt_host', default='localhost'),
    IntField('mqtt_port', default=9000)
]


class LightControl(object):
    def __init__(self):
        pass

    def off(self):
        pass

    def on(self):
        pass
