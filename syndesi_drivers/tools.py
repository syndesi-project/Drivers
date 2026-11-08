# File : tools.py
# Author : Sébastien Deriaz
# License : GPL

from __future__ import annotations

from enum import StrEnum, Enum
import math
from typing import Any
#from typing import TypeVar

class NormalizedStrEnum(StrEnum):
    """
    A StrEnum with case-insensitive parsing
    """
    @classmethod
    def _missing_(cls, value: object) -> NormalizedStrEnum | None:
        if isinstance(value, str):
            normalized = value.strip().upper()
            for member in cls:
                if str(member.value).upper() == normalized:
                    return member
        return None

#E = TypeVar("E", bound="FloatStrEnum")


class NormalizedFloatStrEnum(str, Enum):
    """
    Enum that accepts str / int / float values and can parse them.

    Note:
    - Because Python considers 1 == 1.0, Enum will also treat them as the same value.
    """

    @classmethod
    def _missing_(cls, value : Any) -> NormalizedFloatStrEnum | None:
        # Exact match first
        for member in cls:
            if member.value == value:
                return member

        if isinstance(value, str):
            normalized = value.strip().upper()
            for member in cls:
                if str(member.value).upper() == normalized:
                    return member

        # Approximate float/int match
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            for member in cls:
                if isinstance(member.value, (int, float)) and math.isclose(
                    float(value),
                    float(member.value),
                    rel_tol=0.01,
                    abs_tol=0
                ):
                    return member

        return None

    # @classmethod
    # def parse(cls: type[E], value) -> E:
    #     return cls(value)
