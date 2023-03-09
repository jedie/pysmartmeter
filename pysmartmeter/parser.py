import enum
import re

from rich import print as rprint
from rich.pretty import pprint

from pysmartmeter.data_classes import ObisValue
from pysmartmeter.obis_map import OBIS_KEY_MAP
from pysmartmeter.utilities.string_utils import slugify


ENCODING = 'ASCII'
TERMINATOR = '!\r\n'


class State(enum.Enum):
    identifier = 1
    separator = 2
    data = 3
    terminator = 4


ALL_STATES = [state for state in State]
DATA_SPLIT_RE = re.compile(r'(.+?)\((.+?)\)')


def parse_obis_value(line) -> ObisValue:
    matches = DATA_SPLIT_RE.findall(line)
    if not len(matches) == 1:
        raise ValueError(f'Regex. does not match for line: {line!r}')

    key, raw_value = matches[0]
    value = raw_value
    raw_unit = None
    unit = None
    if key == '0-0:96.8.0*255':  # time of operation in hex
        try:
            value = int(raw_value, 16)
        except Exception as err:
            print(f'Convert {raw_value!r} error: {err}')
        else:
            unit = 'sec.'
    elif '*' in raw_value:
        value, raw_unit = raw_value.split('*')
        try:
            value = float(value)
        except Exception as err:
            print(f'Convert {raw_value!r} error: {err}')

        unit = raw_unit

    name = OBIS_KEY_MAP.get(key, key)

    return ObisValue(
        key=key,
        key_slug=slugify(key, sep='_'),
        name=name,
        raw_value=raw_value,
        value=value,
        raw_unit=raw_unit,
        unit=unit,
    )


class ObisParser:
    def __init__(self, *, publish_callback, verbose=False):
        self.publish_callback = publish_callback
        self.verbose = verbose

        self.state = None
        self._seen_keys = None
        self._buffer = None

    def set_new_state(self, new_state):
        if self.verbose:
            print(f'state: {self.state} -> {new_state}')

        if self.state is None:
            assert (
                new_state == State.identifier
            ), f'New state {new_state.name!r} is not {State.identifier.name!r}'
        elif new_state == State.identifier:
            assert (
                self.state == State.terminator
            ), f'Current state {self.state.name!r} is not {State.terminator.name!r}'
        else:
            current_position = ALL_STATES.index(self.state)
            correct_new_state = ALL_STATES[current_position + 1]
            assert (
                new_state == correct_new_state
            ), f'New state {new_state.name!r} is not {correct_new_state.name!r}'

        self.state = new_state

    def feed_line(self, data):
        line = data.decode(ENCODING)
        if self.verbose:
            rprint(f'[code]{data!r} -> {line!r}')
        if not line:
            if self.verbose:
                print('ignore empty data')
        elif self.state is None:
            if self.verbose:
                print('-' * 100)
                print('Start -> wait for terminator')
            if line == TERMINATOR:
                self.set_new_state(State.identifier)
        elif self.state == State.identifier:
            if self.verbose:
                print('New buffer...', end=' ')
            key = State.identifier.name
            self._buffer = [
                ObisValue(
                    key=key,
                    key_slug=key,
                    name=OBIS_KEY_MAP.get(key, key),
                    raw_value=line.strip(),
                    value=line.strip('/ \r\n'),
                )
            ]
            self._seen_keys = {key}
            if self.verbose:
                print(self._buffer)
            self.set_new_state(State.separator)
        elif self.state == State.separator:
            self.set_new_state(State.data)
        elif self.state == State.data:
            if line == TERMINATOR:
                self.set_new_state(State.terminator)
                if self.verbose:
                    print(f'Expose buffer to callback {self.publish_callback}:')
                    pprint(self._buffer)
                self.publish_callback(obis_values=self._buffer)
                self.set_new_state(State.identifier)
                if self.verbose:
                    print('-' * 100)
            else:
                try:
                    obis_value: ObisValue = parse_obis_value(line)
                    assert obis_value.key not in self._seen_keys, f'Double {obis_value.key} found!'
                except Exception as err:
                    print(f'ERROR parse line {line!r}: {err}')
                else:
                    if self.verbose:
                        print(f'Store: {obis_value}')
                    self._buffer.append(obis_value)
                    self._seen_keys.add(obis_value.key)
        else:
            raise NotImplementedError
