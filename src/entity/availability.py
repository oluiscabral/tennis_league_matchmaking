"""
author: oluiscabral
date: 8/23/23
"""
import datetime
from dataclasses import dataclass
from typing import Set, List

from entity.schedule import Schedule, Period


@dataclass(frozen=True)
class Availability:
    morning: Set[datetime.date]
    afternoon: Set[datetime.date]
    evening: Set[datetime.date]

    def __hash__(self):
        return hash(self.morning) + hash(self.afternoon) + hash(self.evening)

    def meets(self, other: 'Availability') -> bool:
        return (self._meets(self.morning, other.morning)
                or self._meets(self.afternoon, other.afternoon)
                or self._meets(self.evening, other.evening))

    def _meets(self, a, b):
        intersection = a.intersection(b)
        return len(intersection) > 0

    def get_equal_schedules(self, other: 'Availability') -> List[Schedule]:
        equal_schedules = list()
        morning_intersection = self.morning.intersection(other.morning)
        afternoon_intersection = self.afternoon.intersection(other.afternoon)
        evening_intersection = self.evening.intersection(other.evening)
        morning_schedules = self._create_schedules(morning_intersection, Period.MORNING)
        afternoon_schedules = self._create_schedules(afternoon_intersection, Period.AFTERNOON)
        evening_schedules = self._create_schedules(evening_intersection, Period.EVENING)
        equal_schedules.extend(morning_schedules)
        equal_schedules.extend(afternoon_schedules)
        equal_schedules.extend(evening_schedules)
        return sorted(equal_schedules, key=self._schedule_sort)

    def _create_schedules(self, dates: Set[datetime.date], period: Period):
        schedules = set()
        for date in dates:
            schedule = Schedule(0, date, period)
            schedules.add(schedule)
        return schedules

    @staticmethod
    def _schedule_sort(schedule: Schedule):
        return schedule.date, schedule.period.value
