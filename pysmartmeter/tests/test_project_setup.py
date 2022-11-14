from pathlib import Path
from unittest import TestCase

import tomli
from bx_py_utils.path import assert_is_file

import pysmartmeter
from pysmartmeter import __version__


PACKAGE_ROOT = Path(pysmartmeter.__file__).parent.parent


class ProjectSetupTestCase(TestCase):
    def test_version(self):
        pyproject_toml_path = Path(PACKAGE_ROOT, 'pyproject.toml')
        assert_is_file(pyproject_toml_path)

        self.assertIsNotNone(__version__)

        pyproject_toml = tomli.loads(pyproject_toml_path.read_text(encoding='UTF-8'))
        pyproject_version = pyproject_toml['tool']['poetry']['version']

        self.assertEqual(__version__, pyproject_version)
