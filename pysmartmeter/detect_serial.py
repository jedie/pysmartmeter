import grp
import logging
import time
from pathlib import Path

import serial
from rich import print  # noqa
from serial.tools.list_ports_posix import comports


logger = logging.getLogger(__name__)


def get_serial_port(port) -> serial.Serial:
    port_stat = Path(port).stat()

    logger.info('Connect to serial port: %s', port)
    logger.info('file mode: %s', oct(port_stat.st_mode))
    logger.info('user ID: %s', port_stat.st_uid)
    logger.info('user group ID: %s', port_stat.st_gid)
    user_group_name = grp.getgrgid(port_stat.st_gid).gr_name
    logger.info('user group: %r', user_group_name)

    ser = serial.Serial(
        port,
        baudrate=9600,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.SEVENBITS,
        timeout=1,
    )
    return ser


def get_serial(terminator=b'\r\n', verbose=True):
    """
    Get the first "working" serial instance back.
    """
    if verbose:
        print('[cyan]Detect Serial...')

    checked_ports = []
    for port, desc, hwid in comports(include_links=False):
        checked_ports.append(port)
        if verbose:
            print('_' * 100)
            print(f'[magenta]try: {port} {desc} {hwid}')

        try:
            ser = get_serial_port(port)
        except Exception as err:
            if verbose:
                print(f'[red]ERROR: {err}')
                print()
                print('Hint:')
                print('\t[blue]sudo usermod -a -G <user-group> $USER')
                print('and try again ;)')
                print('See README for more details.')
                print('-' * 100)
            continue

        if verbose:
            print(f'Read from {ser}...', flush=True)

        for _try_count in range(5):
            try:
                data = ser.readline()
            except Exception as err:
                if verbose:
                    print(f'[yellow]ERROR: {err}')
                time.sleep(0.1)
                continue
            else:
                if verbose:
                    print(data)
                if data.endswith(terminator):
                    return ser

        if verbose:
            print("[red]Can't read from. Try next serial.")

    if not checked_ports:
        print('[red]No serial ports found!')
