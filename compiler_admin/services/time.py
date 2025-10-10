from dataclasses import dataclass, field
from datetime import date
from typing import MutableMapping
import math


@dataclass
class TimeSummary:
    """Represents a summary of time entries."""

    earliest_date: date | None = None
    latest_date: date | None = None
    total_rows: int = 0
    total_hours: float = 0.0
    hours_per_project: MutableMapping[str, float] = field(default_factory=dict)
    hours_per_user_project: MutableMapping[str, MutableMapping[str, float]] = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeSummary):
            return NotImplemented

        if self.earliest_date != other.earliest_date:
            return False
        if self.latest_date != other.latest_date:
            return False
        if self.total_rows != other.total_rows:
            return False
        if not math.isclose(self.total_hours, other.total_hours, rel_tol=1e-5):
            return False

        if self.hours_per_project.keys() != other.hours_per_project.keys():
            return False
        for key in self.hours_per_project:
            if not math.isclose(self.hours_per_project[key], other.hours_per_project[key], rel_tol=1e-5):
                return False

        if self.hours_per_user_project.keys() != other.hours_per_user_project.keys():
            return False
        for user, projects in self.hours_per_user_project.items():
            if user not in other.hours_per_user_project:
                return False
            if projects.keys() != other.hours_per_user_project[user].keys():
                return False
            for project, hours in projects.items():
                if not math.isclose(hours, other.hours_per_user_project[user][project], rel_tol=1e-5):
                    return False

        return True
