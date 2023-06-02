import dataclasses

from pysmartmeter.user_settings import UserSettings


@dataclasses.dataclass
class Config:
    verbosity: int
    settings: UserSettings
