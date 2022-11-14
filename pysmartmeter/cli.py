"""
    Allow pysmartmeter to be executable
    through `python -m pysmartmeter`.
"""
import typer

from pysmartmeter import __version__
from pysmartmeter.detect_serial import print_detect_serial
from pysmartmeter.dump import serial_dump


app = typer.Typer()


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


def main():
    print(f'PySmartMeter v{__version__}')
    app()
