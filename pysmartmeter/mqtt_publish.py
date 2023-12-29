import logging
import os
import resource
import socket

from rich import print

import pysmartmeter
from pysmartmeter.config import Config
from pysmartmeter.detect_serial import get_serial
from pysmartmeter.parser import ObisParser
from pysmartmeter.user_settings import MqttSettings, UserSettings


logger = logging.getLogger(__name__)


def get_client_id():
    hostname = socket.gethostname()
    client_id = f'PySmartMeter v{pysmartmeter.__version__} on {hostname}'
    return client_id


def publish_forever(*, config: Config):
    serial = get_serial(config=config)

    user_settings: UserSettings = config.settings
    mqtt_settings: MqttSettings = user_settings.mqtt

    mqtt_publisher = HaMqttPublisher(
        settings=mqtt_settings,
        verbosity=config.verbosity,
        config_count=12,  # Send every time the config
    )

    publisher = HomeAssistantMqtt(mqtt_publisher=mqtt_publisher, verbosity=config.verbosity)
    parser = ObisParser(publish_callback=publisher, verbosity=config.verbosity)

    while True:
        data = serial.readline()
        parser.feed_line(data)

    while True:
        # Just collect something that we can send:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        values = [
            HaValue(
                name='System load 1min.',
                value=os.getloadavg()[0],
                device_class='',
                state_class='measurement',
                unit='',
            ),
            HaValue(
                name='Time in user mode (float seconds)',
                value=usage.ru_utime,
                device_class='',
                state_class='measurement',
                unit='sec',
            ),
            HaValue(
                name='Time in system mode (float seconds)',
                value=usage.ru_stime,
                device_class='',
                state_class='measurement',
                unit='sec',
            ),
        ]

        # Collect information:
        ha_values = HaValues(
            device_name=user_settings.app.device_name,
            values=values,
        )

        # Create Payload:
        ha_mqtt_payload = values2mqtt_payload(values=ha_values, name_prefix=user_settings.app.mqtt_payload_prefix)

        # Send vial MQTT to HomeAssistant:
        publisher.publish2homeassistant(ha_mqtt_payload=ha_mqtt_payload)

        print('Wait', end='...')
        for i in range(10, 1, -1):
            time.sleep(1)
            print(i, end='...')
