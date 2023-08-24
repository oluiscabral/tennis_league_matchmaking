"""
author: oluiscabral
date: 8/23/23
"""
from typing import Set, List

from entity.availability import Availability
from entity.city import City
from entity.court import Court
from entity.division import Division
from entity.match import Match
from entity.player import Player
from entity.team import Team
from interactor.matchmaking.edge import MatchmakingEdge


class MatchmakingTeam:

    def __init__(self, team: Team):
        self._team: Team = team
        self._is_searching: bool = False
        self._edges: Set['MatchmakingEdge'] = set()
        self._best_edge: 'MatchmakingEdge | None' = None

    @property
    def id(self) -> str:
        return self._team.id

    @property
    def city(self) -> City:
        return self._team.city

    @property
    def home_court(self) -> Court:
        return self._team.home_court

    @property
    def division(self) -> Division:
        return self._team.division

    @property
    def players(self) -> List[Player]:
        return self._team.players

    @property
    def past_matches(self) -> List[Match]:
        return self._team.past_matches

    @property
    def availability(self) -> Availability:
        return self._team.availability

    @property
    def best_edge(self) -> MatchmakingEdge:
        return self._best_edge

    def is_searching(self) -> bool:
        return self._is_searching

    def has_found_best_edge(self) -> bool:
        return self._best_edge is not None

    def add_edge(self, edge: 'MatchmakingEdge'):
        for stored_edge in self._edges:
            if edge.a == stored_edge.a and edge.b == stored_edge.b:
                return
            if edge.a == stored_edge.b and edge.b == stored_edge.a:
                return
        self._edges.add(edge)

    def search_week_matchup(self) -> MatchmakingEdge | None:
        self._is_searching = True
        while True:
            best_edge: 'MatchmakingEdge | None' = None
            best_edge_node: 'MatchMakingTeam | None' = None
            if self.has_found_best_edge():
                self._is_searching = False
                return self._best_edge
            for edge in self._edges:
                node = self._get_output_node(edge)
                if node.has_found_best_edge():
                    continue
                if (best_edge is None
                        or (edge.distance_points <= best_edge.distance_points
                            and edge.past_matches_points <= best_edge.past_matches_points)):
                    best_edge = edge
                    best_edge_node = node
            if best_edge_node is None:
                return None
            if best_edge_node.is_searching():
                self._is_searching = False
                self._best_edge = best_edge
                best_edge_node.set_best_edge(best_edge)
                return self._best_edge
            else:
                best_edge_node.search_week_matchup()

    def _get_output_node(self, edge: 'MatchmakingEdge') -> 'MatchmakingTeam':
        if edge.a.id == self.id:
            return edge.b
        return edge.a

    def set_best_edge(self, edge: 'MatchmakingEdge'):
        self._best_edge = edge

    def reset(self):
        self._best_edge = None
        self._is_searching = False
