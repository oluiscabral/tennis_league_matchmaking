"""
author: oluiscabral
date: 8/23/23
"""
from geopy.distance import geodesic


class MatchmakingEdge:

    def __init__(self, a: 'MatchMakingTeam', b: 'MatchmakingTeam'):
        self._a = a
        self._b = b
        self._distance_points = None
        self._past_matches_points = None

    @property
    def a(self) -> 'MatchmakingTeam':
        return self._a

    @property
    def b(self) -> 'MatchmakingTeam':
        return self._b

    @property
    def distance_points(self) -> float:
        if self._distance_points is None:
            self._distance_points = self._get_distance_points()
        return self._distance_points

    @property
    def past_matches_points(self) -> int:
        if self._past_matches_points is None:
            self._past_matches_points = self._get_past_matches_points()
        return self._past_matches_points

    def _get_distance_points(self):
        points = 0
        for player in self._a.players:
            for opponent in self._b.players:
                points += geodesic(player.coordinates, opponent.coordinates).mi
        return points

    def _get_past_matches_points(self):
        points = 0
        for match in self._a.past_matches:
            for contestant in match.contestants:
                if self._a.id == contestant:
                    continue
                if self._b.id == contestant:
                    points += 1
        return points
