"""
author: oluiscabral
date: 8/23/23
"""
from typing import Set, Iterable, List

from entity.division import Division
from entity.matchup import Matchup
from entity.team import Team
from interactor.matchmaking import Matchmaking
from interactor.matchmaking.edge import MatchmakingEdge
from interactor.matchmaking.result import MatchMakingResult
from interactor.matchmaking.team import MatchmakingTeam


class MatchmakingImpl(Matchmaking):

    def __init__(self):
        # noinspection PyTypeChecker
        self._beginner_teams: Set[MatchmakingTeam] = set()
        self._intermediate_teams: Set[MatchmakingTeam] = set()
        self._advanced_teams: Set[MatchmakingTeam] = set()

    def get_best_matchups(self, teams: Iterable[Team]) -> List[Matchup]:
        matchups: List[Matchup] = list()
        self._prepare_matchmaking(teams)
        beginner_matchups = self._get_best_matchups(self._beginner_teams)
        intermediate_matchups = self._get_best_matchups(self._intermediate_teams)
        advanced_matchups = self._get_best_matchups(self._advanced_teams)
        matchups.extend(beginner_matchups)
        matchups.extend(intermediate_matchups)
        matchups.extend(advanced_matchups)
        return matchups

    def _prepare_matchmaking(self, teams: Iterable[Team]):
        for team in teams:
            parsed_team = MatchmakingTeam(team)
            if Division.BEGINNER == parsed_team.division:
                self._beginner_teams.add(parsed_team)
            elif Division.INTERMEDIATE == parsed_team.division:
                self._intermediate_teams.add(parsed_team)
            elif Division.ADVANCED == parsed_team.division:
                self._advanced_teams.add(parsed_team)
        self._init_division_edges(self._beginner_teams)
        self._init_division_edges(self._intermediate_teams)
        self._init_division_edges(self._advanced_teams)

    @staticmethod
    def _init_division_edges(teams: Set[MatchmakingTeam]):
        for team in teams:
            MatchmakingImpl._init_edges(team, teams)

    @staticmethod
    def _init_edges(team_a: MatchmakingTeam, teams: Set[MatchmakingTeam]):
        for team_b in teams:
            if team_a.id == team_b.id:
                continue
            if (team_a.division == team_b.division
                    and team_a.availability.meets(team_b.availability)):
                edge = MatchmakingEdge(team_a, team_b)
                team_a.add_edge(edge)
                team_b.add_edge(edge)

    @staticmethod
    def _get_best_matchups(teams: Set[MatchmakingTeam]) -> Set[Matchup]:
        best_result: MatchMakingResult | None = None
        for team in teams:
            MatchmakingImpl._reset(teams)
            team.search_week_matchup()
            result = MatchmakingImpl._get_matchmaking_result(teams)
            if best_result is None or result.is_better_than(best_result):
                best_result = result
        if best_result is None:
            return set()
        return best_result.matchups

    @staticmethod
    def _reset(teams: Set[MatchmakingTeam]):
        for team in teams:
            team.reset()

    @staticmethod
    def _get_matchmaking_result(teams: Set[MatchmakingTeam]) -> MatchMakingResult:
        byes = 0
        matchups = set()
        distance_points = 0
        past_matches_points = 0
        for team in teams:
            already_computed = False
            for matchup in matchups:
                if team in matchup.contestants:
                    already_computed = True
                    break
            if already_computed:
                continue
            if not team.has_found_best_edge():
                byes += 1
                continue
            matchup = MatchmakingImpl._create_matchup(team.best_edge)
            matchups.add(matchup)
            distance_points += team.best_edge.distance_points
            past_matches_points += team.best_edge.past_matches_points
        return MatchMakingResult(byes, matchups, distance_points, past_matches_points)

    @staticmethod
    def _create_matchup(best_edge: MatchmakingEdge) -> Matchup:
        availability = best_edge.a.availability.get_intersection(best_edge.b.availability)
        contestants = (best_edge.a, best_edge.b)
        return Matchup(availability, contestants)
