from bx_py_utils.test_utils.snapshot import assert_snapshot

from pysmartmeter.data_classes import ObisValue
from pysmartmeter.parser import parse_obis_value
from pysmartmeter.tests.base import BaseTestCase
from pysmartmeter.tests.data import (
    RawObisDataMock,
    get_obis_data_block,
    test_data2obis_parser_result,
)
from pysmartmeter.utilities.serializer import serialize_values


class ParserTestCase(BaseTestCase):
    def test_raw_data_mock(self):
        rdm = RawObisDataMock()
        self.assert_verbose(
            got=tuple(rdm.iter_block(count=2)),
            excepted=(
                b'/EBZ5DD3BZ06ETA_107\r\n',
                b'\r\n',
                b'1-0:0.0.0*255(1EBZ0100000123)\r\n',
                b'1-0:96.1.0*255(1EBZ0100000123)\r\n',
                b'1-0:1.8.0*255(0010001*kWh)\r\n',
                b'1-0:96.5.0*255(001C0104)\r\n',
                b'0-0:96.8.0*255(000BEEF01)\r\n',
                b'!\r\n',
                b'/EBZ5DD3BZ06ETA_107\r\n',
                b'\r\n',
                b'1-0:0.0.0*255(1EBZ0100000123)\r\n',
                b'1-0:96.1.0*255(1EBZ0100000123)\r\n',
                b'1-0:1.8.0*255(0010002*kWh)\r\n',
                b'1-0:96.5.0*255(001C0104)\r\n',
                b'0-0:96.8.0*255(000BEEF02)\r\n',
                b'!\r\n',
            ),
        )

    def test_parse_obis_values(self):
        result = parse_obis_value('1-0:0.0.0*255(1EBZ0100000123)\r\n')
        self.assertEqual(
            result,
            ObisValue(
                key='1-0:0.0.0*255',
                key_slug='1_0_0_0_0_255',
                name='Eigentumsnummer',
                raw_value='1EBZ0100000123',
                value='1EBZ0100000123',
                raw_unit=None,
                unit=None,
            ),
        )

        result = parse_obis_value('1-0:1.8.0*255(012345*kWh)\r\n')
        self.assertEqual(
            result,
            ObisValue(
                key='1-0:1.8.0*255',
                key_slug='1_0_1_8_0_255',
                name='Zählerstand Bezug (Tariflos)',
                raw_value='012345*kWh',
                value=12345.0,
                raw_unit='kWh',
                unit='kWh',
            ),
        )

        result = parse_obis_value('0-0:96.8.0*255(00BEEF002)\r\n')
        self.assertEqual(
            result,
            ObisValue(
                key='0-0:96.8.0*255',
                key_slug='0_0_96_8_0_255',
                name='Betriebsdauer',
                raw_value='00BEEF002',
                value=200208386,
                raw_unit=None,
                unit='sec.',
            ),
        )

    def test_happy_path(self):
        parsed_bock_data = get_obis_data_block(count=2)
        self.assertEqual(len(parsed_bock_data), 2)
        self.assert_verbose(
            got=parsed_bock_data[0]['obis_values'][0],
            excepted=ObisValue(
                key='identifier',
                key_slug='identifier',
                name='Gerätetyp mit Software Version',
                raw_value='/EBZ5DD3BZ06ETA_107',
                value='EBZ5DD3BZ06ETA_107',
                raw_unit=None,
                unit=None,
            ),
        )
        self.assert_verbose(
            got=parsed_bock_data[0]['obis_values'][1],
            excepted=ObisValue(
                key='1-0:0.0.0*255',
                key_slug='1_0_0_0_0_255',
                name='Eigentumsnummer',
                raw_value='1EBZ0100000123',
                value='1EBZ0100000123',
                raw_unit=None,
                unit=None,
            ),
        )
        assert_snapshot(got=serialize_values(parsed_bock_data))

    def test_start_in_the_middle(self):
        rdm = RawObisDataMock()
        lines = [
            b'55(001C0104)\r\n',
            b'0-0:96.8.0*255(00017A9F)\r\n',
            b'!\r\n',
        ]
        lines += list(rdm.iter_block(count=1))
        parsed_bock_data = test_data2obis_parser_result(
            lines=lines,
            # verbose=True
        )
        self.assertEqual(len(parsed_bock_data), 1)
        self.assert_verbose(
            got=parsed_bock_data[0]['obis_values'][0],
            excepted=ObisValue(
                key='identifier',
                key_slug='identifier',
                name='Gerätetyp mit Software Version',
                raw_value='/EBZ5DD3BZ06ETA_107',
                value='EBZ5DD3BZ06ETA_107',
                raw_unit=None,
                unit=None,
            ),
        )
        self.assert_verbose(
            got=parsed_bock_data[0]['obis_values'][1],
            excepted=ObisValue(
                key='1-0:0.0.0*255',
                key_slug='1_0_0_0_0_255',
                name='Eigentumsnummer',
                raw_value='1EBZ0100000123',
                value='1EBZ0100000123',
                raw_unit=None,
                unit=None,
            ),
        )
        assert_snapshot(got=serialize_values(parsed_bock_data))

    def test_interim_incorrect_data(self):
        rdm = RawObisDataMock()

        # Start with good data:
        lines = list(rdm.iter_block(count=2))
        lines += [
            b'/EBZ5DD3BZ06ETA_107\r\n',
            b'\r\n',
            b'1-0:0.0.0*255(1EBZ0100000123)\r\n',
            # incorrect data:
            b'foo\rbar\n',
            b'bam\x00boom\n\r',
        ]
        # Correct data:
        lines += list(rdm.iter_block(count=1))
        parsed_bock_data = test_data2obis_parser_result(
            lines=lines,
            # verbose=True
        )
        self.assertEqual(len(parsed_bock_data), 2)
        self.assert_verbose(
            got=parsed_bock_data[0]['obis_values'][0],
            excepted=ObisValue(
                key='identifier',
                key_slug='identifier',
                name='Gerätetyp mit Software Version',
                raw_value='/EBZ5DD3BZ06ETA_107',
                value='EBZ5DD3BZ06ETA_107',
                raw_unit=None,
                unit=None,
            ),
        )
        self.assert_verbose(
            got=parsed_bock_data[0]['obis_values'][1],
            excepted=ObisValue(
                key='1-0:0.0.0*255',
                key_slug='1_0_0_0_0_255',
                name='Eigentumsnummer',
                raw_value='1EBZ0100000123',
                value='1EBZ0100000123',
                raw_unit=None,
                unit=None,
            ),
        )
        assert_snapshot(got=serialize_values(parsed_bock_data))

    def test_handle_empty_line(self):
        line_block = [
            b'',
            b'/ESY5Q3DB1024 V3.04\r\n',
            b'\r\n',
            b'1-0:0.0.0*255(FOOBAR#ETN)\r\n',
            b'1-0:1.8.0*255(00032331.4981013*kWh)\r\n',
            b'1-0:2.8.0*255(00025393.8469367*kWh)\r\n',
            b'1-0:21.7.0*255(002291.51*W)\r\n',
            b'1-0:41.7.0*255(000038.11*W)\r\n',
            b'1-0:61.7.0*255(000250.99*W)\r\n',
            b'1-0:1.7.0*255(002580.61*W)\r\n',
            b'1-0:96.5.5*255(80)\r\n',
            b'0-0:96.1.255*255(1ESY1304004XXX)\r\n',
            b'!\r\n',
        ]
        parsed_bock_data = test_data2obis_parser_result(
            lines=line_block + line_block,
            # verbose=True
        )
        self.assert_verbose(
            got=parsed_bock_data[0]['obis_values'][1],
            excepted=ObisValue(
                key='1-0:0.0.0*255',
                key_slug='1_0_0_0_0_255',
                name='Eigentumsnummer',
                raw_value='FOOBAR#ETN',
                value='FOOBAR#ETN',
                raw_unit=None,
                unit=None,
            ),
        )
        assert_snapshot(got=serialize_values(parsed_bock_data))
