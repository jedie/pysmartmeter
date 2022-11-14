import serial
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
    for port, desc, hwid in comports(include_links=False):
        if verbose:
            print(f'try: {port} {desc} {hwid}')
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
                print(f'ERROR: {err}')
            continue

        if verbose:
            print(f'Read from {ser}...', end=' ', flush=True)
        try:
            data = ser.readline()
        except Exception as err:
            if verbose:
                print(f'ERROR: {err}')
            continue
        else:
            if verbose:
                print(data)
            if data.endswith(terminator):
                return ser


def print_detect_serial():
    print('Detect Serial...')
    ser = get_serial()
    print(ser)
