from bx_py_utils.auto_doc import assert_readme_block
from bx_py_utils.path import assert_is_file
from manageprojects.test_utils.click_cli_utils import invoke_click
from manageprojects.tests.base import BaseTestCase

from pysmartmeter.cli.cli_app import cli
from pysmartmeter.cli.dev import PACKAGE_ROOT
from pysmartmeter.cli.dev import cli as dev_cli
from pysmartmeter.constants import CLI_EPILOG


def assert_cli_help_in_readme(text_block: str, marker: str):
    README_PATH = PACKAGE_ROOT / 'README.md'
    assert_is_file(README_PATH)

    text_block = text_block.replace(CLI_EPILOG, '')
    text_block = f'```\n{text_block.strip()}\n```'
    assert_readme_block(
        readme_path=README_PATH,
        text_block=text_block,
        start_marker_line=f'[comment]: <> (✂✂✂ auto generated {marker} start ✂✂✂)',
        end_marker_line=f'[comment]: <> (✂✂✂ auto generated {marker} end ✂✂✂)',
    )


class ReadmeTestCase(BaseTestCase):
    def test_main_help(self):
        stdout = invoke_click(cli, '--help')
        self.assert_in_content(
            got=stdout,
            parts=(
                'Usage: ./cli.py [OPTIONS] COMMAND [ARGS]...',
                'detect-serial',
                'setup-systemd-service',
                CLI_EPILOG,
            ),
        )
        assert_cli_help_in_readme(text_block=stdout, marker='main help')

    def test_dev_help(self):
        stdout = invoke_click(dev_cli, '--help')
        self.assert_in_content(
            got=stdout,
            parts=(
                'Usage: ./dev-cli.py [OPTIONS] COMMAND [ARGS]...',
                'check-code-style',
                'fix-code-style',
                CLI_EPILOG,
            ),
        )
        assert_cli_help_in_readme(text_block=stdout, marker='dev help')
