import logging
import sys
from pprint import pp

from cli_base.cli_tools.verbosity import setup_logging
from cli_base.tyro_commands import TyroVerbosityArgType
from rich import print  # noqa
from rich.pretty import pprint

from pysmartmeter.cli_app import app
from pysmartmeter.detect_serial import get_serial
from pysmartmeter.parser import ObisParser
from pysmartmeter.user_settings import Hichi, UserSettings, get_user_settings


logger = logging.getLogger(__name__)


def _get_hichi_instance(verbosity: int) -> Hichi:
    user_settings: UserSettings = get_user_settings(verbosity)
    hichi_instance: Hichi = user_settings.hichi_instance
    return hichi_instance


@app.command
def print_detect_serial(verbosity: TyroVerbosityArgType):
    """
    Tries to find a working serial port and display RAW data from it.
    """
    setup_logging(verbosity=verbosity)
    ser = get_serial(verbose=True)
    if ser:
        print('[green]Found serial:')
        print(ser)


@app.command
def dump(verbosity: TyroVerbosityArgType):
    """
    Dump the output of the first working serial port.
    """
    setup_logging(verbosity=verbosity)

    def print_callback(**kwargs):
        pprint(kwargs, indent_guides=False)

    ser = get_serial()
    if not ser:
        print('Serial not found')
        sys.exit(1)

    parser = ObisParser(publish_callback=print_callback)

    while True:
        data = ser.readline()
        print(repr(data))
        parser.feed_line(data)


@app.command
def print_definitions(verbosity: TyroVerbosityArgType):
    """
    Print the used definitions
    """
    setup_logging(verbosity=verbosity)

    hichi_instance: Hichi = _get_hichi_instance(verbosity)
    definitions = hichi_instance.get_definitions()
    pp(definitions)
