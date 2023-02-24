import inspect
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from pysmartmeter.data_classes import MqttSettings
from pysmartmeter.utilities import credentials
from pysmartmeter.utilities.credentials import get_mqtt_settings, store_mqtt_settings


class CredentialsTestCase(TestCase):
    def test_basic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            mocked_temp_path = Path(temp_dir) / '.pysmartmeter'

            with patch.object(credentials, 'CREDENTIAL_FILE_PATH', mocked_temp_path):
                with self.assertRaises(FileNotFoundError) as exc:
                    get_mqtt_settings()
                err_msg = str(exc.exception)
                self.assertIn('No such file or directory:', err_msg)
                self.assertIn(str(mocked_temp_path), err_msg)

                path = store_mqtt_settings(
                    settings=MqttSettings(
                        host='foo',
                        port=123,
                        user_name='',
                        password='',
                    )
                )
                self.assertEqual(path, mocked_temp_path)
                self.assertEqual(
                    mocked_temp_path.read_text(),
                    inspect.cleandoc(
                        '''
                        {
                          "host": "foo",
                          "password": "",
                          "port": 123,
                          "user_name": ""
                        }
                        '''
                    ),
                )

                settings = get_mqtt_settings()
                self.assertEqual(
                    settings,
                    MqttSettings(
                        host='foo',
                        port=123,
                        user_name='',
                        password='',
                    ),
                )
