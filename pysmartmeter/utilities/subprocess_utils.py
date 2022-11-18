import shlex
import subprocess


def verbose_check_call(*args, **kwargs):
    print(f'+{shlex.join(str(part) for part in args)}')
    subprocess.check_call(args, **kwargs)
