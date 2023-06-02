import grp
import sys
import time
from pathlib import Path

import serial
from rich import print  # noqa
from serial.tools.list_ports_posix import comports

from pysmartmeter.config import Config


def get_serial(config: Config) -> serial.Serial:
    """
    Get serial instance
    """
    port = config.settings.hichi.port
    if config.verbosity:
        print(f'[cyan]Init Serial {port}...')

    port_stat = Path(port).stat()
    user_group_name = grp.getgrgid(port_stat.st_gid).gr_name
    if config.verbosity:
        print(f'{port} file mode:', oct(port_stat.st_mode))
        print(f'{port} user ID:', port_stat.st_uid)
        print(f'{port} user group ID:', port_stat.st_gid)
        print(f'{port} user group: {user_group_name!r}')

    try:
        return serial.Serial(
            port,
            baudrate=config.settings.hichi.baudrate,
            parity=config.settings.hichi.parity,
            stopbits=config.settings.hichi.stopbits,
            bytesize=config.settings.hichi.bytesize,
            timeout=config.settings.hichi.timeout,
        )
    except Exception as err:
        print(f'[red]ERROR: {err}')
        print()
        print('Hint:')
        print(f'\t[blue]sudo usermod -a -G {user_group_name} $USER')
        print('and try again ;)')
        print('-' * 100)
        sys.exit(1)


def print_detect_serial(config: Config, terminator=b'\r\n'):
    """
    List all serial ports
    """
    if config.verbosity:
        print('[cyan]Detect Serial...')

    checked_ports = []
    for port, desc, hwid in comports(include_links=False):
        checked_ports.append(port)
        if config.verbosity:
            print('_' * 100)
            print(f'[magenta]try: {port} {desc} {hwid}')

        port_stat = Path(port).stat()
        print(f'{port} file mode:', oct(port_stat.st_mode))
        print(f'{port} user ID:', port_stat.st_uid)
        print(f'{port} user group ID:', port_stat.st_gid)
        user_group_name = grp.getgrgid(port_stat.st_gid).gr_name
        print(f'{port} user group: {user_group_name!r}')

        try:
            ser = serial.Serial(
                port,
                baudrate=config.settings.hichi.baudrate,
                parity=config.settings.hichi.parity,
                stopbits=config.settings.hichi.stopbits,
                bytesize=config.settings.hichi.bytesize,
                timeout=config.settings.hichi.timeout,
            )
        except Exception as err:
            if config.verbosity:
                print(f'[red]ERROR: {err}')
                print()
                print('Hint:')
                print(f'\t[blue]sudo usermod -a -G {user_group_name} $USER')
                print('and try again ;)')
                print('-' * 100)
            continue

        if config.verbosity:
            print(f'Read from {ser}...', flush=True)

        for _try_count in range(5):
            try:
                data = ser.readline()
            except Exception as err:
                if config.verbosity:
                    print(f'[yellow]ERROR: {err}')
                time.sleep(0.1)
                continue
            else:
                if config.verbosity:
                    print(data)
                if data.endswith(terminator):
                    return ser

        if config.verbosity:
            print('[red]Can\'t read from. Try next serial.')

    if not checked_ports:
        print('[red]No serial ports found!')
