"""
author: oluiscabral
date: 8/23/23
"""
from dataclasses import dataclass
from typing import Tuple

from entity.availability import Availability


@dataclass(frozen=True)
class Match:
    id: str
    availability: Availability
    contestants: Tuple[str, str]

    def __hash__(self):
        return hash(self.id)
