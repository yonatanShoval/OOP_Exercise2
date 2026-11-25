"""AttendanceService: the highest count, the mismatches, and the statuses (FR-3.4, FR-4.1, FR-6.1)."""
from pathlib import Path

from teaching_tool.attendance import AttendanceService
from teaching_tool.course import Course

INVENTED = Path(__file__).resolve().parents[1] / "data" / "invented_course.xlsx"


def service():
    return AttendanceService(Course.load_xlsx(INVENTED))


def emails(n):
    return {f"student{i:02d}@demo.test" for i in range(1, n + 1)}


def test_lesson_count_is_the_highest_not_the_sum():
    s = service()
    for c in (30, 30, 29):
        s.add_photo_count(c)
    assert s.lesson_count() == 30


def test_no_photos_means_no_count_and_no_gap():
    assert service().compare(emails(8), set()) == []


def test_a_gap_between_check_ins_and_count_is_a_mismatch():
    s = service()
    s.add_photo_count(6)
    [m] = s.compare(emails(8), set())
    assert m.kind == "count_gap" and m.details == "8 checked in, 6 counted"


def test_equal_numbers_give_no_mismatch():
    s = service()
    s.add_photo_count(8)
    assert s.compare(emails(8), set()) == []


def test_unknown_email_is_a_mismatch():
    s = service()
    [m] = s.compare(set(), {"x@typo.com"})
    assert m.kind == "unknown_email"


def test_rows_cover_every_student_and_the_decision_wins():
    s = service()
    s.decide("student02@demo.test", False)  # checked in, but the lecturer decided absent
    s.decide("student09@demo.test", True)   # did not check in, the lecturer decided present
    rows = {r["email"]: r["status"] for r in s.rows(emails(3))}
    assert len(rows) == 10
    assert rows["student01@demo.test"] == "present"
    assert rows["student02@demo.test"] == "absent"
    assert rows["student09@demo.test"] == "present"
    assert rows["student10@demo.test"] == "absent"
