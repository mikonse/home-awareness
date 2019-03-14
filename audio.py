import socketio

from bus import EventBus
from config import config
from config.fields import StringField, IntField

MODULE_NAME = 'audio'
CONFIG_FIELDS = [
    StringField('volumio_host', default='volumio.local'),
    IntField('volumio_port', default=3000)
]


control = None


class PlaybackControl(object):
    def __init__(self):
        self._state = dict()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def pause(self, *args):
        raise Exception('Not implemented')

    def resume(self, *args):
        raise Exception('Not implemented')

    def restart(self):
        raise Exception('Not implemented')


class VolumioControl(PlaybackControl):
    def __init__(self, host, port):
        super().__init__()
        self.sio = socketio.Client()
        self.url = f'http://{host}:{port}'
        self.sio.connect(self.url)

        self.sio.on('pushState', self.push_state)
        self.sio.emit('getState')

        self.state = dict()

        EventBus.on('tracking.action.shutdown', self.pause)
        # EventBus.on('tracking.action.initialize', self.resume)

    def pause(self, *args):
        self.sio.emit('pause')

    def resume(self, *args):
        self.sio.emit('play')

    def get_status(self):
        return self.state.get('status')

    def get_playing(self):
        return f'{self.state.get("title")} by {self.state.get("artist")} - {self.state.get("album")}'

    def push_state(self, *args):
        self.state = args[0]

    def teardown(self):
        self.sio.disconnect()

    def __del__(self):
        self.sio.disconnect()

    def restart(self):
        self.sio.disconnect()
        self.sio.connect(self.url)


def get_player_state():
    return control.state


def main():
    global control
    control = VolumioControl(config.get(MODULE_NAME, 'volumio_host'), config.get(MODULE_NAME, 'volumio_port'))


if __name__ == '__main__':
    main()
