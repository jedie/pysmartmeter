import sys
from pathlib import Path

from pysmartmeter.data_classes import MqttSettings


CREDENTIAL_FILE_PATH = Path('~/.pysmartmeter').expanduser()


def store_mqtt_settings(settings: MqttSettings):
    print(f'Store MQTT server settings into: {CREDENTIAL_FILE_PATH}')

    data_str = settings.as_json()

    CREDENTIAL_FILE_PATH.touch(exist_ok=True)
    CREDENTIAL_FILE_PATH.chmod(0o600)
    CREDENTIAL_FILE_PATH.write_text(data_str, encoding='UTF-8')
    return CREDENTIAL_FILE_PATH


def get_mqtt_settings(exit_on_missing_config = True) -> MqttSettings:
    try:
        data_str = CREDENTIAL_FILE_PATH.read_text(encoding='UTF-8')
    except FileNotFoundError as err:
        print(f'ERROR: File not found: {err}')
        print('(Hint save settings first with: "./cli.sh store-settings")')
        if (exit_on_missing_config):
       	    sys.exit(1)
        else:
            raise FileNotFoundError ("Config not found.")
    settings = MqttSettings.from_json(data_str)
    return settings
