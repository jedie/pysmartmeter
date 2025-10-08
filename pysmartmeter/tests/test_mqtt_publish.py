from unittest import TestCase
from unittest.mock import patch

from bx_py_utils.test_utils.snapshot import assert_snapshot
from freezegun import freeze_time
from ha_services.mqtt4homeassistant.data_classes import MqttSettings
from ha_services.mqtt4homeassistant.mocks import HostSystemMock
from ha_services.mqtt4homeassistant.mocks.mqtt_client_mock import MqttClientMock

from pysmartmeter import mqtt_handler, mqtt_publish
from pysmartmeter.mqtt_publish import publish_forever
from pysmartmeter.tests.data import RawObisDataMock
from pysmartmeter.user_settings import UserSettings


class StopTestLoop(StopIteration):
    pass


class GetSerialMock:
    def __init__(self, count: int):
        rdm = RawObisDataMock()
        self.lines = rdm.iter_block(count=count + 1)

    def __call__(self, verbose):
        return self

    def readline(self):
        try:
            return next(self.lines)
        except StopIteration as err:
            raise StopTestLoop from err


class MqttPublishTestCase(TestCase):
    maxDiff = None

    def test_publish_forever(self):
        mqtt_client_mock = MqttClientMock()
        user_settings = UserSettings(
            mqtt=MqttSettings(
                main_uid='the_main_uid',
            )
        )

        with (
            HostSystemMock(),
            freeze_time(
                time_to_freeze='2012-01-14T12:00:00+00:00',
                tick=True,  # Needed to avoid ZeroDivisionError in rate calculation
            ),
            patch.object(mqtt_publish, 'get_user_settings', return_value=user_settings),
            patch.object(mqtt_publish, 'get_serial_port', GetSerialMock(count=1)),
            patch.object(mqtt_handler, 'get_connected_client', return_value=mqtt_client_mock),
            self.assertRaises(StopTestLoop),
            self.assertLogs(logger=None),
        ):
            publish_forever(verbosity=0)

        config_payload = mqtt_client_mock.get_config_payload()
        self.assertEqual(
            config_payload[-1],
            {
                'component': 'sensor',
                'device': {
                    'identifiers': 'the_main_uid-ebz_dd3',
                    'manufacturer': 'eBZ',
                    'name': 'eBZ DD3',
                    'via_device': 'the_main_uid',
                },
                'device_class': None,
                'json_attributes_topic': (
                    'homeassistant/sensor/the_main_uid-ebz_dd3/the_main_uid-ebz_dd3-betriebsdauer/attributes'
                ),
                'name': 'Betriebsdauer',
                'origin': {
                    'name': 'ha-services-tests',
                    'support_url': 'https://pypi.org/project/ha_services/',
                    'sw_version': '1.2.3',
                },
                'state_class': None,
                'state_topic': 'homeassistant/sensor/the_main_uid-ebz_dd3/the_main_uid-ebz_dd3-betriebsdauer/state',
                'unique_id': 'the_main_uid-ebz_dd3-betriebsdauer',
                'unit_of_measurement': 'sec.',
            },
        )
        state_messages = mqtt_client_mock.get_state_messages()
        self.assertEqual(
            state_messages[-1],
            {
                'payload': 12513026,
                'qos': 0,
                'retain': False,
                'topic': 'homeassistant/sensor/the_main_uid-ebz_dd3/the_main_uid-ebz_dd3-betriebsdauer/state',
            },
        )
        assert_snapshot(got=config_payload, name_suffix='config_payload')
        assert_snapshot(got=state_messages, name_suffix='state_messages')
