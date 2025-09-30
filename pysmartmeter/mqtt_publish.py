import logging
import sys

from pysmartmeter.detect_serial import get_serial
from pysmartmeter.mqtt_handler import HichiMqttHandler
from pysmartmeter.parser import ObisParser
from pysmartmeter.user_settings import UserSettings, get_user_settings


logger = logging.getLogger(__name__)


def publish_forever(*, verbosity: int):
    """
    Publish all values via MQTT to Home Assistant in a endless loop.
    """
    user_settings: UserSettings = get_user_settings(verbosity)

    hichi_mqtt_handler = HichiMqttHandler(
        user_settings=user_settings,
        verbosity=verbosity,
    )

    ser = get_serial(verbose=True)
    if ser:
        print('[green]Found serial:')
        print(ser)
    else:
        print('Serial not found')
        sys.exit(1)

    parser = ObisParser(publish_callback=hichi_mqtt_handler)

    while True:
        data = ser.readline()
        logger.debug('Raw serial data: %r', data)
        parser.feed_line(data)
