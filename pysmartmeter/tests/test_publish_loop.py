from unittest.mock import patch

import paho.mqtt.client as mqtt
from bx_py_utils.test_utils.redirect import RedirectOut
from bx_py_utils.test_utils.snapshot import assert_snapshot
from ha_services.toml_settings.api import TomlSettings
from ha_services.toml_settings.test_utils.data_class_utils import MockTomlSettings
from manageprojects.tests.base import BaseTestCase

from pysmartmeter import __version__, publish_loop
from pysmartmeter.config import Config
from pysmartmeter.publish_loop import logger as publish_forever_logger
from pysmartmeter.publish_loop import publish_forever
from pysmartmeter.tests.data import TEST_DATA_BIG
from pysmartmeter.tests.mocks import MqttClientMock, SerialMock, SerialMockEnds, SocketMock
from pysmartmeter.user_settings import UserSettings


class CliTestCase(BaseTestCase):
    def test_publish_loop(self):
        mocked_serial = SerialMock(lines=TEST_DATA_BIG)
        mqtt_client = MqttClientMock()
        socket_mock = SocketMock()

        with patch.object(publish_loop, 'get_serial', mocked_serial), patch.object(
            mqtt, 'Client', mqtt_client
        ), patch.object(publish_loop, 'socket', socket_mock), MockTomlSettings(
            SettingsDataclass=UserSettings, settings_overwrites=dict()
        ) as mocked_toml_settings:
            mocked_settings = mocked_toml_settings.toml_settings.get_user_settings()
            self.assertIsInstance(mocked_settings, UserSettings)

            config = Config(verbosity=3, settings=mocked_settings)

            with self.assertRaises(SerialMockEnds), RedirectOut() as buffer:
                publish_forever(config=config)

        mqtt_client.assert_state(
            self,
            init=[[(), {'client_id': f'PySmartMeter v{__version__} on mocked get hostname'}]],
            enabled_logger=[publish_forever_logger],
            credentials=[{'password': 'foobarbaz', 'user_name': 'bar'}],
            connects=[{'host': 'foo.host.tld', 'port': 123}],
            loop_started=True,
        )
        published = mqtt_client.published
        self.assertGreaterEqual(len(published), 8)

        self.assertEqual(buffer.stderr, '')
        self.assert_in_content(
            got=buffer.stdout,
            parts=(
                f'PySmartMeter v{__version__}',
                'Connect foo.host.tld:123 ',
                'login with user: bxr password:fxxxxxxxz... OK',
                'Publish MQTT topic: homeassistant/sensor/EBZ5DD3BZ06ETA107/state',
            ),
        )

        self.assertEqual(socket_mock.getaddrinfos, [('foo.host.tld', 123)])

        assert_snapshot(got=published)
