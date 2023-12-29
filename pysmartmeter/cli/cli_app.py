"""
    CLI for usage
"""
import getpass
import logging
import sys
from pathlib import Path

import rich_click as click
from cli_base.cli_tools.version_info import print_version
from rich import print  # noqa
from rich.console import Console
from rich.pretty import pprint
from rich.traceback import install as rich_traceback_install
from rich_click import RichGroup

import pysmartmeter
from pysmartmeter import constants
from pysmartmeter.data_classes import MqttSettings
from pysmartmeter.detect_serial import print_detect_serial
from pysmartmeter.dump import serial_dump
from pysmartmeter.log_utils import log_config
from pysmartmeter.publish_loop import get_connected_client, publish_forever
from pysmartmeter.utilities import systemd
from pysmartmeter.utilities.credentials import get_mqtt_settings, store_mqtt_settings


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


@click.command()
def detect_serial():
    """
    Just print the detected serial port instance
    """
    log_config()
    print_detect_serial()


cli.add_command(detect_serial)


@click.command()
def dump():
    """
    Just dump serial output
    """
    log_config()
    serial_dump()


cli.add_command(dump)


@click.command()
@click.option('--log/--no-log', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_TRUE)
def publish_loop(log: bool = True, verbose: bool = True):
    """
    Publish current data via MQTT (endless loop)
    """
    if log:
        log_config()
    settings: MqttSettings = get_mqtt_settings()
    pprint(settings.anonymized())
    try:
        publish_forever(settings=settings, verbose=verbose)
    except KeyboardInterrupt:
        print('Bye, bye')


cli.add_command(publish_loop)


@click.command()
def store_settings():
    """
    Store MQTT server settings.
    """
    log_config()

    try:
        settings: MqttSettings = get_mqtt_settings()
    except FileNotFoundError:
        print('No settings stored, yet. ok.')
        print()
        print('Input settings:')
    else:
        print('Current settings:')
        pprint(settings.anonymized())
        print()
        print('Input new settings:')

    host = input('host (e.g.: "test.mosquitto.org"): ')
    if not host:
        print('Host is needed! Abort.')
        sys.exit(1)

    port = input('port (default: 1883): ')
    if port:
        port = int(port)
    else:
        port = 1883
    user_name = input('user name: ')
    password = getpass.getpass('password: ')

    settings = MqttSettings(host=host, port=port, user_name=user_name, password=password)
    file_path = store_mqtt_settings(settings)
    print(f'MQTT server settings stored into: {file_path}')


cli.add_command(store_settings)


@click.command()
def debug_settings():
    """
    Display (anonymized) MQTT server username and password
    """
    log_config()
    settings: MqttSettings = get_mqtt_settings()
    pprint(settings.anonymized())


cli.add_command(debug_settings)


@click.command()
def test_mqtt_connection():
    """
    Test connection to MQTT Server
    """
    log_config()
    settings: MqttSettings = get_mqtt_settings()
    mqttc = get_connected_client(settings=settings, verbose=True)
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
