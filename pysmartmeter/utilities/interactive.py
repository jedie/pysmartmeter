import sys


def confirm(txt):
    if input(f'\n{txt} (Y/N)').lower() not in ('y', 'j'):
        print('Bye.')
        sys.exit(-1)
