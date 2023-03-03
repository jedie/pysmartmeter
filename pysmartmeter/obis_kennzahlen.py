# Auszug einiger OBIS Kennzahlen
# OBIS Kennzahl = 129-129:199.130.03*255  -> OBIS Kennzahl in HEX: 81 81 C7 82 03 FF    Herstelleridentifikation
# OBIS Kennzahl = 1-0:0.0.1*255           -> OBIS Kennzahl in HEX: 01 00 00 00 00 FF    ServerId, Id-Nnummer
# OBIS Kennzahl für Gerätenummer=ServerID -> OBIS Kennzahl in HEX: 01 00 00 00 09 FF    Geräteeinzelidentifikation
# OBIS Kennzahl = 1-0:1.8.0*255           -> OBIS Kennzahl in HEX: 01 00 01 08 00 FF    Wirkenergie, Total, Bezug
# OBIS Kennzahl = 1-0:2.8.0*255           -> OBIS Kennzahl in HEX: 01 00 02 08 00 FF    Wirkenergie, Total, Lieferung
# OBIS Kennzahl = 1-0:1.8.1*255           -> OBIS Kennzahl in HEX: 01 00 01 08 01 FF    Wirkenergie, Tarif 1, Bezug
# OBIS Kennzahl = 1-0:2.8.1*255           -> OBIS Kennzahl in HEX: 01 00 02 08 01 FF    Wirkenergie, Tarif 1, Lieferung
# OBIS Kennzahl = 1-0:1.8.2*255           -> OBIS Kennzahl in HEX: 01 00 01 08 02 FF    Wirkenergie, Tarif 2, Bezug
# OBIS Kennzahl = 1-0:2.8.2*255           -> OBIS Kennzahl in HEX: 01 00 02 08 02 FF    Wirkenergie, Tarif 2, Lieferung
# OBIS Kennzahl für Public Key            -> OBIS Kennzahl in HEX: 81 81 C7 82 05 FF    Public Key

# Sample for binary telegram (concat to one line). Store it in Env SML_BINARY_TEST_MESSAGE:
"""
1b1b1b1b010101017605032b180f620062007263010176010105010e5d5b0b000000000000000000000101634900007605032b181062006200
7263070177010b00000000000000000000070100620affff72620165021a587f7d77078181c78203ff010101010449534b0177070100000009ff
010101010b000000000000000000000177070100010800ff650001018001621e52ff590000000001c90ca70177070100010801ff0101621e52ff
590000000001c90ca70177070100010802ff0101621e52ff5900000000000000000177070100020800ff0101621e52ff59000000000000000001
77070100020801ff0101621e52ff5900000000000000000177070100020802ff0101621e52ff5900000000000000000177070100100700ff0101
621b5200550000005b0177070100240700ff0101621b520055000000170177070100380700ff0101621b5200550000002e01770701004c0700ff
0101621b520055000000150177078181c78205ff0101010183020000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000010101635486007605032b18116200620072630201710163fa36001b1b1b1b1a00f703
"""
import math
from datetime import datetime
from enum import IntEnum

from pysmartmeter.config_manager import ConfigManager
from pysmartmeter.data_classes import ObisValue
from pysmartmeter.utilities.string_utils import slugify


class ObisTupel(IntEnum):
    NUMMER = 0
    TEXT = 1
    PROCESS = 2


class ObisGen:
    def __init__(self, *, publish_callback):
        self._config_manager = ConfigManager()
        self._publish_callback = publish_callback
        self._verbose = self._config_manager.MODULE_OBIS_VERBOSE
        self._add_timestamp = self._config_manager.ADD_TIMESTAMP
        self._external_server_id = self._config_manager.EXTERNAL_SERVER_ID

    _UNIT = {"1B": "W",
             "1E": "Wh",
             "1D": "var",
             "20": "varh",
             "21": "A",
             "23": "V",
             "2C": "Hz",

             }

    _smartmeter = {"070100000009FF": ("1-0:0.0.1*255", "Server ID", True),
                   "070100010800FF": ("1-0:1.8.0*255", "Wirkenergie, Total, Bezug", True),
                   "070100020800FF": ("1-0:2.8.0*255", "Wirkenergie, Total, Lieferung", True),
                   "070100010801FF": ("1-0:1.8.1*255", "Wirkenergie, Tarif 1, Bezug", True),
                   "070100020801FF": ("1-0:2.8.1*255", "Wirkenergie, Tarif 1, Lieferung", True),
                   "070100010802FF": ("1-0:1.8.2*255", "Wirkenergie, Tarif 2, Bezug", True),
                   "070100020802FF": ("1-0:2.8.2*255", "Wirkenergie, Tarif 2, Lieferung", True),
                   "070100100700FF": ("1-0:16.7.0*255", "Aktuelle Gesamtwirkleistung", True),
                   "070100240700FF": ("1-0:36.7.0*255", "Aktuelle Gesamtwirkleistung, Phase L1", True),
                   "070100380700FF": ("1-0:56.7.0*255", "Aktuelle Gesamtwirkleistung, Phase L2", True),
                   "0701004C0700FF": ("1-0:76.7.0*255", "Aktuelle Gesamtwirkleistung, Phase L2", True),
                   "078181C78203FF": ("129-129:199.130.3*255", "Herstelleridentifikation", False),
                   "078181C78205FF": ("129-129:199.130.5*255", "Public Key", False)
                   }

    """ Specific Handler for Smartmeter"""

    def _resolve_obis_value(self, kv_store, key):
        obis_metadata = self._smartmeter.get(kv_store[key + '-7'], None)
        if obis_metadata is None:
            return None

        if not obis_metadata[ObisTupel.PROCESS]:
            return None

        obis_number = obis_metadata[ObisTupel.NUMMER]
        # Server ID
        if obis_number == "1-0:0.0.1*255":
            server_id = self._external_server_id
            if server_id is None:
                server_id = kv_store[key + '-2'][2:]
            return ["identifier", slugify(obis_number), obis_metadata[ObisTupel.TEXT],
                    server_id, server_id, None, None]
        else:
            if self._verbose:
                print("Obis: " + obis_number)
            unit = self._UNIT[kv_store[key + '-4'][2:]]
            scaler_raw = int.from_bytes(bytes.fromhex(kv_store[key + '-3'][2:]), 'big', signed=True)
            scaler = math.pow(10, scaler_raw)
            val = int.from_bytes(bytes.fromhex(kv_store[key + '-2'][2:]), 'big', signed=True) * scaler
            if scaler_raw < 0:
                val = round(val, abs(scaler_raw))

            return [obis_number, slugify(obis_number), obis_metadata[ObisTupel.TEXT],
                    str(val) + "*" + unit, str(val), unit, unit]

    """Generic handler for smartmeter"""

    def send_smartmeter(self, kv_store):

        obis_list = []
        unix_timestamp = int(datetime.timestamp(datetime.utcnow()))

        for key in kv_store:
            value = kv_store[key]
            if value == '77':
                ret_val = self._resolve_obis_value(kv_store, key)
                if ret_val is not None:
                    if self._verbose:
                        print(ret_val)
                    obis = ObisValue(ret_val[0], ret_val[1], ret_val[2], ret_val[3],
                                     ret_val[4], ret_val[5], ret_val[6])
                    obis_list.append(obis)

        if self._add_timestamp:
            obis = ObisValue("utc_timestamp", slugify("utc_timestamp"),
                             "UTC unixtime", str(unix_timestamp), str(unix_timestamp), 's', 's')
            obis_list.append(obis)

        self._publish_callback(obis_values=obis_list)

        return
