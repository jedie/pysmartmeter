import dataclasses
import json
import logging
import sys
from pathlib import Path

import serial
import tomlkit
from ha_services.mqtt4homeassistant.data_classes import MqttSettings as OriginMqttSettings
from cli_base.systemd.data_classes import BaseSystemdServiceInfo, BaseSystemdServiceTemplateContext
from cli_base.toml_settings.api import TomlSettings
from cli_base.toml_settings.serialize import dataclass2toml
from tomlkit import TOMLDocument


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class MqttSettings(OriginMqttSettings):
    """
    MQTT server settings.
    """

    host: str = 'mqtt.your-server.tld'


@dataclasses.dataclass
class SystemdServiceTemplateContext(BaseSystemdServiceTemplateContext):
    """
    Context values for the systemd service file content
    """

    verbose_service_name: str = 'Inverter Connect'
    exec_start: str = f'{sys.executable} -m inverter publish-loop'


@dataclasses.dataclass
class SystemdServiceInfo(BaseSystemdServiceInfo):
    """
    Information for systemd helper functions
    """

    template_context: SystemdServiceTemplateContext = dataclasses.field(default_factory=SystemdServiceTemplateContext)


@dataclasses.dataclass
class Hichi:
    """
    Information about the Hichi Smartmeter aka "volkszaehler.org"
    Defaults: 9600 7E1
    """

    port: str = '/dev/ttyUSB0'
    baudrate: int = 9600
    bytesize: int = serial.SEVENBITS
    parity: str = serial.PARITY_EVEN
    stopbits: int = serial.STOPBITS_ONE
    timeout: int = 1


@dataclasses.dataclass
class UserSettings:
    """
    User settings for PySmartMeter
    """

    systemd: dataclasses = dataclasses.field(default_factory=SystemdServiceInfo)
    mqtt: dataclasses = dataclasses.field(default_factory=MqttSettings)
    hichi: dataclasses = dataclasses.field(default_factory=Hichi)


def migrate_old_settings(toml_settings: TomlSettings):  # TODO: Remove in the Future
    file_path = toml_settings.file_path  # '~/config/pysmartmeter/pysmartmeter.toml'
    if file_path.is_file():
        logger.debug('New settings file exists: %s -> no migration needed', file_path)
        return

    old_settings_file_path = Path('~/.pysmartmeter').expanduser()
    if not old_settings_file_path.is_file():
        logger.debug('No old settings file found: %s -> no migration needed', old_settings_file_path)
        return

    logger.warning('Migrate old settings file %s to %s', old_settings_file_path, file_path)

    data_str = old_settings_file_path.read_text(encoding='UTF-8')
    data = json.loads(data_str)

    user_settings = UserSettings()
    user_settings.mqtt.host = data['host']
    user_settings.mqtt.port = data['port']
    user_settings.mqtt.user_name = data['user_name']
    user_settings.mqtt.password = data['password']

    document: TOMLDocument = dataclass2toml(instance=user_settings)
    doc_str = tomlkit.dumps(document, sort_keys=False)

    file_path.write_text(doc_str, encoding='UTF-8')
    logger.info('New settings file stored to: %s', file_path)

    if input(f'\nRemove old settings file {old_settings_file_path.name} (Y/N)').lower() in ('y', 'j'):
        old_settings_file_path.unlink()
        logger.info('Remove old settings file %s', old_settings_file_path)


###########################################################################################################


def get_toml_settings() -> TomlSettings:
    toml_settings = TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=UserSettings(),
        not_exist_exit_code=None,  # Don't sys.exit() if settings file not present, yet.
    )
    return toml_settings


def get_user_settings(verbosity: int) -> UserSettings:
    toml_settings: TomlSettings = get_toml_settings()
    migrate_old_settings(toml_settings)  # TODO: Remove in the Future
    user_settings: UserSettings = toml_settings.get_user_settings(debug=verbosity > 0)
    return user_settings
