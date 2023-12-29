import grp
import time
from pathlib import Path

import serial
from rich import print  # noqa
from serial.tools.list_ports_posix import comports


def get_serial(
    baudrate=9600,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS,
    timeout=1,
    terminator=b'\r\n',
    verbose=True,
):
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

        port_stat = Path(port).stat()
        print(f'{port} file mode:', oct(port_stat.st_mode))
        print(f'{port} user ID:', port_stat.st_uid)
        print(f'{port} user group ID:', port_stat.st_gid)
        user_group_name = grp.getgrgid(port_stat.st_gid).gr_name
        print(f'{port} user group: {user_group_name!r}')

        try:
            ser = serial.Serial(
                port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=timeout,
            )
        except Exception as err:
            if verbose:
                print(f'[red]ERROR: {err}')
                print()
                print('Hint:')
                print(f'\t[blue]sudo usermod -a -G {user_group_name} $USER')
                print('and try again ;)')
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
            print('[red]Can\'t read from. Try next serial.')

    if not checked_ports:
        print('[red]No serial ports found!')


def print_detect_serial():
    ser = get_serial(verbose=True)
    if ser:
        print('[green]Found serial:')
        print(ser)
