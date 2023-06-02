import logging
import socket

from ha_services.mqtt4homeassistant.mqtt import HaMqttPublisher
from rich import print
from rich.pretty import pprint

import pysmartmeter
from pysmartmeter.config import Config
from pysmartmeter.data_classes import MqttPayload, ObisValue
from pysmartmeter.detect_serial import get_serial
from pysmartmeter.homeassistant import data2config, data2state, ha_convert_obis_values
from pysmartmeter.parser import ObisParser
from pysmartmeter.user_settings import MqttSettings, UserSettings


logger = logging.getLogger(__name__)


def get_client_id():
    hostname = socket.gethostname()
    client_id = f'PySmartMeter v{pysmartmeter.__version__} on {hostname}'
    return client_id


class OnConnectCallback:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def __call__(self, client, userdata, flags, rc):
        if self.verbosity:
            print(f'MQTT broker connect result code: {rc}', end=' ')

        if rc == 0:
            if self.verbosity:
                print('[green]OK')
        else:
            print('\n[red]MQTT Connection not successful!')
            print('[yellow]Please check your credentials\n')
            raise RuntimeError(f'MQTT connection result code {rc} is not 0')

        if self.verbosity:
            print(f'\t{userdata=}')
            print(f'\t{flags=}')


def obis_values2mqtt_state(obis_values: list[ObisValue], verbose: bool = False) -> MqttPayload:
    ha_values = ha_convert_obis_values(obis_values=obis_values)
    if verbose:
        pprint(ha_values)
    return data2state(ha_values=ha_values)


def obis_values2mqtt_config(obis_values: list[ObisValue]) -> list[MqttPayload]:
    ha_values = ha_convert_obis_values(obis_values=obis_values)
    return data2config(ha_values=ha_values)


class HomeAssistantMqtt:
    def __init__(self, mqtt_publisher: HaMqttPublisher, verbosity: int = 1):
        self.mqtt_publisher = mqtt_publisher
        self.verbosity = verbosity

        self.send_count = 0

    def __call__(self, *, obis_values: list[ObisValue]):
        pprint(obis_values)

        if self.send_count % 12 == 0:
            for payload in obis_values2mqtt_config(obis_values=obis_values):
                self.mqtt_publisher.publish(mqtt_payload=payload)

        if self.verbosity:
            print(f'publish values (send count: {self.send_count}):')
        self.mqtt_publisher.publish(mqtt_payload=obis_values2mqtt_state(obis_values=obis_values, verbose=self.verbose))
        self.send_count += 1


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
