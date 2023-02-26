import socket
from unittest.mock import patch

import paho.mqtt.client as mqtt
from bx_py_utils.test_utils.redirect import RedirectOut
from bx_py_utils.test_utils.snapshot import assert_snapshot
from manageprojects.tests.base import BaseTestCase

from pysmartmeter import __version__, publish_loop
from pysmartmeter.data_classes import MqttSettings
from pysmartmeter.publish_loop import logger as publish_forever_logger
from pysmartmeter.publish_loop import publish_forever
from pysmartmeter.tests.mocks import MqttClientMock, SerialMock, SerialMockEnds


class CliTestCase(BaseTestCase):
    def test_publish_loop(self):
        mocked_serial = SerialMock(
            lines=(
                b'/EBZ5DD3BZ06ETA_107\r\n',
                b'\r\n',
                b'1-0:0.0.0*255(1EBZ0100000123)\r\n',
                b'1-0:96.1.0*255(1EBZ0100000123)\r\n',
                b'1-0:1.8.0*255(0010001*kWh)\r\n',
                b'1-0:96.5.0*255(001C0104)\r\n',
                b'0-0:96.8.0*255(000BEEF01)\r\n',
                b'!\r\n',
                b'/EBZ5DD3BZ06ETA_107\r\n',
                b'\r\n',
                b'1-0:0.0.0*255(1EBZ0100000123)\r\n',
                b'1-0:96.1.0*255(1EBZ0100000123)\r\n',
                b'1-0:1.8.0*255(0010002*kWh)\r\n',
                b'1-0:96.5.0*255(001C0104)\r\n',
                b'0-0:96.8.0*255(000BEEF02)\r\n',
                b'!\r\n',
            )
        )
        mqtt_client = MqttClientMock()

        with patch.object(publish_loop, 'get_serial', mocked_serial), patch.object(mqtt, 'Client', mqtt_client):
            with self.assertRaises(SerialMockEnds), RedirectOut() as buffer:
                publish_forever(
                    settings=MqttSettings(
                        host='foo.host.tld',
                        port=123,
                        user_name='bar',
                        password='foobarbaz',
                    ),
                    verbose=True,
                )

        mqtt_client.assert_state(
            self,
            init=[[(), {'client_id': f'PySmartMeter v{__version__} on {socket.gethostname()}'}]],
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

        assert_snapshot(got=published)
