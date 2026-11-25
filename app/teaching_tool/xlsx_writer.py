"""The local .xlsx attendance sheet (component C12, offline implementation).

One row per student, one column per lesson. A sheet with real names is kept only as a
file on the lecturer's computer (FR-6.3, FR-6.4, D49).
"""
from pathlib import Path

import openpyxl

from .sheet_writer import SheetWriter

FIXED = ["First name", "Last name", "Email", "Group"]


class XlsxSheetWriter(SheetWriter):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def write_attendance(self, lesson_name, rows):
        """Add (or replace) this lesson's column. Students are matched by email."""
        if self.path.exists():
            wb = openpyxl.load_workbook(self.path)
            ws = wb.active
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Attendance"
            ws.append(FIXED)

        header = [c.value for c in ws[1]]
        if lesson_name in header:
            col = header.index(lesson_name) + 1
        else:
            col = len(header) + 1
            ws.cell(row=1, column=col, value=lesson_name)

        row_of = {str(ws.cell(row=r, column=3).value or "").lower(): r for r in range(2, ws.max_row + 1)}
        for data in rows:
            r = row_of.get(data["email"].lower())
            if r is None:
                r = ws.max_row + 1
                for c, key in enumerate(("first_name", "last_name", "email", "group"), start=1):
                    ws.cell(row=r, column=c, value=data[key])
                row_of[data["email"].lower()] = r
            ws.cell(row=r, column=col, value=data["status"])
        wb.save(self.path)
        return str(self.path)

    def write_lesson_summary(self, lesson_name, checked_in, head_count):
        """A "Lessons" tab: one row per lesson with its numbers (replaced if written again)."""
        wb = openpyxl.load_workbook(self.path)
        if "Lessons" not in wb.sheetnames:
            wb.create_sheet("Lessons").append(["Lesson", "Checked in", "Head count"])
        ws = wb["Lessons"]
        for r in range(2, ws.max_row + 1):
            if ws.cell(row=r, column=1).value == lesson_name:
                ws.delete_rows(r)
                break
        ws.append([lesson_name, checked_in, head_count])
        wb.save(self.path)

    def write_comments(self, lesson_name, rows):
        """The "Comments" tab. This lesson's old rows are replaced, so writing again does not repeat them."""
        wb = openpyxl.load_workbook(self.path)
        if "Comments" not in wb.sheetnames:
            wb.create_sheet("Comments").append(["Lesson", "Time", "Text"])
        ws = wb["Comments"]
        for r in range(ws.max_row, 1, -1):
            if ws.cell(row=r, column=1).value == lesson_name:
                ws.delete_rows(r)
        for row in rows:
            ws.append([lesson_name, row["time"], row["text"]])
        wb.save(self.path)
