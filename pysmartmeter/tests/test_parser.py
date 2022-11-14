from pprint import pprint
from unittest import TestCase

from pysmartmeter.parser import ObisParser, parse_obis_values

RAW_TEST_DATA_SMALL = (
    b'/EBZ5DD3BZ06ETA_107\r\n',  # Manufacturer and software version
    b'\r\n',
    b'1-0:0.0.0*255(1EBZ0100000123)\r\n',  # Device-ID
    b'1-0:96.1.0*255(1EBZ0100000123)\r\n',
    b'1-0:1.8.0*255(012345*kWh)\r\n',
    b'1-0:96.5.0*255(001C0104)\r\n',  # operating state
    b'0-0:96.8.0*255(00017A9F)\r\n',  # == 96927sec (time of operation)
    b'!\r\n',
)


class ParserTestCase(TestCase):
    def test_parse_obis_values(self):
        result = parse_obis_values('1-0:0.0.0*255(1EBZ0100000123)\r\n')
        self.assertEqual(result, ('1-0:0.0.0*255', '1EBZ0100000123', None))

        result = parse_obis_values('1-0:1.8.0*255(012345*kWh)\r\n')
        self.assertEqual(result, ('1-0:1.8.0*255', 12345.0, 'kWh'))

    def parse(self, lines, expected_data):
        class PublisherMock:
            def __init__(self):
                self.data = []

            def __call__(self, **kwargs):
                self.data.append(kwargs)

        publish_mock = PublisherMock()
        parser = ObisParser(publish_callback=publish_mock)

        for line in lines:
            parser.feed_line(line)
        try:
            self.assertEqual(
                publish_mock.data,
                expected_data,
            )
        except AssertionError:
            print('-' * 100)
            pprint(publish_mock.data)
            print('-' * 100)
            raise

    def test_happy_path(self):
        self.parse(
            lines=RAW_TEST_DATA_SMALL + RAW_TEST_DATA_SMALL,
            expected_data=[
                {
                    'data': {
                        'identifier': ('/EBZ5DD3BZ06ETA_107', None),
                        '1-0:0.0.0*255': ('1EBZ0100000123', None),
                        '1-0:96.1.0*255': ('1EBZ0100000123', None),
                        '1-0:1.8.0*255': (12345.0, 'kWh'),
                        '1-0:96.5.0*255': ('001C0104', None),
                        '0-0:96.8.0*255': ('00017A9F', None),
                    }
                }
            ],
        )

    def test_start_in_the_middle(self):
        lines = (
            b'55(001C0104)\r\n',
            b'0-0:96.8.0*255(00017A9F)\r\n',
            b'!\r\n',
        ) + RAW_TEST_DATA_SMALL
        self.parse(
            lines=lines,
            expected_data=[
                {
                    'data': {
                        'identifier': ('/EBZ5DD3BZ06ETA_107', None),
                        '1-0:0.0.0*255': ('1EBZ0100000123', None),
                        '1-0:96.1.0*255': ('1EBZ0100000123', None),
                        '1-0:1.8.0*255': (12345.0, 'kWh'),
                        '1-0:96.5.0*255': ('001C0104', None),
                        '0-0:96.8.0*255': ('00017A9F', None),
                    }
                }
            ],
        )
