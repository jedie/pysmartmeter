import shlex
import subprocess
import sys


def verbose_check_call(*popenargs, verbose: bool = True, exit_on_error: bool = False, **kwargs):
    print(f'+{shlex.join(str(part) for part in popenargs)}')
    try:
        subprocess.check_call(popenargs, **kwargs)
    except subprocess.CalledProcessError as err:
        if verbose:
            print(f'Process "{popenargs[0]}" finished with exit code {err.returncode!r}')
        if exit_on_error:
            sys.exit(err.returncode)
        raise
