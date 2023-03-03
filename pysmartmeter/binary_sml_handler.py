from crccheck.crc import Crc16X25

from pysmartmeter.config_manager import ConfigManager


class ParserBinMessage:
    _idx = 0
    _stack = []
    _kv_store = {}
    _msg_hex = ""
    _akt_byte = ""
    _nxt_byte = ""
    _start_pattern = b'\x1B\x1B\x1B\x1B\x01\x01\x01\x01'
    _end_pattern = b'\x1B\x1B\x1B\x1B\x1A'
    _end_pattern_len = 8
    _ba: bytearray = bytearray()

    def __init__(self, verbose: bool = True):
        self._config_manager = ConfigManager()
        self._verbose = verbose
        self._verbose = self._config_manager.MODULE_BINPARSER_VERBOSE
        self._clear()
        _ba: bytearray = bytearray()

    def _clear(self):
        self._idx = 8
        self._stack = [1]

    def _get_bytes(self):
        idx_a = 2 * self._idx
        self._akt_byte = self._msg_hex[idx_a:idx_a + 2]
        self._nxt_byte = self._msg_hex[idx_a + 2:idx_a + 4]
        return self._akt_byte, self._nxt_byte

    def _calc_dist(self, is_long=False):
        if is_long:
            return int(self._akt_byte[1], 16) * 16 + int(self._nxt_byte[1], 16)
        else:
            return int(self._akt_byte[1], 16)

    def _idx_step(self, idx_delta, list_idx_delta):

        value = self._msg_hex[self._idx * 2: (self._idx + idx_delta) * 2]
        key = '-'.join(map(str, self._stack))
        self._kv_store[key] = value

        self._idx += idx_delta
        if list_idx_delta >= 0:
            self._stack.append(list_idx_delta)
            # self._stack[-1] += -1
        else:
            if self._akt_byte != "00":
                self._stack[-1] += -1
            else:
                del self._stack[1:-1]
                self._stack[0] += 2
                self._stack[-1] += -1

        while self._stack[-1] <= 0:
            self._stack.pop()
            self._stack[-1] += -1

    def _traverse_sml(self, msg_hex):

        self._msg_hex = msg_hex

        idx_prev = self._idx
        execute = True
        while execute:
            self._get_bytes()
            if self._akt_byte == '00':        # End of element list
                self._idx_step(1, -1)
            elif self._akt_byte[0] == '0':    # List of byte
                self._idx_step(self._calc_dist(), -1)
            elif self._akt_byte[0] == '8':    # Long list of byte
                self._idx_step(self._calc_dist(True), -1)
            elif self._akt_byte[0] == '7':    # List of elements
                self._idx_step(1, self._calc_dist())
            elif self._akt_byte[0] == 'F':    # Long list of elements
                self._idx_step(1, self._calc_dist(True))
            elif self._akt_byte[0] == '6':    # Unsigned Integer
                self._idx_step(self._calc_dist(), -1)
            elif self._akt_byte[0] == '5':    # Integer
                self._idx_step(self._calc_dist(), -1)

            if self._idx == idx_prev:
                execute = False
            idx_prev = self._idx

        if self._verbose:
            for kv in self._kv_store:
                print(kv + ": " + self._kv_store[kv])
            print()

        return self._kv_store

    def handle_received_bytes(self, br):
        if self._config_manager.SML_BINARY_TEST_MESSAGE is not None:
            br = self._config_manager.SML_BINARY_TEST_MESSAGE
        ret_val = None
        self._ba.extend(br)

        start_value = self._ba.find(self._start_pattern)
        end_value = self._ba.find(self._end_pattern, start_value + 1)
        array_len = len(self._ba)
        # Check: start pattern found, end pattern found, 8 trailing chars (fill,crc)
        if start_value >= 0 and end_value >= 0 and (array_len - end_value) >= 8:

            msg = self._ba[start_value:end_value + 8]
            crc = Crc16X25.calc(msg[0:-2]).to_bytes(2, 'little').hex().upper()

            if msg[-2:].hex().upper() == crc:
                kv_store = self._traverse_sml(msg.hex().upper())
                self._clear()
                del self._ba[0:end_value + self._end_pattern_len]
                ret_val = kv_store
            else:
                print("Failed crc check")
                del self._ba[0:end_value + self._end_pattern_len]

        return ret_val
