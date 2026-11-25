"""Write an invented course list of 10 students, for development and tests.

It has the same sheet layout and headers as the real participant list, so the same
code loads both. All names and emails are invented (domain demo.test).

Usage: python tests/data/make_invented_course.py
"""
import pathlib

import openpyxl

HEADERS = ["שם פרטי", "שם משפחה", 'דוא"ל', "קבוצות"]
STUDENTS = [
    ("Dana", "Levi", "student01@demo.test", "1"),
    ("Omer", "Cohen", "student02@demo.test", "1"),
    ("Noa", "Mizrahi", "student03@demo.test", "1"),
    ("Yossi", "Peretz", "student04@demo.test", "2"),
    ("Maya", "Biton", "student05@demo.test", "2"),
    ("Amit", "Friedman", "student06@demo.test", "2"),
    ("Shira", "Katz", "student07@demo.test", "3"),
    ("Eitan", "Azulay", "student08@demo.test", "3"),
    ("Tamar", "Shapiro", "student09@demo.test", "3"),
    ("Ariel", "Dahan", "student10@demo.test", ""),
]


def main():
    out = pathlib.Path(__file__).with_name("invented_course.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "participants"
    ws.append(HEADERS)
    for row in STUDENTS:
        ws.append(list(row))
    wb.save(out)
    print(f"written: {out} ({len(STUDENTS)} invented students)")


if __name__ == "__main__":
    main()
