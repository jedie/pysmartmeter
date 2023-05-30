"""
    CLI for development
"""
import logging
import sys
from pathlib import Path

import rich_click as click
from ha_services.cli_tools.dev_tools import _run_tox, _run_unittest_cli
from manageprojects.utilities import code_style
from manageprojects.utilities.publish import publish_package
from manageprojects.utilities.subprocess_utils import verbose_check_call
from manageprojects.utilities.version_info import print_version
from rich import print  # noqa; noqa
from rich_click import RichGroup

import pysmartmeter
from pysmartmeter import constants
from pysmartmeter.constants import PACKAGE_ROOT


logger = logging.getLogger(__name__)


OPTION_ARGS_DEFAULT_TRUE = dict(is_flag=True, show_default=True, default=True)
OPTION_ARGS_DEFAULT_FALSE = dict(is_flag=True, show_default=True, default=False)
ARGUMENT_EXISTING_DIR = dict(
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path)
)
ARGUMENT_NOT_EXISTING_DIR = dict(
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        readable=False,
        writable=True,
        path_type=Path,
    )
)
ARGUMENT_EXISTING_FILE = dict(
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path)
)


class ClickGroup(RichGroup):  # FIXME: How to set the "info_name" easier?
    def make_context(self, info_name, *args, **kwargs):
        info_name = './dev-cli.py'
        return super().make_context(info_name, *args, **kwargs)


@click.group(
    cls=ClickGroup,
    epilog=constants.CLI_EPILOG,
)
def cli():
    pass


@click.command()
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def mypy(verbose: bool = True):
    """Run Mypy (configured in pyproject.toml)"""
    verbose_check_call('mypy', '.', cwd=PACKAGE_ROOT, verbose=verbose, exit_on_error=True)


cli.add_command(mypy)


@click.command()
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def coverage(verbose: bool = True):
    """
    Run and show coverage.
    """
    verbose_check_call('coverage', 'run', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'combine', '--append', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'report', '--fail-under=30', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'xml', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'json', verbose=verbose, exit_on_error=True)


cli.add_command(coverage)


@click.command()
def install():
    """
    Run pip-sync and install 'inverter' via pip as editable.
    """
    verbose_check_call('pip-sync', PACKAGE_ROOT / 'requirements.dev.txt')
    verbose_check_call('pip', 'install', '--no-deps', '-e', '.')


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
    bin_path = Path(sys.executable).parent

    verbose_check_call(bin_path / 'pip', 'install', '-U', 'pip')
    verbose_check_call(bin_path / 'pip', 'install', '-U', 'pip-tools')

    extra_env = dict(
        CUSTOM_COMPILE_COMMAND='./cli.py update',
    )

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

    verbose_check_call(bin_path / 'safety', 'check', '-r', 'requirements.dev.txt')

    # Install new dependencies in current .venv:
    verbose_check_call(bin_path / 'pip-sync', 'requirements.dev.txt')


cli.add_command(update)


@click.command()
def publish():
    """
    Build and upload this project to PyPi
    """
    _run_unittest_cli(verbose=False, exit_after_run=False)  # Don't publish a broken state

    publish_package(
        module=pysmartmeter,
        package_path=PACKAGE_ROOT,
    )


cli.add_command(publish)


@click.command()
@click.option('--color/--no-color', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def fix_code_style(color: bool = True, verbose: bool = False):
    """
    Fix code style of all inverter source code files via darker
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


@click.command()  # Dummy command
def test():
    """
    Run unittests
    """
    _run_unittest_cli()


cli.add_command(test)


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


######################################################################################################
# TODO:
#
# @click.command()
# @click.option('--force', **OPTION_ARGS_DEFAULT_FALSE)
# def create_default_settings(force):
#     """
#     Create a default user settings file. (Used by CI pipeline ;)
#     """
#     if not force and 'CI' not in os.environ:
#         print('We are not running in CI pipeline and "--force" not used -> Abort.')
#         sys.exit(-1)
#
#     settings_dataclass = UserSettings()
#     toml_settings = TomlSettings(
#         dir_name=SETTINGS_DIR_NAME,
#         file_name=SETTINGS_FILE_NAME,
#         settings_dataclass=settings_dataclass,
#     )
#
#     settings_path = toml_settings.file_path
#     if settings_path.is_file():
#         print(f'[green]Use settings file already exists here: {settings_path}')
#         return
#
#     document: TOMLDocument = dataclass2toml(instance=settings_dataclass)
#     doc_str = tomlkit.dumps(document, sort_keys=False)
#
#     settings_path.write_text(doc_str, encoding='UTF-8')
#     print(f'[green]Default settings file created here: {settings_path}')
#
#
# cli.add_command(create_default_settings)
#
######################################################################################################


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
    cli()
