"""
    Allow pysmartmeter to be executable
    through `python -m pysmartmeter`.
"""


from pysmartmeter.cli import cli_app


def main():
    cli_app.main()


if __name__ == '__main__':
    main()
