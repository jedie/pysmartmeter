from pysmartmeter.data_classes import ObisValue
from pysmartmeter.parser import ObisParser


RAW_TEST_DATA_SMALL = (
    '/EBZ5DD3BZ06ETA_107\r\n'  # Manufacturer and software version
    '\r\n'
    '1-0:0.0.0*255(1EBZ0100000123)\r\n'  # Eigentumsnummer
    '1-0:96.1.0*255(1EBZ0100000123)\r\n'  # Geräte-Identifikationsnummer
    '1-0:1.8.0*255({kwh}*kWh)\r\n'  # Summe der Momentan-Leistungen in allen Phase
    '1-0:96.5.0*255(001C0104)\r\n'  # Betriebszustand
    '0-0:96.8.0*255({epoch})\r\n'  # Betriebsdauer in Sekunden
    '!\r\n'
)
RAW_TEST_DATA_BIG = (
    '/EBZ5DD3BZ06ETA_107\r\n'  # Manufacturer and software version
    '\r\n'
    '1-0:0.0.0*255(1EBZ0100000123)\r\n'  # Eigentumsnummer
    '1-0:96.1.0*255(1EBZ0100000123)\r\n'  # Geräte-Identifikationsnummer
    '1-0:1.8.0*255(005087.48789958*kWh)\r\n'  # Zählerstand Bezug (Tariflos)
    '1-0:16.7.0*255(000236.12*W)\r\n'  # Summe der Momentan-Leistungen in allen Phase
    '1-0:36.7.0*255(000212.65*W)\r\n'  # Momentane Leistung in Phase L1
    '1-0:56.7.0*255(000000.00*W)\r\n'  # Momentane Leistung in Phase L2
    '1-0:76.7.0*255(000023.47*W)\r\n'  # Momentane Leistung in Phase L3
    '1-0:32.7.0*255(234.2*V)\r\n'  # Spannung in Phase L1
    '1-0:52.7.0*255(235.1*V)\r\n'  # Spannung in Phase L2
    '1-0:72.7.0*255(231.8*V)\r\n'  # Spannung in Phase L3
    '1-0:96.5.0*255(001C0104)\r\n'  # Betriebszustand
    '0-0:96.8.0*255(00BEEF00)\r\n'  # Betriebsdauer in Sekunden
    '!\r\n'
)
TEST_DATA_BIG = tuple(
    line.encode('ASCII') for line in (RAW_TEST_DATA_BIG + RAW_TEST_DATA_BIG).splitlines(keepends=True)
)


class RawObisDataMock:
    def __init__(self):
        self.kwh = 10000
        self.epoch = 0x00BEEF00

    def iter_block(self, count=1):
        for _ in range(count):
            self.kwh += 1
            self.epoch += 1
            data_str = RAW_TEST_DATA_SMALL.format(
                kwh=f'{self.kwh:07}',
                epoch=f'{self.epoch:09X}',
            )
            for line in data_str.splitlines(keepends=True):
                yield line.encode('ASCII')


def test_data2obis_parser_result(lines, verbose=False):
    class PublisherMock:
        def __init__(self):
            self.data = []

        def __call__(self, **kwargs):
            self.data.append(kwargs)

    publish_mock = PublisherMock()
    parser = ObisParser(publish_callback=publish_mock, verbose=verbose)

    for line in lines:
        parser.feed_line(line)

    return publish_mock.data


def get_obis_data_block(count=1):
    rdm = RawObisDataMock()
    parsed_bock_data = test_data2obis_parser_result(
        lines=rdm.iter_block(count=count + 1),
        # verbose=True
    )
    return parsed_bock_data


def get_obis_values() -> list[ObisValue]:
    parsed_bock_data = get_obis_data_block(count=1)
    return parsed_bock_data[0]['obis_values']
