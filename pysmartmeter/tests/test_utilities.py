from unittest import TestCase

from pysmartmeter.utilities.string_utils import slugify


class UtilitiesTestCase(TestCase):
    def test_slugify(self):
        self.assertEqual(slugify('Test äöü ß'), 'Testaou')
        self.assertEqual(slugify('1-0:96.1.0*255'), '109610255')
        self.assertEqual(slugify('EBZ5DD3BZ06ETA_107'), 'EBZ5DD3BZ06ETA107')

        self.assertEqual(slugify('Test äöü ß', sep='-'), 'Test-aou')
        self.assertEqual(slugify('1-0:96.1.0*255', sep='-'), '1-0-96-1-0-255')
        self.assertEqual(slugify('EBZ5DD3BZ06ETA_107', sep='-'), 'EBZ5DD3BZ06ETA-107')
