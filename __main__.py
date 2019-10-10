import asyncio
from asyncio import create_task

import audio
import bus
import mqtt
import tracking
import web
import wifi
from log import LOG


async def main():
    shutdown_signal = asyncio.Event()
    modules = []

    # start main bus
    LOG.info('Starting message bus')
    modules.append(create_task(bus.main(shutdown_signal)))

    # start user tracking
    LOG.info('Starting user tracking')
    modules.append(create_task(tracking.main(shutdown_signal)))

    # start wifi tracker
    LOG.info('Starting Wifi tracking')
    modules.append(create_task(wifi.main(shutdown_signal)))

    # start volumio control
    LOG.info('Starting volumio control')
    modules.append(create_task(audio.main(shutdown_signal)))

    # start web interface
    LOG.info('Starting web interface')
    modules.append(create_task(web.main(shutdown_signal)))

    # start mqtt
    LOG.info('Starting MQTT')
    modules.append(create_task(mqtt.main(shutdown_signal)))

    LOG.info('Done starting up')

    try:
        await asyncio.gather(*modules)
    except KeyboardInterrupt:
        shutdown_signal.set()


if __name__ == '__main__':
    asyncio.run(main())
