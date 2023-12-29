"""
    CLI for usage
"""
import logging
import sys
from pathlib import Path

import rich_click as click
from cli_base.cli_tools.verbosity import OPTION_KWARGS_VERBOSE, setup_logging
from cli_base.cli_tools.version_info import print_version
from cli_base.toml_settings.api import TomlSettings
from cli_base.toml_settings.exceptions import UserSettingsNotFound
from ha_services.mqtt4homeassistant.mqtt import get_connected_client
from rich import print  # noqa
from rich.console import Console
from rich.traceback import install as rich_traceback_install
from rich_click import RichGroup

import pysmartmeter
from pysmartmeter import constants
from pysmartmeter.config import Config
from pysmartmeter.constants import SETTINGS_DIR_NAME, SETTINGS_FILE_NAME
from pysmartmeter.detect_serial import print_detect_serial
from pysmartmeter.dump import serial_dump
from pysmartmeter.publish_loop import publish_forever
from pysmartmeter.user_settings import MqttSettings, UserSettings, migrate_old_settings
from pysmartmeter.utilities import systemd


logger = logging.getLogger(__name__)


OPTION_ARGS_DEFAULT_TRUE = dict(is_flag=True, show_default=True, default=True)
OPTION_ARGS_DEFAULT_FALSE = dict(is_flag=True, show_default=True, default=False)
ARGUMENT_EXISTING_DIR = dict(
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path)
)
ARGUMENT_NOT_EXISTING_DIR = dict(
    type=click.Path(exists=False, file_okay=False, dir_okay=True, readable=False, writable=True, path_type=Path)
)
ARGUMENT_EXISTING_FILE = dict(
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path)
)


class ClickGroup(RichGroup):  # FIXME: How to set the "info_name" easier?
    def make_context(self, info_name, *args, **kwargs):
        info_name = './cli.py'
        return super().make_context(info_name, *args, **kwargs)


@click.group(
    cls=ClickGroup,
    epilog=constants.CLI_EPILOG,
)
def cli():
    pass


######################################################################################################
# User settings

toml_settings = TomlSettings(
    dir_name=SETTINGS_DIR_NAME,
    file_name=SETTINGS_FILE_NAME,
    settings_dataclass=UserSettings(),
    not_exist_exit_code=None,  # Don't sys.exit() if settings file not present, yet.
)
migrate_old_settings(toml_settings)  # TODO: Remove in the Future

try:
    user_settings: UserSettings = toml_settings.get_user_settings(debug=True)
except UserSettingsNotFound:
    # Use default one
    user_settings = UserSettings()


option_kwargs_usb_port = dict(
    required=True,
    type=str,
    help='USB port Hichi smartmeter e.g.: /dev/ttyUSB0',
    default=user_settings.hichi.port or None,  # Don't accept empty string: We need a address ;)
    show_default=True,
)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def edit_settings(verbosity: int):
    """
    Edit the settings file. On first call: Create the default one.
    """
    setup_logging(verbosity=verbosity)
    toml_settings.open_in_editor()


cli.add_command(edit_settings)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def debug_settings(verbosity: int):
    """
    Display (anonymized) MQTT server username and password
    """
    setup_logging(verbosity=verbosity)
    toml_settings.print_settings()


cli.add_command(debug_settings)


######################################################################################################


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def detect_serial(verbosity: int):
    """
    Just print the detected serial port instance
    """
    setup_logging(verbosity=verbosity)
    config = Config(verbosity=verbosity, settings=user_settings)
    print_detect_serial(config)


cli.add_command(detect_serial)


@click.command()
@click.option('-p', '--port', **option_kwargs_usb_port)
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def dump(port: str, verbosity: int):
    """
    Just dump serial output
    """
    setup_logging(verbosity=verbosity)
    user_settings.hichi.port = port
    config = Config(verbosity=verbosity, settings=user_settings)
    serial_dump(config)


cli.add_command(dump)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def publish_loop(verbosity: int):
    """
    Publish current data via MQTT (endless loop)
    """
    setup_logging(verbosity=verbosity)
    config = Config(verbosity=verbosity, settings=user_settings)
    try:
        publish_forever(config=config)
    except KeyboardInterrupt:
        print('Bye, bye')


cli.add_command(publish_loop)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def test_mqtt_connection(verbosity: int):
    """
    Test connection to MQTT Server
    """
    setup_logging(verbosity=verbosity)
    mqtt_settings: MqttSettings = user_settings.mqtt
    mqttc = get_connected_client(settings=mqtt_settings, verbosity=verbosity)
    mqttc.loop_start()
    mqttc.loop_stop()
    mqttc.disconnect()
    print('\n[green]Test succeed[/green], bye ;)')


cli.add_command(test_mqtt_connection)


@click.command()
def debug_systemd_service():
    """
    Just print the systemd service file content
    """
    content = systemd.compile_service()
    print(content)


cli.add_command(debug_systemd_service)


@click.command()
def setup_systemd_service():
    """
    Setup PySmartMeter systemd services and starts it.
    """
    systemd.write_service_file()
    systemd.enable_service()
    systemd.restart_service()
    systemd.status()


cli.add_command(setup_systemd_service)


@click.command()
def systemd_status():
    """
    Call systemd status of PySmartMeter services
    """
    systemd.status()


cli.add_command(systemd_status)


@click.command()
def systemd_stop():
    """
    Stop PySmartMeter systemd services
    """
    systemd.stop()
    systemd.status()


cli.add_command(systemd_stop)


@click.command()
def systemd_restart():
    """
    Restart PySmartMeter systemd services
    """
    systemd.restart_service()
    systemd.status()


cli.add_command(systemd_restart)


@click.command()
def version():
    """Print version and exit"""
    # Pseudo command, because the version always printed on every CLI call ;)
    sys.exit(0)


cli.add_command(version)


def main():
    print_version(pysmartmeter)

    console = Console()
    rich_traceback_install(
        width=console.size.width,  # full terminal width
        show_locals=True,
        suppress=[click],
        max_frames=2,
    )

    # Execute Click CLI:
    cli.name = './cli.py'
    cli()
