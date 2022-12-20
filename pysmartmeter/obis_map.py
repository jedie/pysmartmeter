# https://dewiki.de/Lexikon/OBIS-Kennzahlen
OBIS_KEY_MAP = {
    'identifier': 'Gerätetyp mit Software Version',
    '1-0:0.0.0*255': 'Eigentumsnummer',
    '1-0:96.1.0*255': 'Geräte-Identifikationsnummer',
    '1-0:1.8.0*255': 'Zählerstand (Tariflos)',
    '1-0:16.7.0*255': 'Momentan-Leistungen',
    '1-0:36.7.0*255': 'Momentane Leistung L1',
    '1-0:56.7.0*255': 'Momentane Leistung L2',
    '1-0:76.7.0*255': 'Momentane Leistung L3',
    '1-0:32.7.0*255': 'Spannung L1',
    '1-0:52.7.0*255': 'Spannung L2',
    '1-0:72.7.0*255': 'Spannung L3',
    '1-0:96.5.0*255': 'Betriebszustand',
    '0-0:96.8.0*255': 'Betriebsdauer',
}

OBIS_OPERATION_DURATION_KEY = '0-0:96.8.0*255'

DEFAULT_HS_STATE = 'measurement'
OBIS_KEY2HA_STATE_CLASS = {
    '1-0:1.8.0*255': 'total',
    '0-0:96.8.0*255': 'total',
}
