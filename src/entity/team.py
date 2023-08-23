"""
author: oluiscabral
date: 8/23/23
"""
from dataclasses import dataclass
from typing import List

from entity.availability import Availability
from entity.city import City
from entity.court import Court
from entity.division import Division
from entity.match import Match
from entity.player import Player


@dataclass(frozen=True)
class Team:
    id: str
    city: City
    home_court: Court
    division: Division
    players: List[Player]
    past_matches: List[Match]
    availability: Availability

    def __hash__(self):
        return hash(self.id)
