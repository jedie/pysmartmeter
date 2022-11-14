import enum
import re

ENCODING = 'ASCII'
TERMINATOR = '!\r\n'


class State(enum.Enum):
    identifier = 1
    separator = 2
    data = 3
    terminator = 4


ALL_STATES = [state for state in State]
DATA_SPLIT_RE = re.compile(r'(.+?)\((.+?)\)')


def parse_obis_values(line):
    matches = DATA_SPLIT_RE.findall(line)
    if not len(matches) == 1:
        print(f'ERROR with data line: {line!r}')
        return
    key, value = matches[0]
    unit = None
    if '*' in value:
        value, unit = value.split('*')
        value = float(value)
    return key, value, unit


class ObisParser:
    def __init__(self, *, publish_callback):
        self.publish_callback = publish_callback
        self.state = None

        self._buffer = {}

    def set_new_state(self, new_state):
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
        if self.state is None:
            # Start -> wait for terminator
            if line == TERMINATOR:
                self.set_new_state(State.identifier)
        elif self.state == State.identifier:
            self._buffer.clear()
            self._buffer[State.identifier.name] = (line.strip(), None)
            self.set_new_state(State.separator)
        elif self.state == State.separator:
            self.set_new_state(State.data)
        elif self.state == State.data:
            if line == TERMINATOR:
                self.set_new_state(State.terminator)
                self.publish_callback(data=self._buffer)
                self.set_new_state(State.identifier)
            else:
                try:
                    key, value, unit = parse_obis_values(line)
                    assert key not in self._buffer, f'Double {key} found!'
                except Exception as err:
                    print(f'ERROR parse line {line!r}: {err}')
                else:
                    self._buffer[key] = (value, unit)
        else:
            raise NotImplementedError
