from pathlib import Path

from bx_py_utils.path import assert_is_file

import pysmartmeter


CLI_EPILOG = 'Project Homepage: https://github.com/jedie/pysmartmeter'

BASE_PATH = Path(pysmartmeter.__file__).parent

PACKAGE_ROOT = BASE_PATH.parent
assert_is_file(PACKAGE_ROOT / 'pyproject.toml')

SETTINGS_DIR_NAME = 'pysmartmeter'
SETTINGS_FILE_NAME = 'pysmartmeter'
