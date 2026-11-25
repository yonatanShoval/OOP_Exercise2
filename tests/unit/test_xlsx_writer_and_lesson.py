"""XlsxSheetWriter writes one column per lesson; Lesson.close deletes personal data (FR-1.5, FR-6.2)."""
import openpyxl

from teaching_tool.database import FakeDatabase
from teaching_tool.lesson import Lesson
from teaching_tool.xlsx_writer import XlsxSheetWriter


def row(email, status):
    return {"first_name": "F", "last_name": "L", "email": email, "group": "1", "status": status}


def test_two_lessons_give_two_columns_and_read_back(tmp_path):
    writer = XlsxSheetWriter(tmp_path / "attendance.xlsx")
    writer.write_attendance("2026-11-26", [row("a@demo.test", "present"), row("b@demo.test", "absent")])
    writer.write_attendance("2026-11-30", [row("a@demo.test", "absent"), row("b@demo.test", "present")])
    ws = openpyxl.load_workbook(tmp_path / "attendance.xlsx").active
    assert [c.value for c in ws[1]] == ["First name", "Last name", "Email", "Group", "2026-11-26", "2026-11-30"]
    assert [c.value for c in ws[2]][4:] == ["present", "absent"]
    assert ws.max_row == 3


def test_closing_a_lesson_deletes_codes_and_check_ins():
    db = FakeDatabase()
    lesson = Lesson.open(db)
    db.add(lesson.path("codes"), {"value": "K7Q2"})
    db.add(lesson.path("checkins"), {"email": "a@demo.test", "code": "K7Q2"})
    db.add(lesson.path("checkins"), {"email": "b@demo.test", "code": "K7Q2"})
    assert lesson.close() == 3
    assert db.list(lesson.path("checkins")) == []
    assert db.get(lesson.path())["closed"] is True
