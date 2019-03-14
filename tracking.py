from time import time

from bus import EventBus, emit, Message
from config.fields import ChoiceField

from log import LOG


MODULE_NAME = 'tracking'
CONFIG_FIELDS = [
    ChoiceField('test_choice', default='one', choices=('one', 'two', 'three', 'four'), type=str)
]


_tracked_users = dict()


def on_user_enter(message):
    global _tracked_users
    if len(_tracked_users) == 0:
        LOG.info('First user entered, initializing system')
        emit(Message('tracking.action.initialize'))

    _tracked_users[message.data.get('user')] = time()


def on_user_exit(message):
    global _tracked_users
    if message.data.get('user') in _tracked_users:
        del _tracked_users[message.data.get('user')]

    if len(_tracked_users) == 0:
        LOG.info('Last user let, shutting down system')
        emit(Message('tracking.action.shutdown'))


def get_current_users():
    return [{'name': user, 'time': since} for user, since in _tracked_users.items()]


def main():
    EventBus.on('tracking.event.user_enter', on_user_enter)
    EventBus.on('tracking.event.user_exit', on_user_exit)


if __name__ == '__main__':
    main()
