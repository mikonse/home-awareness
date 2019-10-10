import asyncio
import re
import subprocess
from threading import Thread

from time import sleep, time
from modular_conf.fields import TupleListField

from common import User
from config import config
from bus import e_bus
from bus.events import Event, InfoEvent
from common.events import TrackingEvent
from log import LOG

MODULE_NAME = 'wifi'
CONFIG_FIELDS = [
    TupleListField(
        name='to_track',
        n_elems=2,
        element_names=('name', 'mac'),
        default=[]
    )
]


class Watcher:
    def __init__(self, terminate: asyncio.Event, exit_threshold=600, sleep_amount=30):
        self.tracked = {}
        self.terminate = terminate
        self.exit_threshold = exit_threshold
        self.sleep_amount = sleep_amount

    async def run(self) -> None:
        e_bus.emit('tracker.wifi.initialized', InfoEvent('tracker.wifi.initialized'))

        line_re = re.compile(
            r'^\s*(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>[a-z0-9]+:[a-z0-9]+:[a-z0-9]+:[a-z0-9]+:[a-z0-9]+:[a-z0-9]+).*$')
        while not self.terminate.is_set():
            # look for currently connected devices
            try:
                devices = subprocess.check_output("arp-scan -l", shell=True).decode('ascii')
                # devices = """Interface: enp6s0, datalink type: EN10MB (Ethernet)
                #     Starting arp-scan 1.9.5 with 256 hosts (https://github.com/royhills/arp-scan)
                #     192.168.141.1   cc:ce:1e:6c:d0:0a       (Unknown)
                #     192.168.141.34  e8:df:70:02:4c:e9       (Unknown)
                #     192.168.141.37  ee:df:70:01:9a:42       (Unknown)
                #     192.168.141.43  b8:27:eb:d8:94:5f       Raspberry Pi Foundation
                #     192.168.141.41  08:d8:33:a6:af:e8       Shenzhen RF Technology Co., Ltd
                #     192.168.141.28  08:78:08:5d:18:32       (Unknown)
                #     192.168.141.48  b8:27:eb:1c:0a:af       Raspberry Pi Foundation
                #     192.168.141.48  b8:27:eb:1c:0a:af       Raspberry Pi Foundation (DUP: 2)
                #
                #     8 packets received by filter, 0 packets dropped by kernel
                #     Ending arp-scan 1.9.5: 256 hosts scanned in 2.455 seconds (104.28 hosts/sec). 8 responded"""
            except subprocess.CalledProcessError:
                await asyncio.sleep(30)
                continue

            lines = devices.split('\n')[2:-4]
            macs = []

            # parse all macs out of arp-scan output
            for line in lines:
                match = line_re.match(line)
                if match:
                    macs.append(match.group('mac'))
                else:
                    LOG.error('Failed to parse arp-scan output')
                    continue

            # update tracked macs
            curr_time = time()

            enter = set(macs).difference(self.tracked.keys())

            for mac in macs:
                self.tracked[mac] = curr_time

            leave = [x for x in self.tracked.keys() if
                     curr_time - self.tracked.get(x) >= self.exit_threshold and x not in enter]

            # delete all timed out macs
            for mac in list(self.tracked.keys()):
                if curr_time - self.tracked.get(mac) >= self.exit_threshold:
                    del self.tracked[mac]

            for mac in enter:
                found = next((x for x in config.get(MODULE_NAME, "to_track") if x[1] == mac), None)
                if found:
                    LOG.info(f'User {found[0]} ({found[1]}) entered')
                    e_bus.emit('tracking.event.user_enter', TrackingEvent(User(found[0], found[1])))

            for mac in leave:
                found = next((x for x in config.get(MODULE_NAME, "to_track") if x[1] == mac), None)
                if found:
                    LOG.info(f'User {found[0]} ({found[1]}) left')
                    e_bus.emit('tracking.event.user_exit', TrackingEvent(User(found[0], found[1])))

            # now wait for next round
            await asyncio.sleep(self.sleep_amount)


async def main(shutdown_signal: asyncio.Event) -> None:
    config.register_module(MODULE_NAME, CONFIG_FIELDS)

    watcher = Watcher(shutdown_signal, exit_threshold=600, sleep_amount=30)

    await watcher.run()
    await shutdown_signal.wait()


if __name__ == '__main__':
    asyncio.run(main())
