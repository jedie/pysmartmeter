import dataclasses
from typing import Optional, Union


@dataclasses.dataclass
class ObisValue:
    """
    A "raw" Obis value
    """

    key: str  # origin name e.g.: '1-0:1.8.0*255'
    raw_value: str  # e.g.: '0010002*kWh'
    value: Union[str, float]  # e.g.: 10002.0
    raw_unit: Optional[str] = None  # e.g.: 'kWh'
    unit: Optional[str] = None  # e.g.: 'kWh'

    def copy(self) -> 'ObisValue':
        data = dataclasses.asdict(self)
        return ObisValue(**data)


@dataclasses.dataclass
class HomeassistantValue:
    """
    Obis value prepared for Homeassistant submission
    """

    unique_id: str
    value_key: str
    device_class: str  # e.g.: 'energy' / 'voltage'
    state_class: str
    obis_value: ObisValue

    @property
    def key(self):
        return self.obis_value.key


@dataclasses.dataclass
class MqttPayload:
    topic: str
    data: dict
