import json
import logging
import socket
import sys

import paho.mqtt.client as mqtt
from bx_py_utils.anonymize import anonymize
from rich.pretty import pprint

import pysmartmeter
from pysmartmeter.data_classes import MqttSettings, ObisValue
from pysmartmeter.detect_serial import get_serial
from pysmartmeter.homeassistant import data2config, data2state, ha_convert_obis_values
from pysmartmeter.parser import ObisParser


logger = logging.getLogger(__name__)


class MqttPublisher:
    def __init__(self, settings: MqttSettings, verbose: bool = True):
        self.verbose = verbose

        client_id = self.get_client_id()

        print(f'Connect {settings.host}:{settings.port} as {client_id!r}...', end=' ')
        self.mqttc = mqtt.Client(client_id=client_id)
        self.mqttc.enable_logger(logger=logger)

        if settings.user_name and settings.password:
            print(
                f'login with user: {anonymize(settings.user_name)}'
                f' password:{anonymize(settings.password)}...',
                end=' ',
            )
            self.mqttc.username_pw_set(settings.user_name, settings.password)
        self.mqttc.connect(settings.host, port=settings.port)
        print('OK')

        self.mqttc.loop_start()

    def get_client_id(self):
        hostname = socket.gethostname()
        client_id = f'PySmartMeter v{pysmartmeter.__version__} on {hostname}'
        return client_id

    def publish(self, *, topic: str, data: dict):
        if self.verbose:
            print('_' * 100)
            print(f'Publish MQTT topic: {topic}')
            pprint(data)

        assert self.mqttc.is_connected()
        info = self.mqttc.publish(topic=topic, payload=json.dumps(data))

        if self.verbose:
            print('publish result:', info)


class HomeAssistantMqtt:
    def __init__(self, mqtt_publisher: MqttPublisher, verbose: bool = True):
        self.mqtt_publisher = mqtt_publisher
        self.verbose = verbose

        self.send_count = 0

    def __call__(self, *, obis_values: list[ObisValue]):
        ha_values = ha_convert_obis_values(obis_values=obis_values)
        if self.verbose:
            print(f'publish values (send count: {self.send_count}):')
            pprint(ha_values)

        if self.send_count % 12 == 0:
            for config in data2config(ha_values=ha_values):
                self.mqtt_publisher.publish(
                    topic=config['topic'],
                    data=config['data'],
                )

        result = data2state(ha_values=ha_values)
        self.mqtt_publisher.publish(
            topic=result['topic'],
            data=result['data'],
        )
        self.send_count += 1


def publish_forever(*, settings: MqttSettings, verbose):
    serial = get_serial()
    if not serial:
        print('Serial not found')
        sys.exit(1)

    mqtt_publisher = MqttPublisher(settings=settings, verbose=verbose)
    publisher = HomeAssistantMqtt(mqtt_publisher=mqtt_publisher, verbose=verbose)
    parser = ObisParser(publish_callback=publisher, verbose=verbose)

    while True:
        data = serial.readline()
        parser.feed_line(data)
