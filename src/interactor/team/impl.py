"""
author: oluiscabral
date: 8/23/23
"""
import datetime
import uuid
from typing import Set, List

from entity.availability import Availability
from entity.city import City
from entity.court import Court
from entity.division import Division
from entity.match import Match
from entity.matchup import Matchup
from entity.player import Player
from entity.team import Team
from interactor.team import TeamInteractor, TeamDatabase


class TeamInteractorImpl(TeamInteractor):

    # noinspection PyTypeChecker
    def __init__(self):
        self._db: TeamDatabase = None

    def set_db(self, db: TeamDatabase):
        self._db = db

    def create_teams(self, input_data) -> Set[Team]:
        teams = set()
        for data in input_data:
            team_id = data['team_id']
            city = City(data['city'])
            home_court = Court(data['Home Court'])
            division = TeamInteractorImpl.get_division(data)
            past_matches = self._db.get_past_matches(team_id)
            availability = TeamInteractorImpl._create_availability(data)
            player_1 = Player(data['player1_id'], data['player1_coords'])
            player_2 = Player(data['player2_id'], data['player2_coords'])
            team = Team(team_id, city, home_court, division, [player_1, player_2], past_matches, availability)
            teams.add(team)
        return teams

    @staticmethod
    def _create_availability(data):
        morning_dates = TeamInteractorImpl._create_dates(data['morning'])
        afternoon_dates = TeamInteractorImpl._create_dates(data['afternoon'])
        evening_dates = TeamInteractorImpl._create_dates(data['evening'])
        return Availability(morning_dates, afternoon_dates, evening_dates)

    @staticmethod
    def _create_dates(date_texts: Set[str]):
        today = datetime.date.today()
        dates = set()
        for date_text in date_texts:
            date_values_text = date_text.split(' ')[1]
            date_value_texts = date_values_text.split('/')
            day = int(date_value_texts[1])
            month = int(date_value_texts[0])
            created_date = datetime.date(month=month, day=day, year=today.year)
            dates.add(created_date)
        return dates

    @staticmethod
    def get_division(data):
        data_division = data['division'].lower()
        if Division.BEGINNER.name.lower() == data_division:
            return Division.BEGINNER
        if Division.INTERMEDIATE.name.lower() == data_division:
            return Division.INTERMEDIATE
        if Division.ADVANCED.name.lower() == data_division:
            return Division.ADVANCED
        return None

    def save_matchups(self, matchups: List[Matchup]):
        matches = list()
        for matchup in matchups:
            match_id = str(uuid.uuid4())
            team_a, team_b = matchup.contestants
            match = Match(match_id, matchup.availability, (team_a.id, team_b.id))
            matches.append(match)
        self._db.save_matches(matches)
