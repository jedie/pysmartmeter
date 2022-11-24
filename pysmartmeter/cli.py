import getpass
import os
import shutil
import sys
from pathlib import Path

import typer
from bx_py_utils.path import assert_is_dir, assert_is_file
from rich.pretty import pprint

import pysmartmeter
from pysmartmeter import __version__
from pysmartmeter.data_classes import MqttSettings
from pysmartmeter.detect_serial import print_detect_serial
from pysmartmeter.dump import serial_dump
from pysmartmeter.log_utils import log_config
from pysmartmeter.publish_loop import publish_forever
from pysmartmeter.utilities import subprocess_utils, systemd
from pysmartmeter.utilities.credentials import get_mqtt_settings, store_mqtt_settings


PACKAGE_ROOT = Path(pysmartmeter.__file__).parent.parent
assert_is_dir(PACKAGE_ROOT)
assert_is_file(PACKAGE_ROOT / 'pyproject.toml')

app = typer.Typer()


def which(file_name: str) -> Path:
    venv_bin_path = Path(sys.executable).parent
    assert venv_bin_path.is_dir()
    bin_path = venv_bin_path / file_name
    if not bin_path.is_file():
        raise FileNotFoundError(f'File {file_name}!r not found in {venv_bin_path}')
    return bin_path


def verbose_check_call(file_name, *args, **kwargs):
    file_name = which(file_name)
    kwargs.setdefault('cwd', PACKAGE_ROOT)
    subprocess_utils.verbose_check_call(
        file_name,
        *args,
        verbose=True,
        exit_on_error=True,
        **kwargs,
    )


@app.command()
def detect_serial():
    """
    Just print the detected serial port instance
    """
    log_config()
    print_detect_serial()


@app.command()
def dump():
    """
    Just dump serial output
    """
    log_config()
    serial_dump()


@app.command()
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


@app.command()
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


@app.command()
def debug_settings():
    """
    Display (anonymized) MQTT server username and password
    """
    log_config()
    settings: MqttSettings = get_mqtt_settings()
    pprint(settings.anonymized())


@app.command()
def debug_systemd_service():
    """
    Just print the systemd service file content
    """
    content = systemd.compile_service()
    print(content)


@app.command()
def setup_systemd_service():
    """
    Setup PySmartMeter systemd services and starts it.
    """
    systemd.write_service_file()
    systemd.enable_service()
    systemd.restart_service()


@app.command()
def systemd_status():
    """
    Call systemd status of PySmartMeter services
    """
    systemd.status()


@app.command()
def systemd_stop():
    """
    Stop PySmartMeter systemd services
    """
    systemd.stop()


def _call_darker(*, argv):
    from darker.__main__ import main as darker_main  # it's a dev requirements

    # Work-a-round for:
    #
    #   File ".../site-packages/darker/linting.py", line 148, in _check_linter_output
    #     with Popen(  # nosec
    #   ...
    #   File "/usr/lib/python3.10/subprocess.py", line 1845, in _execute_child
    #     raise child_exception_type(errno_num, err_msg, err_filename)
    # FileNotFoundError: [Errno 2] No such file or directory: 'flake8'
    #
    # Just add .venv/bin/ to PATH:
    venv_path = Path(sys.executable).parent
    assert_is_dir(venv_path)
    assert_is_file(venv_path / 'flake8')
    venv_path = str(venv_path)
    if venv_path not in os.environ['PATH']:
        os.environ['PATH'] = venv_path + os.pathsep + os.environ['PATH']

    result = darker_main(argv=argv)
    print(f'Darker returns: {result!r}')


@app.command()
def fix_code_style():
    """
    Fix code style via darker
    """
    _call_darker(argv=['--color'])


@app.command()
def check_code_style(verbose: bool = True):
    from flake8.main.cli import main as flake8_main  # it's a dev requirements

    _call_darker(argv=['--color', '--check'])
    if verbose:
        argv = ['--verbose']
    else:
        argv = []

    flake8_main(argv=argv)


@app.command()
def mypy(verbose: bool = False):
    """Run Mypy (configured in pyproject.toml)"""
    args = ['mypy']
    if verbose:
        args.append('--verbose')
    verbose_check_call(*args, PACKAGE_ROOT)


@app.command()  # Just add this command to help page
def test():
    """
    Run unittests
    """
    # Use the CLI from unittest module and pass all args to it:
    verbose_check_call(sys.executable, '-m', 'unittest', *sys.argv[2:])


@app.command()
def coverage():
    """
    Run and show coverage.
    """
    verbose_check_call('coverage', 'run')
    verbose_check_call('coverage', 'report', '--fail-under=30')
    verbose_check_call('coverage', 'json')


@app.command()
def publish():
    """
    Build and upload this project to PyPi
    """
    log_config()
    test()  # Don't publish a broken state

    # TODO: Add the checks from:
    #       https://github.com/jedie/poetry-publish/blob/main/poetry_publish/publish.py

    dist_path = PACKAGE_ROOT / 'dist'
    if dist_path.exists():
        shutil.rmtree(dist_path)

    subprocess_utils.verbose_check_call('poetry', 'build', verbose=True, exit_on_error=True)

    verbose_check_call('twine', 'check', 'dist/*')
    verbose_check_call('twine', 'upload', 'dist/*')


def main():
    print(f'PySmartMeter v{__version__}')
    if len(sys.argv) >= 2 and sys.argv[1] == 'test':
        # Just use the CLI from unittest with all available options and origin --help output ;)
        return test()
    else:
        app()
