from pathlib import Path

import openpyxl
import pytest

from teaching_tool.course import Course, FIRST_NAME, LAST_NAME, EMAIL, GROUP

INVENTED = Path(__file__).resolve().parents[1] / "data" / "invented_course.xlsx"


def write_list(path, rows, header=(FIRST_NAME, LAST_NAME, EMAIL, GROUP)):
    wb = openpyxl.Workbook()
    wb.active.append(list(header))
    for row in rows:
        wb.active.append(list(row))
    wb.save(path)
    return path


def test_loads_the_invented_list_of_10():
    course = Course.load_xlsx(INVENTED)
    assert len(course.students) == 10
    assert course.warnings == []


def test_find_ignores_case_and_spaces():
    course = Course.load_xlsx(INVENTED)
    assert course.find("  Student03@DEMO.test ").first_name == "Noa"
    assert course.find("nobody@demo.test") is None


def test_empty_group_cell_is_kept():
    course = Course.load_xlsx(INVENTED)
    assert course.find("student10@demo.test").group == ""


def test_row_with_no_email_is_kept_with_a_warning(tmp_path):
    course = Course.load_xlsx(write_list(tmp_path / "l.xlsx", [("A", "B", "a@demo.test", "1"), ("C", "D", None, "1")]))
    assert len(course.students) == 2
    assert len(course.warnings) == 1 and "no email" in course.warnings[0]


def test_same_email_twice_keeps_one_row_with_a_warning(tmp_path):
    course = Course.load_xlsx(write_list(tmp_path / "l.xlsx", [("A", "B", "a@demo.test", "1"), ("A2", "B2", "A@demo.test", "2")]))
    assert len(course.students) == 1
    assert "appears twice" in course.warnings[0]


def test_a_file_that_is_not_a_participant_list_is_refused(tmp_path):
    with pytest.raises(ValueError):
        Course.load_xlsx(write_list(tmp_path / "l.xlsx", [], header=("Name", "Mail")))
