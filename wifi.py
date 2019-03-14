import asyncio
import re
import subprocess
from threading import Thread

from time import sleep, time

from config import config
from config.fields import TupleListField
from bus import emit, Message
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


_tracked = dict()


def watch(exit_timeout=600, sleep_amount=30):
    asyncio.set_event_loop(asyncio.new_event_loop())
    emit(Message('tracker.wifi.initialized'))

    line_re = re.compile(
        r'^\s*(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>[a-z0-9]+:[a-z0-9]+:[a-z0-9]+:[a-z0-9]+:[a-z0-9]+:[a-z0-9]+).*$')
    while True:
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
            sleep(30)
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

        enter = set(macs).difference(_tracked.keys())

        for mac in macs:
            _tracked[mac] = curr_time

        leave = [x for x in _tracked.keys() if
                 curr_time - _tracked.get(x) >= exit_timeout and x not in enter]

        # delete all timed out macs
        for mac in list(_tracked.keys()):
            if curr_time - _tracked.get(mac) >= exit_timeout:
                del _tracked[mac]

        for mac in enter:
            found = next((x for x in config.get(MODULE_NAME, "to_track") if x[1] == mac), None)
            if found:
                LOG.info(f'User {found[0]} ({found[1]}) entered')
                emit(Message('tracking.event.user_enter', {'user': found[0], 'mac': found[1]}))

        for mac in leave:
            found = next((x for x in config.get(MODULE_NAME, "to_track") if x[1] == mac), None)
            if found:
                LOG.info(f'User {found[0]} ({found[1]}) left')
                emit(Message('tracking.event.user_exit', {'user': found[0], 'mac': found[1]}))

        # now wait for next round
        sleep(sleep_amount)


def main():
    watcher = Thread(target=watch, kwargs={'exit_timeout': 600, 'sleep_amount': 30})
    watcher.start()


if __name__ == '__main__':
    main()
