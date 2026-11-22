"""Spreadsheet tools test (offline): build an attendance sheet (.xlsx) from the real participant list.

Reads course-materials/courseid_130158_participants.xlsx and writes
course-materials/attendance-output/attendance-test.xlsx. Both stay out of git.
The email column is NOT copied. The attendance marks are invented test data.
"""
import random
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

REPO_ROOT = Path(__file__).resolve().parents[3]
PARTICIPANTS = REPO_ROOT / "course-materials" / "courseid_130158_participants.xlsx"
OUT_FILE = REPO_ROOT / "course-materials" / "attendance-output" / "attendance-test.xlsx"
LESSON_DATE = "2026-11-19"

# Column names in the lecturer's file (Hebrew): first name, last name, groups.
FIRST, LAST, GROUP = "שם פרטי", "שם משפחה", "קבוצות"

source = load_workbook(PARTICIPANTS, read_only=True).active
rows = list(source.iter_rows(values_only=True))
header = list(rows[0])
i_first, i_last, i_group = header.index(FIRST), header.index(LAST), header.index(GROUP)

rng = random.Random(42)  # fixed seed: the invented marks are the same in every run
book = Workbook()
sheet = book.active
sheet.title = "Attendance"
sheet.append(["First name", "Last name", "Group", f"{LESSON_DATE} (TEST DATA)"])
for cell in sheet[1]:
    cell.font = Font(bold=True)
present = 0
for row in rows[1:]:
    row = list(row) + [None] * (len(header) - len(row))  # some rows end early when the last cells are empty
    status = "present" if rng.random() < 0.8 else "absent"
    present += status == "present"
    sheet.append([row[i_first], row[i_last], row[i_group], status])
sheet.freeze_panes = "A2"
for column, width in zip("ABCD", (18, 18, 20, 26)):
    sheet.column_dimensions[column].width = width

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
book.save(OUT_FILE)
print(f"Wrote {len(rows) - 1} students ({present} marked present, test data) to {OUT_FILE}")
