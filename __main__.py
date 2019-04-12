import audio
import bus
import mqtt
import tracking
import web
import wifi
from log import LOG


def main():
    # start main bus
    LOG.info('Starting message bus')
    bus.main()

    # start user tracking
    LOG.info('Starting user tracking')
    tracking.main()

    # start wifi tracker
    LOG.info('Starting Wifi tracking')
    wifi.main()

    # start volumio control
    LOG.info('Starting volumio control')
    audio.main()

    # start web interface
    LOG.info('Starting web interface')
    web.main()

    # start mqtt
    LOG.info('Starting MQTT')
    mqtt.main()

    LOG.info('Done starting up')


if __name__ == '__main__':
    main()
