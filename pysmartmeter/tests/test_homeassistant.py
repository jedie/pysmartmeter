import re

from bx_py_utils.test_utils.snapshot import assert_snapshot

from pysmartmeter.data_classes import HomeassistantValue, ObisValue
from pysmartmeter.homeassistant import (
    data2config,
    data2state,
    get_value_by_key,
    ha_convert_obis_values,
)
from pysmartmeter.tests import BaseTestCase
from pysmartmeter.tests.data import get_obis_values
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
                obis_value=ObisValue(
                    key='1-0:1.8.0*255',
                    key_slug='1_0_1_8_0_255',
                    name='Zählerstand (Tariflos)',
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
        config = data2config(ha_values=ha_values)

        unique_ids = []
        for data in config:
            topic = data['topic']
            self.assertRegex(topic, TOPIC_MATCHER)

            # Check object_id uniqueness:
            unique_id = data['data']['unique_id']
            self.assertNotIn(unique_id, unique_ids)
            unique_ids.append(unique_id)

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
        assert_snapshot(got=config)

    def test_data2state(self):
        ha_values = ha_convert_obis_values(obis_values=get_obis_values())
        result = data2state(ha_values=ha_values)
        self.assert_verbose(
            got=result,
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
