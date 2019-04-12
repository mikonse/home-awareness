from threading import Thread
from time import time, sleep

import bus
from bus.message import Message


class Alarm:
    def __init__(self, time, days, once=False):
        self.time = time
        self.days = days
        self.once = once

    def next(self):
        pass

    def serialize(self):
        return {
            'time': self.time,
            'days': self.days,
            'once': self.once
        }

    def __call__(self, *args, **kwargs):
        bus.emit(Message('alarm.do_stuff', data=self.serialize()))


class Watcher(Thread):
    def __init__(self):
        super(Watcher, self).__init__()
        self.running = True
        self.repeating = dict()  # time: callable
        self.one_time = dict()

    def run(self):
        while self.running:
            curr_time = time()
            for t, alarm in list(self.repeating.items()):
                if curr_time <= t:
                    alarm()
                    del self.repeating[t]
                    self.repeating[alarm.next()] = alarm

            for t, alarm in list(self.one_time.items()):
                if curr_time <= t:
                    alarm()
                    del self.one_time[t]
            sleep(1)

    def terminate(self):
        self.running = False

    def set(self, alarm, next=None, once=False):
        if once:
            self.one_time[next or alarm.next()] = alarm
        else:
            self.one_time[next or alarm.next()] = alarm


watcher = Watcher()


def set_alarm(time, days, once=False):
    alarm = Alarm(time, days, once)
    watcher.set(alarm, alarm.next(), alarm.once)


def main():
    watcher.start()


if __name__ == '__main__':
    main()
