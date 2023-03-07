import json
import logging
import socket
import sys

import paho.mqtt.client as mqtt
from bx_py_utils.anonymize import anonymize
from rich import print
from rich.pretty import pprint

import pysmartmeter
from pysmartmeter.data_classes import MqttPayload, MqttSettings, ObisValue
from pysmartmeter.detect_serial import get_serial
from pysmartmeter.homeassistant import data2config, data2state, ha_convert_obis_values
from pysmartmeter.parser import ObisParser


logger = logging.getLogger(__name__)


def get_client_id():
    hostname = socket.gethostname()
    client_id = f'PySmartMeter v{pysmartmeter.__version__} on {hostname}'
    return client_id


class OnConnectCallback:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def __call__(self, client, userdata, flags, rc):
        if self.verbose:
            print(f'MQTT broker connect result code: {rc}', end=' ')

        if rc == 0:
            if self.verbose:
                print('[green]OK')
        else:
            print('\n[red]MQTT Connection not successful!')
            print('[yellow]Please check your credentials\n')
            raise RuntimeError(f'MQTT connection result code {rc} is not 0')

        if self.verbose:
            print(f'\t{userdata=}')
            print(f'\t{flags=}')


def get_connected_client(settings: MqttSettings, verbose: bool = True, timeout=10):
    client_id = get_client_id()

    if verbose:
        print(
            f'\nConnect [cyan]{settings.host}:{settings.port}[/cyan] as "[magenta]{client_id}[/magenta]"...', end=' '
        )

    socket.setdefaulttimeout(timeout)  # Sadly: Timeout will not used in getaddrinfo()!
    info = socket.getaddrinfo(settings.host, settings.port)
    if not info:
        print('[red]Resolve error: No info!')
    elif verbose:
        print('Host/port test [green]OK')

    mqttc = mqtt.Client(client_id=client_id)
    mqttc.on_connect = OnConnectCallback(verbose=verbose)
    mqttc.enable_logger(logger=logger)

    if settings.user_name and settings.password:
        if verbose:
            print(
                f'login with user: {anonymize(settings.user_name)} password:{anonymize(settings.password)}...',
                end=' ',
            )
        mqttc.username_pw_set(settings.user_name, settings.password)

    mqttc.connect(settings.host, port=settings.port)

    if verbose:
        print('[green]OK')
    return mqttc


class MqttPublisher:
    def __init__(self, settings: MqttSettings, verbose: bool = True):
        self.verbose = verbose
        self.mqttc = get_connected_client(settings=settings, verbose=verbose)
        self.mqttc.loop_start()

    def publish(self, *, mqtt_payload: MqttPayload) -> None:
        if self.verbose:
            print('_' * 100)
            print(f'Publish MQTT topic: {mqtt_payload.topic}')
            pprint(mqtt_payload.data)

        assert self.mqttc.is_connected(), 'Not connected to MQTT broker!'
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
