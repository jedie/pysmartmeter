"""
    Allow pysmartmeter to be executable
    through `python -m pysmartmeter`.
"""
import shlex
import subprocess
import sys
from pathlib import Path

import typer
from bx_py_utils.path import assert_is_dir, assert_is_file

import pysmartmeter
from pysmartmeter import __version__
from pysmartmeter.detect_serial import print_detect_serial
from pysmartmeter.dump import serial_dump


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


def verbose_check_call(*args):
    print(f'+{shlex.join(str(part) for part in args)}')
    subprocess.check_call(args)


@app.command()
def detect_serial():
    """
    Just print the detected serial port instance
    """
    print_detect_serial()


@app.command()
def dump():
    """
    Just dump serial output
    """
    serial_dump()


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
    coverage_bin = which('coverage')
    verbose_check_call(coverage_bin, 'run')
    verbose_check_call(coverage_bin, 'report', '--fail-under=30')
    verbose_check_call(coverage_bin, 'json')


def main():
    print(f'PySmartMeter v{__version__}')
    if len(sys.argv) >= 2 and sys.argv[1] == 'test':
        # Just use the CLI from unittest with all available options and origin --help output ;)
        return test()
    else:
        app()
