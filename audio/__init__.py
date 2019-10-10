import asyncio

from audio.volumio import VolumioControl
from config import config
from modular_conf.fields import StringField, IntField

MODULE_NAME = 'audio'
CONFIG_FIELDS = [
    StringField('volumio_host', default='volumio.local'),
    IntField('volumio_port', default=3000)
]

control = None


async def main(shutdown_signal: asyncio.Event):
    config.register_module(MODULE_NAME, CONFIG_FIELDS)

    global control
    control = VolumioControl(config.get(MODULE_NAME, 'volumio_host'), config.get(MODULE_NAME, 'volumio_port'))

    await shutdown_signal.wait()


if __name__ == '__main__':
    asyncio.run(main())
