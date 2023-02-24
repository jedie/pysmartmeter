import getpass
import logging
import shutil
import sys
from pathlib import Path

import rich_click as click
from bx_py_utils.path import assert_is_file
from manageprojects.git import Git
from manageprojects.utilities import code_style
from manageprojects.utilities.subprocess_utils import verbose_check_call
from manageprojects.utilities.version_info import print_version
from rich import print  # noqa
from rich.pretty import pprint
from rich_click import RichGroup

import pysmartmeter
from pysmartmeter import __version__, constants
from pysmartmeter.data_classes import MqttSettings
from pysmartmeter.detect_serial import print_detect_serial
from pysmartmeter.dump import serial_dump
from pysmartmeter.log_utils import log_config
from pysmartmeter.publish_loop import publish_forever
from pysmartmeter.utilities import systemd
from pysmartmeter.utilities.credentials import get_mqtt_settings, store_mqtt_settings


logger = logging.getLogger(__name__)


PACKAGE_ROOT = Path(pysmartmeter.__file__).parent.parent
assert_is_file(PACKAGE_ROOT / 'pyproject.toml')

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


cli.add_command(systemd_stop)


@click.command()
def mypy(verbose: bool = True):
    """Run Mypy (configured in pyproject.toml)"""
    verbose_check_call('mypy', '.', cwd=PACKAGE_ROOT, verbose=verbose, exit_on_error=True)


cli.add_command(mypy)


@click.command()
def coverage(verbose: bool = True):
    """
    Run and show coverage.
    """
    verbose_check_call('coverage', 'run', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'report', '--fail-under=50', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'json', verbose=verbose, exit_on_error=True)


cli.add_command(coverage)


@click.command()
def install():
    """
    Run pip-sync and install 'pysmartmeter' via pip as editable.
    """
    verbose_check_call('pip-sync', PACKAGE_ROOT / 'requirements.dev.txt')
    verbose_check_call('pip', 'install', '-e', '.')


cli.add_command(install)


@click.command()
def safety():
    """
    Run safety check against current requirements files
    """
    verbose_check_call('safety', 'check', '-r', 'requirements.dev.txt')


cli.add_command(safety)


@click.command()
def update():
    """
    Update "requirements*.txt" dependencies files
    """
    extra_env = dict(
        CUSTOM_COMPILE_COMMAND='./cli.py update',
    )
    bin_path = Path(sys.executable).parent

    pip_compile_base = [
        bin_path / 'pip-compile',
        '--verbose',
        '--allow-unsafe',  # https://pip-tools.readthedocs.io/en/latest/#deprecations
        '--resolver=backtracking',  # https://pip-tools.readthedocs.io/en/latest/#deprecations
        '--upgrade',
        '--generate-hashes',
    ]

    # Only "prod" dependencies:
    verbose_check_call(
        *pip_compile_base,
        'pyproject.toml',
        '--output-file',
        'requirements.txt',
        extra_env=extra_env,
    )

    # dependencies + "dev"-optional-dependencies:
    verbose_check_call(
        *pip_compile_base,
        'pyproject.toml',
        '--extra=dev',
        '--output-file',
        'requirements.dev.txt',
        extra_env=extra_env,
    )

    verbose_check_call('safety', 'check', '-r', 'requirements.dev.txt')

    # Install new dependencies in current .venv:
    verbose_check_call('pip-sync', 'requirements.dev.txt')


cli.add_command(update)


@click.command()
def publish():
    """
    Build and upload this project to PyPi
    """
    _run_unittest_cli(verbose=False, exit_after_run=False)  # Don't publish a broken state

    git = Git(cwd=PACKAGE_ROOT, detect_root=True)

    # TODO: Add the checks from:
    #       https://github.com/jedie/poetry-publish/blob/main/poetry_publish/publish.py

    dist_path = PACKAGE_ROOT / 'dist'
    if dist_path.exists():
        shutil.rmtree(dist_path)

    verbose_check_call(sys.executable, '-m', 'build')
    verbose_check_call('twine', 'check', 'dist/*')

    git_tag = f'v{__version__}'
    print('\ncheck git tag')
    git_tags = git.tag_list()
    if git_tag in git_tags:
        print(f'\n *** ERROR: git tag {git_tag!r} already exists!')
        print(git_tags)
        sys.exit(3)
    else:
        print('OK')

    verbose_check_call('twine', 'upload', 'dist/*')

    git.tag(git_tag, message=f'publish version {git_tag}')
    print('\ngit push tag to server')
    git.push(tags=True)


cli.add_command(publish)


@click.command()
@click.option('--color/--no-color', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def fix_code_style(color: bool = True, verbose: bool = False):
    """
    Fix code style of all pysmartmeter source code files via darker
    """
    code_style.fix(package_root=PACKAGE_ROOT, color=color, verbose=verbose)


cli.add_command(fix_code_style)


@click.command()
@click.option('--color/--no-color', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def check_code_style(color: bool = True, verbose: bool = False):
    """
    Check code style by calling darker + flake8
    """
    code_style.check(package_root=PACKAGE_ROOT, color=color, verbose=verbose)


cli.add_command(check_code_style)


@click.command()
def update_test_snapshot_files():
    """
    Update all test snapshot files (by remove and recreate all snapshot files)
    """

    def iter_snapshot_files():
        yield from PACKAGE_ROOT.rglob('*.snapshot.*')

    removed_file_count = 0
    for item in iter_snapshot_files():
        item.unlink()
        removed_file_count += 1
    print(f'{removed_file_count} test snapshot files removed... run tests...')

    # Just recreate them by running tests:
    _run_unittest_cli(
        extra_env=dict(
            RAISE_SNAPSHOT_ERRORS='0',  # Recreate snapshot files without error
        ),
        verbose=False,
        exit_after_run=False,
    )

    new_files = len(list(iter_snapshot_files()))
    print(f'{new_files} test snapshot files created, ok.\n')


cli.add_command(update_test_snapshot_files)


def _run_unittest_cli(extra_env=None, verbose=True, exit_after_run=True):
    """
    Call the origin unittest CLI and pass all args to it.
    """
    if extra_env is None:
        extra_env = dict()

    extra_env.update(
        dict(
            PYTHONUNBUFFERED='1',
            PYTHONWARNINGS='always',
        )
    )

    args = sys.argv[2:]
    if not args:
        if verbose:
            args = ('--verbose', '--locals', '--buffer')
        else:
            args = ('--locals', '--buffer')

    verbose_check_call(
        sys.executable,
        '-m',
        'unittest',
        *args,
        timeout=15 * 60,
        extra_env=extra_env,
    )
    if exit_after_run:
        sys.exit(0)


@click.command()  # Dummy command
def test():
    """
    Run unittests
    """
    _run_unittest_cli()


cli.add_command(test)


def _run_tox():
    verbose_check_call(sys.executable, '-m', 'tox', *sys.argv[2:])
    sys.exit(0)


@click.command()  # Dummy "tox" command
def tox():
    """
    Run tox
    """
    _run_tox()


cli.add_command(tox)


@click.command()
def version():
    """Print version and exit"""
    # Pseudo command, because the version always printed on every CLI call ;)
    sys.exit(0)


cli.add_command(version)


def main():
    print_version(pysmartmeter)

    if len(sys.argv) >= 2:
        # Check if we just pass a command call
        command = sys.argv[1]
        if command == 'test':
            _run_unittest_cli()
        elif command == 'tox':
            _run_tox()

    # Execute Click CLI:
    cli.name = './cli.py'
    cli()
