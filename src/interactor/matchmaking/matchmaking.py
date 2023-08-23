"""
author: oluiscabral
date: 8/23/23
"""
from abc import ABC
from dataclasses import dataclass
from typing import Set, Iterable

from geopy.distance import geodesic

from entity.division import Division
from entity.team import Team


class OutputGetMatchups:
    pass


class Matchmaking(ABC):

    def create_matchups(self, teams: Set[Team]):
        pass


class MatchMakingDatabase(ABC):
    pass


class MatchMakingTeamEdge:

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
                if self._a.id == contestant.id:
                    continue
                if self._b.id == contestant.id:
                    points += 1
        return points


class MatchmakingTeam:

    # noinspection PyTypeChecker
    def __init__(self, team: Team):
        self._team: Team = team
        self._is_searching: bool = False
        self._matchup: 'MatchMakingTeamEdge' = None
        self._edges: Set['MatchMakingTeamEdge'] = set()

    @property
    def id(self):
        return self._team.id

    @property
    def city(self):
        return self._team.city

    @property
    def home_court(self):
        return self._team.home_court

    @property
    def division(self):
        return self._team.division

    @property
    def players(self):
        return self._team.players

    @property
    def past_matches(self):
        return self._team.past_matches

    @property
    def availability(self):
        return self._team.availability

    @property
    def matchup(self):
        return self._matchup

    def is_searching(self) -> bool:
        return self._is_searching

    def has_found_matchup(self) -> bool:
        return self._matchup is not None

    def add_edge(self, edge: 'MatchMakingTeamEdge'):
        for stored_edge in self._edges:
            if edge.a == stored_edge.a and edge.b == stored_edge.b:
                return
            if edge.a == stored_edge.b and edge.b == stored_edge.a:
                return
        self._edges.add(edge)

    def search_week_matchup(self) -> MatchMakingTeamEdge | None:
        self._is_searching = True
        while True:
            best_edge: 'MatchMakingTeamEdge' = None
            best_edge_node: 'MatchMakingTeam' = None
            if self.has_found_matchup():
                self._is_searching = False
                return self._matchup
            for edge in self._edges:
                node = self._get_output_node(edge)
                if node.has_found_matchup():
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
                self._matchup = best_edge
                best_edge_node.set_matchup(best_edge)
                return self._matchup
            else:
                best_edge_node.search_week_matchup()

    def _get_output_node(self, edge: 'MatchMakingTeamEdge') -> 'MatchmakingTeam':
        if edge.a.id == self.id:
            return edge.b
        return edge.a

    def set_matchup(self, matchup: 'MatchMakingTeamEdge'):
        self._matchup = matchup

    def reset_matchup(self):
        self._matchup = None
        self._is_searching = False


@dataclass(frozen=True)
class MatchMakingResult:
    byes: int
    distance_points: float
    past_matches_points: int
    matchups: Set[MatchMakingTeamEdge]

    def is_better_than(self, other: 'MatchMakingResult'):
        if self.byes < other.byes:
            return True
        return self.distance_points < other.distance_points and self.past_matches_points < self.past_matches_points


class MatchmakingImpl(Matchmaking):
    WEEK_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    def __init__(self):
        # noinspection PyTypeChecker
        self._beginner_teams: Set[MatchmakingTeam] = set()
        self._intermediate_teams: Set[MatchmakingTeam] = set()
        self._advanced_teams: Set[MatchmakingTeam] = set()
        self._db: MatchMakingDatabase = None

    def set_database(self, db: MatchMakingDatabase):
        self._db = db

    def create_matchups(self, teams: Iterable[Team]):
        output = list()
        self._init_matchmaking(teams)
        beginner_output = self._get_best_matchups(self._beginner_teams)
        intermediate_output = self._get_best_matchups(self._intermediate_teams)
        advanced_output = self._get_best_matchups(self._advanced_teams)
        output.extend(beginner_output)
        output.extend(intermediate_output)
        output.extend(advanced_output)
        return output

    def _init_matchmaking(self, teams: Iterable[Team]):
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

    def _init_division_edges(self, teams: Set[MatchmakingTeam]):
        for team in teams:
            self._init_edges(team, teams)

    @staticmethod
    def _init_edges(team_a: MatchmakingTeam, teams: Set[MatchmakingTeam]):
        for team_b in teams:
            if team_a.id == team_b.id:
                continue
            if (team_a.division == team_b.division
                    and team_a.availability.meets(team_b.availability)):
                edge = MatchMakingTeamEdge(team_a, team_b)
                team_a.add_edge(edge)
                team_b.add_edge(edge)

    @staticmethod
    def _get_matchmaking_result(teams: Set[MatchmakingTeam]):
        byes = 0
        matchups = set()
        distance_points = 0
        past_matches_points = 0
        for team in teams:
            if not team.has_found_matchup():
                byes += 1
                continue
            matchup = team.matchup
            matchups.add(matchup)
            distance_points += matchup.distance_points
            past_matches_points += matchup.past_matches_points
        return MatchMakingResult(byes, distance_points, past_matches_points, matchups)

    def _create_output(self, best_result: MatchMakingResult):
        output = list()
        for matchup in best_result.matchups:
            matchup_output = dict()
            matchup_output['team1'] = matchup.a.id
            matchup_output['team2'] = matchup.b.id
            matchup_output['Reccomended Day/Times'] = self._get_daytimes_output(matchup)
            output.append(matchup_output)
        return output

    def _get_daytimes_output(self, matchup: MatchMakingTeamEdge):
        output = list()
        equal_schedules = matchup.a.availability.get_equal_schedules(matchup.b.availability)
        for equal_schedule in equal_schedules:
            weekday = equal_schedule.date.weekday()
            weekday_name = self.WEEK_DAYS[weekday]
            period_name = equal_schedule.period.name.capitalize()
            output.append(f'{weekday_name} {period_name}')
        return output

    def _get_best_matchups(self, teams: Set[MatchmakingTeam]):
        best_result: MatchMakingResult = None
        for team in teams:
            self._reset_matchups(teams)
            team.search_week_matchup()
            result = self._get_matchmaking_result(teams)
            if best_result is None or result.is_better_than(best_result):
                best_result = result
        return self._create_output(best_result)

    @staticmethod
    def _reset_matchups(teams: Set[MatchmakingTeam]):
        for team in teams:
            team.reset_matchup()

    def save_result(self, result: dict):
        pass
