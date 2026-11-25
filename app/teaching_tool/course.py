"""The course list (component C7): students loaded from the participant .xlsx file.

The real list stays on the lecturer's computer and is never uploaded (FR-1.4).
"""
from dataclasses import dataclass
from pathlib import Path

import openpyxl

# Column headers of the participant list downloaded from the course site.
FIRST_NAME, LAST_NAME, EMAIL, GROUP = "שם פרטי", "שם משפחה", 'דוא"ל', "קבוצות"


@dataclass(frozen=True)
class Student:
    first_name: str
    last_name: str
    email: str
    group: str


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


class Course:
    """The students of one course, found by email."""

    def __init__(self, students: list[Student], warnings: list[str] | None = None):
        self.students = students
        self.warnings = warnings or []
        self._by_email = {normalize_email(s.email): s for s in students if s.email}

    @classmethod
    def load_xlsx(cls, path: str | Path) -> "Course":
        """Read the participant list. Rows with no email are kept, with a warning (UC-1).

        The same email twice keeps the first row, with a warning.
        """
        wb = openpyxl.load_workbook(path, read_only=True)
        rows = wb.active.iter_rows(values_only=True)
        header = [str(h).strip() if h is not None else "" for h in next(rows)]
        missing = [h for h in (FIRST_NAME, LAST_NAME, EMAIL, GROUP) if h not in header]
        if missing:
            raise ValueError(f"Not a participant list: missing columns {missing}")
        col = {name: header.index(name) for name in (FIRST_NAME, LAST_NAME, EMAIL, GROUP)}

        students, warnings, seen = [], [], set()
        for line, row in enumerate(rows, start=2):
            row = list(row) + [None] * (len(header) - len(row))  # short rows: empty last cells
            if not any(row):
                continue
            cell = lambda name: str(row[col[name]]).strip() if row[col[name]] is not None else ""
            student = Student(cell(FIRST_NAME), cell(LAST_NAME), cell(EMAIL), cell(GROUP))
            email = normalize_email(student.email)
            if not email:
                warnings.append(f"Row {line}: no email ({student.first_name} {student.last_name})")
            elif email in seen:
                warnings.append(f"Row {line}: the email {student.email} appears twice; kept the first row")
                continue
            seen.add(email)
            students.append(student)
        wb.close()
        return cls(students, warnings)

    def find(self, email: str) -> Student | None:
        return self._by_email.get(normalize_email(email))
