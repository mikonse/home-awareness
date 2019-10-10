import asyncio
from typing import Dict

import socketio

from bus import e_bus, Event
from utils import make_callback


class VolumioControl:
    def __init__(self, host, port):
        super().__init__()
        self.sio = socketio.AsyncClient()
        self.url = f'http://{host}:{port}'
        self.sio.connect(self.url)

        self.sio.on('pushState', self._push_state)
        self.sio.on('pushQueue', self._push_queue)
        self._update_state()

        self.state = {}

        e_bus.on('tracking.action.shutdown', make_callback(self.pause, self))

    async def pause(self) -> None:
        await self.sio.emit('pause')

    async def resume(self) -> None:
        await self.sio.emit('play')

    async def get_status(self) -> Dict:
        return self.state.get('status')

    async def get_playing(self) -> str:
        return f'{self.state.get("title")} by {self.state.get("artist")} - {self.state.get("album")}'

    async def _push_state(self, *args) -> None:
        self.state = args[0]

    async def _push_queue(self, *args) -> None:
        # TODO: figure out
        self.state['queue'] = args[0]  # ?????

    async def set_volume(self, volume: int) -> None:
        await self.sio.emit('volume', volume)

    async def mute(self) -> None:
        await self.sio.emit('mute')

    async def unmute(self) -> None:
        await self.sio.emit('unmute')

    async def add_to_queue(self, uri: str) -> None:
        await self.sio.emit('addToQueue', data={'uri': uri})

    async def play_playlist(self, playlist: str) -> None:
        await self.sio.emit('playPlaylist', data={'name': playlist})

    async def enqueue_playlist(self, playlist: str) -> None:
        await self.sio.emit('enqueue', data={'name': playlist})

    async def play_song_in_playlist(self, current_song: str, playlist: str):
        # TODO: clear queue
        await self.enqueue_playlist(playlist)
        await self.add_to_queue(current_song)
        await self.move_queue(current_song, 0)

    async def move_queue(self, song_uri: str, pos: int) -> None:
        curr_pos = 1234  # TODO: determine from current queue
        await self.sio.emit('moveQueue', data={'from': curr_pos, 'to': pos})

    async def _update_state(self):
        await self.sio.emit('getState')

    def __del__(self):
        self.sio.disconnect()

    async def restart(self) -> None:
        await self.sio.disconnect()
        await self.sio.connect(self.url)
