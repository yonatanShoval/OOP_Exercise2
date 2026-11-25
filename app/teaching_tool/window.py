"""The lecturer's window (component C6), in tkinter.

The window holds no logic: it calls the other classes, and shows their results.
Firestore and the head counter work in background threads, so their results go
through a queue, and the window reads the queue every 200 ms.
"""
import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import qrcode
from PIL import ImageTk

from .attendance import AttendanceService
from .checkin import CheckInService, ROTATE_SECONDS
from .course import Course
from .headcount import HeadCounter
from .lesson import Lesson
from .xlsx_writer import XlsxSheetWriter

CHECKIN_URL = "https://oop-exercise2.web.app/checkin.html"
REPO_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_DIR = REPO_ROOT / "course-materials"  # blocked by .gitignore
SHEET_PATH = PRIVATE_DIR / "attendance" / "attendance.xlsx"
FONT = ("Segoe UI", 12)


class LecturerWindow:
    def __init__(self, db, counter: HeadCounter | None = None):
        self.db = db
        self.counter = counter or HeadCounter()
        self.events = queue.Queue()
        self.course = self.lesson = self.checkins = self.attendance = None
        self.checkin_on = False
        self.sheet_written = False

        self.root = tk.Tk()
        self.root.title("Teaching Tool: lecturer")
        self.root.configure(bg="white")
        buttons = tk.Frame(self.root, bg="white")
        buttons.pack(side="left", fill="y", padx=10, pady=10)
        self.btn = {}
        for key, text, command in [
            ("load", "1. Load course list", self.load_course),
            ("open", "2. Open lesson", self.open_lesson),
            ("checkin", "3. Start check-in", self.toggle_checkin),
            ("photos", "4. Add class photos", self.add_photos),
            ("compare", "5. Compare", self.compare),
            ("sheet", "6. Write sheet (.xlsx)", self.write_sheet),
            ("close", "7. Close lesson", self.close_lesson),
        ]:
            self.btn[key] = tk.Button(buttons, text=text, command=command, font=FONT, width=24, anchor="w")
            self.btn[key].pack(pady=3)

        right = tk.Frame(self.root, bg="white")
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.counts = tk.Label(right, text="", font=("Segoe UI", 14, "bold"), bg="white", anchor="w", justify="left")
        self.counts.pack(fill="x")
        self.log_box = tk.Text(right, width=70, height=22, font=("Consolas", 11))
        self.log_box.pack(fill="both", expand=True)

        self.projector = None
        self.qr_image = None
        self.update_buttons()
        self.root.after(200, self.poll)

    # ---------- helpers ----------
    def log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def update_buttons(self):
        has_lesson = self.lesson is not None
        self.btn["open"]["state"] = "normal" if self.course and not has_lesson else "disabled"
        for key in ("checkin", "photos", "compare", "sheet", "close"):
            self.btn[key]["state"] = "normal" if has_lesson else "disabled"
        self.btn["checkin"]["text"] = "3. Stop check-in" if self.checkin_on else "3. Start check-in"
        self.show_counts()

    def show_counts(self):
        if not self.checkins:
            self.counts["text"] = "No lesson open."
            return
        c = self.checkins.counts
        count = self.attendance.lesson_count()
        self.counts["text"] = (f"Accepted: {len(c.accepted)}    Unknown emails: {len(c.unknown_emails)}    "
                               f"Rejected codes: {c.rejected}\nHead count: {count if count is not None else '—'}")

    def poll(self):
        """Read results from background threads (Firestore listener, head counter)."""
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "checkin":
                    self.log(f"check-in {value.status}: {value.email}")
                elif kind == "photo":
                    self.attendance.add_photo_count(value.count())
                    self.log(f"{Path(value.path).name}: {value.count()} people")
                elif kind == "error":
                    self.log(f"error: {value}")
                self.show_counts()
        except queue.Empty:
            pass
        self.root.after(200, self.poll)

    # ---------- actions ----------
    def load_course(self):
        path = filedialog.askopenfilename(title="Course participant list", initialdir=PRIVATE_DIR,
                                          filetypes=[("Excel", "*.xlsx")])
        if not path:
            return
        try:
            self.course = Course.load_xlsx(path)
        except ValueError as e:
            messagebox.showerror("Course list", str(e))
            return
        self.log(f"Loaded {len(self.course.students)} students from {Path(path).name}")
        for w in self.course.warnings:
            self.log("  warning: " + w)
        self.update_buttons()

    def open_lesson(self):
        self.lesson = Lesson.open(self.db)
        self.checkins = CheckInService(self.db, self.course, self.lesson)
        self.attendance = AttendanceService(self.course)
        self.checkins.listen(lambda result: self.events.put(("checkin", result)))
        self.log(f"Lesson opened: {self.lesson.id}")
        self.update_buttons()

    def toggle_checkin(self):
        self.checkin_on = not self.checkin_on
        self.lesson.set_checkin_open(self.checkin_on)
        if self.checkin_on:
            self.projector = tk.Toplevel(self.root, bg="white")
            self.projector.title("Check-in: scan with your phone")
            self.qr_label = tk.Label(self.projector, bg="white")
            self.qr_label.pack(padx=20, pady=20)
            tk.Label(self.projector, text="Scan to check in", font=("Segoe UI", 28), bg="white").pack(pady=(0, 20))
            self.projector.protocol("WM_DELETE_WINDOW", self.toggle_checkin)
            self.rotate()
            self.log("Check-in started")
        else:
            if self.projector:
                self.projector.destroy()
                self.projector = None
            self.log("Check-in stopped")
        self.update_buttons()

    def rotate(self):
        """Show a new code every 10 s. Its validity is checked with server times, not with this timer."""
        if not self.checkin_on:
            return
        code = self.checkins.next_code()
        url = f"{CHECKIN_URL}?l={self.lesson.id}&t={code}"
        self.qr_image = ImageTk.PhotoImage(qrcode.make(url, box_size=14, border=4).get_image())
        self.qr_label.configure(image=self.qr_image)
        self.root.after(ROTATE_SECONDS * 1000, self.rotate)

    def add_photos(self):
        paths = filedialog.askopenfilenames(title="Class photos", initialdir=PRIVATE_DIR,
                                            filetypes=[("Photos", "*.jpg *.jpeg *.png")])
        if not paths:
            return
        self.log(f"Counting {len(paths)} photo(s) on this computer, about 5 s each…")

        def work():
            for p in paths:
                try:
                    self.events.put(("photo", self.counter.count(p)))
                except Exception as e:  # shown in the window, not lost in the thread
                    self.events.put(("error", e))
        threading.Thread(target=work, daemon=True).start()

    def compare(self):
        c = self.checkins.counts
        mismatches = self.attendance.compare(c.accepted, c.unknown_emails)
        if not mismatches:
            self.log("Compare: no mismatch.")
        for m in mismatches:
            self.log(f"MISMATCH ({m.kind}): {m.details}")

    def write_sheet(self):
        rows = self.attendance.rows(self.checkins.counts.accepted)
        try:
            where = XlsxSheetWriter(SHEET_PATH).write_attendance(self.lesson.id, rows)
        except PermissionError:
            self.log("The sheet is open in Excel. Close it, then click Write sheet again.")
            return
        present = sum(r["status"] == "present" for r in rows)
        self.sheet_written = True
        self.log(f"Sheet written: {where} ({present} present of {len(rows)})")
        try:
            os.startfile(where)  # opens in Excel, so the sheet appears at once in the demo (Windows)
        except OSError as e:
            self.log(f"Could not open the sheet automatically: {e}")

    def close_lesson(self):
        if not self.sheet_written and not messagebox.askyesno(
                "Close lesson", "The sheet was not written yet. Close anyway?"):
            return
        if self.checkin_on:
            self.toggle_checkin()
        deleted = self.lesson.close()
        self.log(f"Lesson closed. Deleted {deleted} records (codes and check-ins) from the cloud.")
        self.lesson = self.checkins = self.attendance = None
        self.sheet_written = False
        self.update_buttons()

    def run(self):
        self.root.mainloop()
