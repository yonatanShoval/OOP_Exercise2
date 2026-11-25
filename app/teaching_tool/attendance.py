"""Attendance (component C11): compare check-ins with the head count, and build the statuses.

The system raises mismatches and the lecturer decides. It never marks anyone by itself
(FR-4.1 – FR-4.3, FR-6.1).
"""
from dataclasses import dataclass

from .course import Course, normalize_email


@dataclass(frozen=True)
class Mismatch:
    kind: str  # "count_gap" or "unknown_email" (the challenge adds more kinds in part 3)
    details: str


class AttendanceService:
    def __init__(self, course: Course):
        self.course = course
        self.photo_counts: list[int] = []
        self.decisions: dict[str, bool] = {}  # email -> present, decided by the lecturer

    def add_photo_count(self, count: int) -> None:
        self.photo_counts.append(count)

    def lesson_count(self) -> int | None:
        """The highest count of the lesson's photos, not the sum (FR-3.4)."""
        return max(self.photo_counts) if self.photo_counts else None

    def compare(self, accepted: set, unknown_emails: set) -> list[Mismatch]:
        mismatches = []
        count = self.lesson_count()
        if count is not None and count != len(accepted):
            mismatches.append(Mismatch("count_gap", f"{len(accepted)} checked in, {count} counted"))
        for email in sorted(unknown_emails):
            mismatches.append(Mismatch("unknown_email", f"{email} is not on the course list"))
        return mismatches

    def decide(self, email: str, present: bool) -> None:
        self.decisions[normalize_email(email)] = present

    def rows(self, accepted: set) -> list[dict]:
        """One row per student on the course list. The lecturer's decision wins over the check-in."""
        rows = []
        for s in self.course.students:
            email = normalize_email(s.email)
            present = self.decisions.get(email, email in accepted)
            rows.append({"first_name": s.first_name, "last_name": s.last_name, "email": s.email,
                         "group": s.group, "status": "present" if present else "absent"})
        return rows
