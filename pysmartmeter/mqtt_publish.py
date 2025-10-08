import logging

from pysmartmeter.detect_serial import get_serial_port
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

    port = user_settings.hichi.port

    ser = get_serial_port(port)

    parser = ObisParser(publish_callback=hichi_mqtt_handler)

    while True:
        data = ser.readline()
        logger.debug('Raw serial data: %r', data)
        parser.feed_line(data)
