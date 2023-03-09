# https://dewiki.de/Lexikon/OBIS-Kennzahlen
OBIS_KEY_MAP = {
    'identifier': 'Gerätetyp mit Software Version',
    '1-0:0.0.0*255': 'Eigentumsnummer',
    '1-0:96.1.0*255': 'Geräte-Identifikationsnummer',
    '0-0:96.1.255*255': 'Geräte-Identifikationsnummer',
    '1-0:1.8.0*255': 'Zählerstand Bezug (Tariflos)',
    '1-0:2.8.0*255': 'Zählerstand Lieferung (Tariflos)',
    '1-0:1.8.1*255': 'Zählerstand Bezug (Tarif 1)',
    '1-0:2.8.1*255': 'Zählerstand Lieferung (Tarif 1)',
    '1-0:1.8.2*255': 'Zählerstand Bezug (Tarif 2)',
    '1-0:2.8.2*255': 'Zählerstand Lieferung (Tarif 2)',
    '1-0:16.7.0*255': 'Momentan-Leistungen',
    '1-0:36.7.0*255': 'Momentane Leistung L1',
    '1-0:56.7.0*255': 'Momentane Leistung L2',
    '1-0:76.7.0*255': 'Momentane Leistung L3',
    '1-0:32.7.0*255': 'Spannung L1',
    '1-0:52.7.0*255': 'Spannung L2',
    '1-0:72.7.0*255': 'Spannung L3',
    '1-0:96.5.0*255': 'Betriebszustand',
    '0-0:96.8.0*255': 'Betriebsdauer',
    '1-0:1.7.0*255': 'Momentan-Leistungen',
    '1-0:21.7.0*255': 'Wirkleistung L1 Bezug (Momentan)',
    '1-0:41.7.0*255': 'Wirkleistung L2 Bezug (Momentan)',
    '1-0:61.7.0*255': 'Wirkleistung L3 Bezug (Momentan)',
    '1-0:96.5.5*255': 'Status',
}

OBIS_OPERATION_DURATION_KEY = '0-0:96.8.0*255'

DEFAULT_HS_STATE = 'measurement'
OBIS_KEY2HA_STATE_CLASS = {
    '1-0:1.8.0*255': 'total',
    '1-0:2.8.0*255': 'total',
    '1-0:1.8.1*255': 'total',
    '1-0:2.8.1*255': 'total',
    '1-0:1.8.2*255': 'total',
    '1-0:2.8.2*255': 'total',
}
DEFAULT_HS_DEVICE_CLASS = 'energy'
OBIS_KEY2HA_DEVICE_CLASS = {
    '1-0:32.7.0*255': 'voltage',
    '1-0:52.7.0*255': 'voltage',
    '1-0:72.7.0*255': 'voltage',
}
