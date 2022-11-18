import sys

from rich.pretty import pprint

from pysmartmeter.detect_serial import get_serial
from pysmartmeter.parser import ObisParser


def print_callback(**kwargs):
    pprint(kwargs, indent_guides=False)


def serial_dump():
    """
    Dump the output of the first working serial port.
    """
    ser = get_serial()
    if not ser:
        print('Serial not found')
        sys.exit(1)

    parser = ObisParser(publish_callback=print_callback)

    while True:
        data = ser.readline()
        print(repr(data))
        parser.feed_line(data)


if __name__ == '__main__':
    try:
        serial_dump()
    except KeyboardInterrupt:
        print('\nbye, bye\n')
