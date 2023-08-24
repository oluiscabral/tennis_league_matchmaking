"""
author: oluiscabral
date: 8/23/23
"""
import datetime
import os
import sqlite3
from typing import List

from entity.availability import Availability
from entity.match import Match
from interactor.team import TeamDatabase


class TeamDatabaseImpl(TeamDatabase):

    def __init__(self):
        self._db_file_path = self._get_db_file_path()

    @staticmethod
    def _get_db_file_path() -> str:
        module_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(module_path, 'team.db')

    def get_past_matches(self, team_id: str) -> List[Match]:
        past_matches = list()
        conn = sqlite3.connect(self._db_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, team_a, team_b FROM match WHERE team_a = ? OR team_b = ?", (team_id, team_id))
        for match_row in cursor.fetchall():
            morning_dates = set()
            afternoon_dates = set()
            evening_dates = set()
            match_id, team_a, team_b = match_row
            cursor.execute("SELECT date, period FROM availability WHERE match = ?", (match_id,))
            for availability_row in cursor.fetchall():
                date_text, period = availability_row
                date = datetime.date.fromisoformat(date_text)
                if period == 0:
                    morning_dates.add(date)
                elif period == 1:
                    afternoon_dates.add(date)
                elif period == 2:
                    evening_dates.add(date)
            availability = Availability(morning_dates, afternoon_dates, evening_dates)
            match = Match(match_id, availability, (team_a, team_b))
            past_matches.append(match)
        cursor.close()
        conn.close()
        return past_matches

    def save_matches(self, matches: List[Match]):
        conn = sqlite3.connect(self._db_file_path)
        cursor = conn.cursor()
        for match in matches:
            match_id = match.id
            team_a, team_b = match.contestants
            cursor.execute("INSERT INTO match (id, team_a, team_b) VALUES (?, ?, ?)", (match_id, team_a, team_b))
        conn.commit()
        for match in matches:
            availability = match.availability
            insert_query = "INSERT INTO availability (date, match, period) VALUES (?, ?, ?)"
            for date in availability.morning:
                cursor.execute(insert_query, (date.isoformat(), match.id, 0))
            for date in availability.afternoon:
                cursor.execute(insert_query, (date.isoformat(), match.id, 1))
            for date in availability.evening:
                cursor.execute(insert_query, (date.isoformat(), match.id, 2))
        conn.commit()
        cursor.close()
        conn.close()
