from enum import Enum
from typing import NamedTuple


class TelemetryData(NamedTuple):
    type: str
    name: str


class BaseTelemetryEnum(Enum):
    pass
