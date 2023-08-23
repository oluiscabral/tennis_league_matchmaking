"""
author: oluiscabral
date: 8/23/23
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Player:
    id: str
    coordinates: Tuple[str, str]

    def __hash__(self):
        return hash(self.id)
