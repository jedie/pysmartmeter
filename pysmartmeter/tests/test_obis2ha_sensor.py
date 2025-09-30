from unittest import TestCase

from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.device import MqttDevice

from pysmartmeter.obis2ha_sensors import Obis2HaSensors, UniqueIds
from pysmartmeter.user_settings import parse_definition


class Obis2HaSensorTestCase(TestCase):
    def test_unique_ids(self):
        unique_ids = UniqueIds()

        self.assertEqual(unique_ids.get_unique_uid('Foo'), 'foo')
        self.assertEqual(unique_ids.get_unique_uid('Bar'), 'bar')

        self.assertEqual(unique_ids.get_unique_uid('Foo'), 'foo_2')

        self.assertEqual(unique_ids.get_unique_uid('Foo Bar !'), 'foo_bar')
        self.assertEqual(unique_ids.get_unique_uid('Foo Bar ?'), 'foo_bar_2')
        self.assertEqual(unique_ids.get_unique_uid('Foo Bar !'), 'foo_bar_3')

    def test_happy_path(self):
        with self.assertLogs(logger=None):
            obis2ha_sensors = Obis2HaSensors(
                definitions=parse_definition(name='ebz_dd3'),
                device=MqttDevice(name='Foo', uid='parent_uid'),
            )

        all_keys = sorted(obis2ha_sensors.obis_key2sensor.keys())
        self.assertEqual(all_keys[-3:], ['1-0:96.5.0*255', '1-0:96.5.5*255', 'identifier'])

        sensor = obis2ha_sensors['1-0:32.7.0*255']
        self.assertIsInstance(sensor, Sensor)
        self.assertEqual(sensor.name, 'Spannung L1')
        self.assertEqual(sensor.uid, 'parent_uid-spannung_l1')
        self.assertEqual(sensor.device_class, 'voltage')
        self.assertEqual(sensor.state_class, 'measurement')
        self.assertEqual(sensor.unit_of_measurement, 'V')
        self.assertEqual(sensor.suggested_display_precision, 1)
        self.assertEqual(sensor.min_value, 200)
        self.assertEqual(sensor.max_value, 260)
