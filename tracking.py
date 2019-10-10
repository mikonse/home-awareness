import asyncio
from time import time
from typing import List

from modular_conf.fields import ChoiceField

from bus import e_bus
from bus.events import Event
from common.events import TrackingEvent
from config import config

from log import LOG


MODULE_NAME = 'tracking'
CONFIG_FIELDS = [
    ChoiceField('test_choice', default='one', choices=('one', 'two', 'three', 'four'), type=str)
]


class UserTracker:
    def __init__(self):
        self.users = {}

        e_bus.on('tracking.event.user_enter', self.on_user_enter)
        e_bus.on('tracking.event.user_exit', self.on_user_exit)

    async def on_user_enter(self, event: TrackingEvent) -> None:
        if len(self.users) == 0:
            LOG.info('First user entered, initializing system')
            e_bus.emit('tracking.action.initialize', Event())

        self.users[event.user.name] = time()

    async def on_user_exit(self, event: TrackingEvent) -> None:
        if event.user.name in self.users:
            del self.users[event.user.name]

        if len(self.users) == 0:
            LOG.info('Last user let, shutting down system')
            e_bus.emit('tracking.action.shutdown', Event())

    def get_current_users(self) -> List:
        return [{'name': user, 'time': since} for user, since in self.users.items()]


async def main(shutdown_signal: asyncio.Event):
    config.register_module(MODULE_NAME, CONFIG_FIELDS)
    tracker = UserTracker()

    await shutdown_signal.wait()


if __name__ == '__main__':
    asyncio.run(main())
