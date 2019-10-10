from bus import Event
from common import User


class TrackingEvent(Event):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
