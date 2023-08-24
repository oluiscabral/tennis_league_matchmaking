"""
author: oluiscabral
date: 8/23/23
"""
from abc import ABC
from typing import Set, List

from entity.match import Match
from entity.matchup import Matchup
from entity.team import Team


class TeamInteractor(ABC):

    def create_teams(self, input_data) -> Set[Team]:
        pass

    def save_matchups(self, matchups: List[Matchup]):
        pass


class TeamDatabase(ABC):

    def get_past_matches(self, team_id: str) -> List[Match]:
        pass

    def save_matches(self, matches: List[Match]):
        pass
