import dataclasses
import logging
import sys
import tomllib
from pprint import pformat

from bx_py_utils.path import assert_is_file
from cli_base.systemd.data_classes import BaseSystemdServiceInfo, BaseSystemdServiceTemplateContext
from cli_base.toml_settings.api import TomlSettings
from ha_services.mqtt4homeassistant.data_classes import MqttSettings
from rich import print  # noqa

from pysmartmeter.constants import BASE_PATH, SETTINGS_DIR_NAME, SETTINGS_FILE_NAME


logger = logging.getLogger(__name__)


DEFINITION_FILES_PATH = BASE_PATH / 'definitions'


def parse_definition(name: str) -> dict:
    definition_file_path = DEFINITION_FILES_PATH / f'{name}.toml'
    logger.info('Loaded definitions from %s', definition_file_path)

    assert_is_file(definition_file_path)
    content = definition_file_path.read_text(encoding='UTF-8')
    definitions = tomllib.loads(content)
    logger.info('definitions: %s', pformat(definitions))
    return definitions


@dataclasses.dataclass
class Hichi:
    """
    The "name" is the prefix of "pysmartmeter/definitions/*.yaml" files!
    """

    name: str = 'ebz_dd3'
    manufacturer: str = 'eBZ'
    verbose_name: str = 'eBZ DD3'

    port: str = '/dev/ttyUSB0'

    timeout: float = 0.5
    retries: int = 3

    def get_definitions(self) -> dict:
        definitions = parse_definition(self.name)
        return definitions


@dataclasses.dataclass
class SystemdServiceTemplateContext(BaseSystemdServiceTemplateContext):
    """
    Context values for the systemd service file content
    """

    verbose_service_name: str = 'pysmartmeter'
    exec_start: str = f'{sys.executable} -m pysmartmeter publish-loop'


@dataclasses.dataclass
class SystemdServiceInfo(BaseSystemdServiceInfo):
    """
    Information for systemd helper functions
    """

    template_context: SystemdServiceTemplateContext = dataclasses.field(default_factory=SystemdServiceTemplateContext)


@dataclasses.dataclass
class UserSettings:
    """
    User settings for PySmartMeter
    """

    systemd: dataclasses = dataclasses.field(default_factory=SystemdServiceInfo)
    mqtt: dataclasses = dataclasses.field(default_factory=MqttSettings)
    hichi: dataclasses = dataclasses.field(default_factory=Hichi)


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
    user_settings: UserSettings = toml_settings.get_user_settings(debug=verbosity > 0)
    return user_settings
