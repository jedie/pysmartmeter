from unittest import TestCase

from rich.pretty import pprint


class BaseTestCase(TestCase):
    def assert_verbose(self, got, excepted):
        try:
            self.assertEqual(
                got,
                excepted,
            )
        except AssertionError:
            print('-' * 100)
            pprint(got, indent_guides=False)
            print('-' * 100)
            raise
