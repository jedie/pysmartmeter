from unittest.mock import patch

from manageprojects.test_utils.click_cli_utils import invoke_click
from manageprojects.tests.base import BaseTestCase

from pysmartmeter import detect_serial
from pysmartmeter.cli import cli_app
from pysmartmeter.cli.cli_app import cli
from pysmartmeter.data_classes import MqttSettings


class CliTestCase(BaseTestCase):
    def test_publish_loop(self):
        settings = MqttSettings(
            host='foo.host.tld',
            port=123,
            user_name='bar',
            password='foobarbaz',
        )

        class PublishForever:
            calls = []

            def __call__(self, **kwargs):
                self.calls.append(kwargs)
                raise KeyboardInterrupt

        mocked_publish_forever = PublishForever()

        with patch.object(cli_app, 'get_mqtt_settings', return_value=settings), patch.object(
            cli_app, 'publish_forever', mocked_publish_forever
        ):
            stdout = invoke_click(cli, 'publish-loop')

        self.assertEqual(mocked_publish_forever.calls, [{'settings': settings, 'verbose': True}])
        self.assert_in_content(
            got=stdout,
            parts=(
                'foo.host.tld',
                'fxxxxxxxz',
                'Bye, bye',
            ),
        )

    def test_detect_serial(self):
        with patch.object(detect_serial, 'comports', return_value=[]):
            stdout = invoke_click(cli, 'detect-serial')

        self.assert_in_content(
            got=stdout,
            parts=(
                'Detect Serial...',
                'No serial ports found!',
            ),
        )
