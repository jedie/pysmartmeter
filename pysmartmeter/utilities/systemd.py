import getpass
import os
import sys
from pathlib import Path
from subprocess import CalledProcessError

from manageprojects.utilities.subprocess_utils import verbose_check_call
from rich import print  # noqa

from pysmartmeter import __version__


SERVICE_NAME = 'pysmartmeter.service'
SYSTEMD_SERVICE_PATH = Path(f'/etc/systemd/system/{SERVICE_NAME}')

SYSTEMD_SERVICE_TEMPLATE = '''
[Unit]
Description=PySmartMeter {version}
After=syslog.target network.target

[Service]
User={user}
Group={group}
WorkingDirectory={work_dir}

ExecStart={python_bin} -m pysmartmeter publish-loop --no-log --no-verbose

Restart=always
RestartSec=5s
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=PySmartMeter

[Install]
WantedBy=multi-user.target
'''


def compile_service():

    user_name = os.environ.get('SUDO_USER', getpass.getuser())
    work_dir = Path(sys.executable).parent

    content = SYSTEMD_SERVICE_TEMPLATE.format(
        version=__version__,
        user=user_name,
        group=user_name,
        work_dir=work_dir,
        python_bin=sys.executable,
    )
    return content


def write_service_file():
    content = compile_service()
    print(f'Write "{SYSTEMD_SERVICE_PATH}"...')
    try:
        SYSTEMD_SERVICE_PATH.write_text(content, encoding='UTF-8')
    except PermissionError as err:
        print(f'ERROR: {err}')
        print('Please restart this command with "sudo" ;)')
        sys.exit(1)

    verbose_check_call('systemctl', 'daemon-reload')


def call_service_command(command: str):
    try:
        verbose_check_call('systemctl', command, SERVICE_NAME)
    except CalledProcessError as err:
        print('-' * 100)
        print(f'[red]ERROR: {err}')
        print('[blue bold](Hint: Maybe sudo is needed for this command!)')
        print('-' * 100)
        raise


def enable_service():
    print(f'Enable systemd service {SERVICE_NAME!r}')
    call_service_command('enable')


def restart_service():
    print(f'(re-)start systemd service {SERVICE_NAME!r}')
    call_service_command('restart')


def status():
    call_service_command('status')


def stop():
    call_service_command('stop')
