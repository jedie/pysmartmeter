import dataclasses
from unittest import TestCase

from bx_py_utils.test_utils.snapshot import assert_snapshot

from pysmartmeter.user_settings import Hichi


class UserSettingsTestCase(TestCase):
    def test_hichi_dataclass(self):
        hichi = Hichi()
        self.assertEqual(hichi.manufacturer, 'eBZ')
        self.assertEqual(hichi.verbose_name, 'eBZ DD3')
        self.assertEqual(hichi.port, '/dev/ttyUSB0')

        with self.assertLogs(logger=None):
            definitions = hichi.get_definitions()
        self.assertIsInstance(definitions, dict)

        # Check samples:
        self.assertEqual(
            definitions['parameters'][0], {'obis_key': 'identifier', 'name': 'Gerätetyp mit Software Version'}
        )

        assert_snapshot(got=dataclasses.asdict(hichi))
