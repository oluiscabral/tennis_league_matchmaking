"""
author: oluiscabral
date: 8/23/23
"""
from dataclasses import dataclass
from typing import Set

from entity.matchup import Matchup


@dataclass(frozen=True)
class MatchMakingResult:
    byes: int
    matchups: Set[Matchup]
    distance_points: float
    past_matches_points: int

    def is_better_than(self, other: 'MatchMakingResult'):
        if self.byes < other.byes:
            return True
        elif other.byes < self.byes:
            return False
        return self.distance_points < other.distance_points and self.past_matches_points <= self.past_matches_points
