"""
author: oluiscabral
date: 8/23/23
"""
from abc import ABC
from typing import Set

from entity.team import Team


class Matchmaking(ABC):

    def get_best_matchups(self, teams: Set[Team]):
        pass
