"""
author: oluiscabral
date: 8/23/23
"""
from dataclasses import dataclass
from typing import Tuple

from entity.availability import Availability
from entity.team import Team


@dataclass(frozen=True)
class Matchup:
    availability: Availability
    contestants: Tuple[Team, Team]
