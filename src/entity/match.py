"""
author: oluiscabral
date: 8/23/23
"""
from dataclasses import dataclass
from typing import Tuple

from entity.city import City
from entity.court import Court
from entity.division import Division
from entity.schedule import Schedule


@dataclass(frozen=True)
class Match:
    id: str
    city: City
    court: Court
    schedule: Schedule
    division: Division
    contestants: Tuple['Team', 'Team']

    def __hash__(self):
        return hash(self.id)
