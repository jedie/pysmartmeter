"""
    Allow pysmartmeter to be executable
    through `python -m pysmartmeter`.
"""
from pysmartmeter import cli


def main():
    cli.main()


if __name__ == '__main__':
    main()
