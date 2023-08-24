"""
author: oluiscabral
date: 8/23/23
"""
import datetime
from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class Availability:
    morning: Set[datetime.date]
    afternoon: Set[datetime.date]
    evening: Set[datetime.date]

    def __hash__(self):
        value = 0
        for date in self.morning.union(self.afternoon).union(self.evening):
            value += hash(date)
        return value

    def meets(self, other: 'Availability') -> bool:
        return (self._meets(self.morning, other.morning)
                or self._meets(self.afternoon, other.afternoon)
                or self._meets(self.evening, other.evening))

    @staticmethod
    def _meets(a, b):
        intersection = a.intersection(b)
        return len(intersection) > 0

    def get_intersection(self, other: 'Availability') -> 'Availability':
        morning_intersection = self.morning.intersection(other.morning)
        afternoon_intersection = self.afternoon.intersection(other.afternoon)
        evening_intersection = self.evening.intersection(other.evening)
        return Availability(morning_intersection, afternoon_intersection, evening_intersection)
