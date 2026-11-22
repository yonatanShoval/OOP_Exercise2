"""Spreadsheet tools test (online): write an attendance table to a Google Sheet.

Only INVENTED data is written (Student 01 ...). The real participant list never goes to the cloud.
Auth: the service account key in secrets/ (fixed path, never in git). The sheet must be shared
with the service account's email as an editor.
Usage: python write_google_sheet.py <Google Sheet URL>
"""
import sys
import time
from pathlib import Path

import gspread

KEY_PATH = Path(__file__).resolve().parents[3] / "secrets" / "serviceAccountKey.json"
LESSON_DATE = "2026-11-19"

if len(sys.argv) != 2:
    raise SystemExit("Usage: python write_google_sheet.py <Google Sheet URL>")
if not KEY_PATH.exists():
    raise SystemExit(f"Key file not found: {KEY_PATH}")

rows = [["Student", "Group", f"{LESSON_DATE} (TEST DATA)"]]
rows += [[f"Student {n:02d}", "A" if n <= 5 else "B", "present" if n % 4 else "absent"]
         for n in range(1, 11)]

start = time.time()
client = gspread.service_account(filename=str(KEY_PATH))
worksheet = client.open_by_url(sys.argv[1]).sheet1
worksheet.clear()
worksheet.update(rows, "A1")
written = time.time() - start

read_back = worksheet.get_all_values()  # read the sheet again to confirm the data arrived
print(f"Wrote {len(rows) - 1} invented students in {written:.2f} s")
print(f"Read back {len(read_back) - 1} rows; match: {read_back == rows}")
