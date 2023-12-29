import dataclasses
import re

from bx_py_utils.test_utils.snapshot import assert_snapshot

from pysmartmeter.data_classes import HomeassistantValue, MqttPayload, ObisValue
from pysmartmeter.homeassistant import data2config, data2state, get_value_by_key, ha_convert_obis_values
from pysmartmeter.parser import ObisParser
from pysmartmeter.publish_loop import HomeAssistantMqtt, obis_values2mqtt_config, obis_values2mqtt_state
from pysmartmeter.tests.base import BaseTestCase
from pysmartmeter.tests.data import TEST_DATA_BIG, get_obis_values
from pysmartmeter.tests.mocks import MqttPublisherMock
from pysmartmeter.utilities.serializer import serialize_values


# origin from:
# https://github.com/home-assistant/core/blob/dev/homeassistant/components/mqtt/discovery.py
# prefixed with "homeassistant" here:
TOPIC_MATCHER = re.compile(
    r'homeassistant/(?P<component>\w+)/(?:(?P<node_id>[a-zA-Z0-9_-]+)/)'
    r'?(?P<object_id>[a-zA-Z0-9_-]+)/config'
)


class HomeassistantTestCase(BaseTestCase):
    def test_ha_convert_obis_values(self):
        ha_values = ha_convert_obis_values(obis_values=get_obis_values())

        # Test examples:
        value_10180255 = get_value_by_key(values=ha_values, key='1-0:1.8.0*255')
        self.assert_verbose(
            got=value_10180255,
            excepted=HomeassistantValue(
                unique_id='ebz5dd3bz06eta107_1_0_1_8_0_255',
                value_key='value_1_0_1_8_0_255',
                state_class='total',
                device_class='energy',
                obis_value=ObisValue(
                    key='1-0:1.8.0*255',
                    key_slug='1_0_1_8_0_255',
                    name='Zählerstand Bezug (Tariflos)',
                    raw_value='0010002*kWh',
                    value=10002.0,
                    raw_unit='kWh',
                    unit='kWh',
                ),
            ),
        )
        value_009680255 = get_value_by_key(values=ha_values, key='0-0:96.8.0*255')
        self.assert_verbose(
            got=value_009680255,
            excepted=HomeassistantValue(
                unique_id='ebz5dd3bz06eta107_0_0_96_8_0_255',
                value_key='value_0_0_96_8_0_255',
                state_class='measurement',
                device_class='energy',
                obis_value=ObisValue(
                    key='0-0:96.8.0*255',
                    key_slug='0_0_96_8_0_255',
                    name='Betriebsdauer',
                    raw_value='000BEEF02',
                    value=12513026,
                    raw_unit=None,
                    unit='sec.',
                ),
            ),
        )

        assert_snapshot(got=serialize_values(ha_values))

    def test_data2config(self):
        ha_values = ha_convert_obis_values(obis_values=get_obis_values())
        mqtt_payloads = data2config(ha_values=ha_values)
        self.assertIsInstance(mqtt_payloads, list)

        payloads = []
        unique_ids = []
        for mqtt_payload in mqtt_payloads:
            self.assertIsInstance(mqtt_payload, MqttPayload)
            self.assertRegex(mqtt_payload.topic, TOPIC_MATCHER)

            # Check object_id uniqueness:
            unique_id = mqtt_payload.data['unique_id']
            self.assertNotIn(unique_id, unique_ids)
            unique_ids.append(unique_id)

            payloads.append(dataclasses.asdict(mqtt_payload))

        self.assertEqual(
            unique_ids,
            [
                'ebz5dd3bz06eta107_identifier',
                'ebz5dd3bz06eta107_1_0_0_0_0_255',
                'ebz5dd3bz06eta107_1_0_96_1_0_255',
                'ebz5dd3bz06eta107_1_0_1_8_0_255',
                'ebz5dd3bz06eta107_1_0_96_5_0_255',
                'ebz5dd3bz06eta107_0_0_96_8_0_255',
                'ebz5dd3bz06eta107_human_op_time',
            ],
        )
        assert_snapshot(got=payloads)

    def test_data2state(self):
        ha_values = ha_convert_obis_values(obis_values=get_obis_values())
        mqtt_payload = data2state(ha_values=ha_values)
        self.assertIsInstance(mqtt_payload, MqttPayload)
        self.assert_verbose(
            got=dataclasses.asdict(mqtt_payload),
            excepted={
                'topic': 'homeassistant/sensor/EBZ5DD3BZ06ETA107/state',
                'data': {
                    'value_identifier': 'EBZ5DD3BZ06ETA_107',
                    'value_1_0_0_0_0_255': '1EBZ0100000123',
                    'value_1_0_96_1_0_255': '1EBZ0100000123',
                    'value_1_0_1_8_0_255': 10002.0,
                    'value_1_0_96_5_0_255': '001C0104',
                    'value_0_0_96_8_0_255': 12513026,
                    'value_human_op_time': 4.8,
                },
            },
        )

    def test_homeassistant_mqtt_payloads(self):
        """
        Snapshot a complete configs/data MQTT payload for Home Assistant
        """

        def obis2mqtt(obis_values):
            payloads = obis_values2mqtt_config(obis_values=obis_values)
            payloads.append(obis_values2mqtt_state(obis_values=obis_values))
            results = []
            for mqtt_payload in payloads:
                self.assertIsInstance(mqtt_payload, MqttPayload)
                results.append(dataclasses.asdict(mqtt_payload))
            return results

        # Snapshot RAW_TEST_DATA_SMALL:
        results = obis2mqtt(obis_values=get_obis_values())
        self.assertEqual(len(results), 8)
        assert_snapshot(got=results)

    def test_ha_publisher(self):
        mqtt_publisher = MqttPublisherMock()

        publisher = HomeAssistantMqtt(mqtt_publisher=mqtt_publisher, verbose=False)
        parser = ObisParser(publish_callback=publisher, verbose=False)
        for line in TEST_DATA_BIG:
            parser.feed_line(line)

        self.assertEqual(len(mqtt_publisher.mqtt_payloads), 15)
        result = []
        for payload in mqtt_publisher.mqtt_payloads:
            self.assertIsInstance(payload, MqttPayload)
            result.append(dataclasses.asdict(payload))

        assert_snapshot(got=result)
