from unittest.mock import patch

import paho.mqtt.client as mqtt
from bx_py_utils.test_utils.snapshot import assert_text_snapshot
from manageprojects.test_utils.click_cli_utils import invoke_click
from manageprojects.tests.base import BaseTestCase

import pysmartmeter
from pysmartmeter import publish_loop
from pysmartmeter.cli import cli_app
from pysmartmeter.cli.cli_app import cli
from pysmartmeter.data_classes import MqttSettings
from pysmartmeter.tests.mocks import MqttClientMock, SocketMock


class TestMqttConnection(BaseTestCase):
    def test_via_cli(self):
        mqtt_client = MqttClientMock()
        socket_mock = SocketMock()
        settings = MqttSettings(
            host='foo.host.tld',
            port=123,
            user_name='bar',
            password='foobarbaz',
        )

        with patch.object(mqtt, 'Client', mqtt_client), patch.object(
            publish_loop, 'socket', socket_mock
        ), patch.object(cli_app, 'get_mqtt_settings', return_value=settings), patch.object(
            pysmartmeter, '__version__', '1.2.3'
        ):
            stdout = invoke_click(cli, 'test-mqtt-connection')

        self.assert_in_content(
            got=stdout,
            parts=(
                'Connect foo.host.tld:123 ',
                'Host/port test OK',
                'Test succeed',
            ),
        )
        assert_text_snapshot(got=stdout)
