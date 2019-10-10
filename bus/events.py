import json
from typing import Dict, Optional


class Event:
    def __init__(self, data: Optional[Dict] = None):
        self.data = data

    def serialize(self) -> Dict:
        return json.dumps(self.data)

    @staticmethod
    def deserialize(value: str) -> 'Event':
        obj = json.loads(value)
        return Event(obj)

    def __str__(self) -> str:
        if self.data:
            return json.dumps(self.data)
        else:
            return ''


class InfoEvent(Event):
    def __init__(self, message: str):
        super().__init__()
        self.message = message


class EventError(Event):
    def __init__(self, error: Exception):
        super().__init__()
        self.error = error
