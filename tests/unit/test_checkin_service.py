"""CheckInService: the 60-second window, the course list, and duplicates (FR-2.6 – FR-2.8)."""
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from teaching_tool.checkin import CheckInService
from teaching_tool.course import Course
from teaching_tool.database import FakeDatabase
from teaching_tool.lesson import Lesson

INVENTED = Path(__file__).resolve().parents[1] / "data" / "invented_course.xlsx"
CODE_TIME = datetime(2026, 11, 26, 9, 5, 20, tzinfo=timezone.utc)


@pytest.fixture
def setup():
    now = {"t": CODE_TIME}
    db = FakeDatabase(clock=lambda: now["t"])
    lesson = Lesson.open(db)
    service = CheckInService(db, Course.load_xlsx(INVENTED), lesson)
    code = service.next_code()  # saved at 09:05:20, server time
    return service, code


def checkin(code, seconds_after, email="student01@demo.test"):
    return {"email": email, "code": code, "server_time": CODE_TIME + timedelta(seconds=seconds_after)}


@pytest.mark.parametrize("seconds, status", [
    (7, "accepted"),
    (30, "accepted"),   # the slowest first check-in seen in the phone test, with email typing
    (60, "accepted"),
    (61, "old_code"),
    (-1, "old_code"),
])
def test_code_age(setup, seconds, status):
    service, code = setup
    assert service.handle(checkin(code, seconds)).status == status


def test_code_is_stored_under_its_value_for_the_rules(setup):
    service, code = setup
    assert service.db.get(f"{service.lesson.path('codes')}/{code}")["server_time"] == CODE_TIME


def test_unknown_code_is_rejected(setup):
    service, _ = setup
    assert service.handle(checkin("not-a-code", 3)).status == "unknown_code"
    assert service.counts.rejected == 1


def test_email_not_on_the_list_becomes_a_mismatch(setup):
    service, code = setup
    result = service.handle(checkin(code, 3, email="x@typo.com"))
    assert result.status == "unknown_email"
    assert service.counts.unknown_emails == {"x@typo.com"}
    assert service.counts.accepted == set()


def test_the_same_student_twice_is_counted_once(setup):
    service, code = setup
    service.handle(checkin(code, 3))
    assert service.handle(checkin(code, 5, email=" Student01@demo.test")).status == "duplicate"
    assert len(service.counts.accepted) == 1


def test_check_ins_from_the_database_are_handled(setup):
    service, code = setup
    results = []
    service.listen(results.append)
    service.db.clock = lambda: CODE_TIME + timedelta(seconds=4)
    service.db.add(service.lesson.path("checkins"), {"email": "student02@demo.test", "code": code})
    assert [r.status for r in results] == ["accepted"]
