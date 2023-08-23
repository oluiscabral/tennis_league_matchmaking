"""
author: oluiscabral
date: 8/23/23
"""
from dataclasses import dataclass
from datetime import date
from enum import Enum


class Period(Enum):
    MORNING = 1
    AFTERNOON = 2
    EVENING = 3


@dataclass(frozen=True)
class Schedule:
    week: int
    date: date
    period: Period
