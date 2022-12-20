import json
import logging
import socket
import sys

import paho.mqtt.client as mqtt
from bx_py_utils.anonymize import anonymize
from rich.pretty import pprint

import pysmartmeter
from pysmartmeter.data_classes import MqttPayload, MqttSettings, ObisValue
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

    def publish(self, *, mqtt_payload: MqttPayload) -> None:
        if self.verbose:
            print('_' * 100)
            print(f'Publish MQTT topic: {mqtt_payload.topic}')
            pprint(mqtt_payload.data)

        assert self.mqttc.is_connected()
        info = self.mqttc.publish(topic=mqtt_payload.topic, payload=json.dumps(mqtt_payload.data))

        if self.verbose:
            print('publish result:', info)


def obis_values2mqtt_state(obis_values: list[ObisValue], verbose: bool = False) -> MqttPayload:
    ha_values = ha_convert_obis_values(obis_values=obis_values)
    if verbose:
        pprint(ha_values)
    return data2state(ha_values=ha_values)


def obis_values2mqtt_config(obis_values: list[ObisValue]) -> list[MqttPayload]:
    ha_values = ha_convert_obis_values(obis_values=obis_values)
    return data2config(ha_values=ha_values)


class HomeAssistantMqtt:
    def __init__(self, mqtt_publisher: MqttPublisher, verbose: bool = True):
        self.mqtt_publisher = mqtt_publisher
        self.verbose = verbose

        self.send_count = 0

    def __call__(self, *, obis_values: list[ObisValue]):
        if self.send_count % 12 == 0:
            for payload in obis_values2mqtt_config(obis_values=obis_values):
                self.mqtt_publisher.publish(mqtt_payload=payload)

        if self.verbose:
            print(f'publish values (send count: {self.send_count}):')
        self.mqtt_publisher.publish(
            mqtt_payload=obis_values2mqtt_state(obis_values=obis_values, verbose=self.verbose)
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
