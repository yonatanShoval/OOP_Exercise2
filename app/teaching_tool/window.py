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
from tkinter import filedialog, messagebox, simpledialog

import qrcode
from PIL import ImageTk

from .attendance import AttendanceService
from .checkin import CheckInService, ROTATE_SECONDS
from .comments import CommentService
from .polls import PollService, DEFAULT_DURATION_S
from .course import Course
from .headcount import HeadCounter
from .lesson import Lesson
from .xlsx_writer import XlsxSheetWriter

CHECKIN_URL = "https://oop-exercise2.web.app/checkin.html"
LESSON_URL = "https://oop-exercise2.web.app/lesson.html"
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
        self.comments = self.polls = None
        self.poll_window = None
        self.checkin_on = False
        self.sheet_written = False
        self.photo_paths = []  # this lesson's photos, deleted from the computer when the lesson closes
        self.counting = False  # True while photos are counted in the background

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
            ("poll", "Open a poll", self.open_poll),
            ("sheet", "6. Write sheet (.xlsx)", self.write_sheet),
            ("close", "7. Close lesson", self.close_lesson),
        ]:
            self.btn[key] = tk.Button(buttons, text=text, command=command, font=FONT, width=24, anchor="w")
            self.btn[key].pack(pady=3)

        tk.Label(buttons, text="Comments:", font=FONT, bg="white").pack(anchor="w", pady=(12, 0))
        self.comment_mode = tk.StringVar(value="during")
        self.mode_buttons = [
            tk.Radiobutton(buttons, text=text, value=value, variable=self.comment_mode, font=FONT, bg="white",
                           command=self.set_comment_mode)
            for value, text in [("during", "During the lesson"), ("after", "Only after the lesson"), ("closed", "Closed")]
        ]
        for rb in self.mode_buttons:
            rb.pack(anchor="w")

        right = tk.Frame(self.root, bg="white")
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.counts = tk.Label(right, text="", font=("Segoe UI", 14, "bold"), bg="white", anchor="w", justify="left")
        self.counts.pack(fill="x")
        self.status = tk.Label(right, text="", font=FONT, fg="#1a5fb4", bg="white", anchor="w")
        self.status.pack(fill="x")
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
        for key in ("checkin", "photos", "compare", "poll", "sheet", "close"):
            self.btn[key]["state"] = "normal" if has_lesson else "disabled"
        for rb in self.mode_buttons:
            rb["state"] = "normal" if has_lesson else "disabled"
        if self.counting:  # one count at a time; Close lesson waits too, so no photo is deleted mid-count
            self.btn["photos"]["state"] = self.btn["close"]["state"] = "disabled"
        self.btn["checkin"]["text"] = "3. Stop check-in" if self.checkin_on else "3. Start check-in"
        self.show_counts()

    def show_counts(self):
        if not self.checkins:
            self.counts["text"] = "No lesson open."
            return
        c = self.checkins.counts
        count = self.attendance.lesson_count()
        # Expired codes are rejected by the security rules, at the entrance, and never reach Python.
        # This count is only what the backup check in Python caught, so it is almost always 0.
        self.counts["text"] = (f"Accepted: {len(c.accepted)}    Unknown emails: {len(c.unknown_emails)}    "
                               f"Rejected by backup check: {c.rejected}\n"
                               f"Head count: {count if count is not None else '—'}")

    def poll(self):
        """Read results from background threads (Firestore listener, head counter)."""
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "checkin":
                    self.log(f"check-in {value.status}: {value.email}")
                elif kind == "photo":
                    self.attendance.add_photo_count(value.count())
                    self.photo_paths.append(value.path)
                    self.log(f"{Path(value.path).name}: {value.count()} people")
                elif kind == "progress":
                    self.status["text"] = value
                elif kind == "counting_done":
                    self.counting = False
                    self.status["text"] = f"Counting done: {value} photo(s)."
                    self.update_buttons()
                elif kind == "comment":
                    self.log(f"COMMENT: {value['text']}")
                elif kind == "answer":
                    self.show_poll(value)
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
        self.comments = CommentService(self.db, self.lesson)
        self.comments.listen(lambda c: self.events.put(("comment", c)))
        self.comment_mode.set("during")
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
                                            filetypes=[("Photos", "*.jpg *.jpeg *.png *.heic *.heif")])
        if not paths:
            return
        heic = [Path(p).name for p in paths if Path(p).suffix.lower() in (".heic", ".heif")]
        if heic:
            # The model's image reader cannot open HEIC, the iPhone's default photo format.
            messagebox.showwarning(
                "Photo format", "HEIC photos are not supported:\n" + "\n".join(heic) +
                "\n\nSend the photo as JPEG. For example, email it to yourself from the iPhone "
                "(Mail sends JPEG), or set the iPhone camera to Settings > Camera > Formats > "
                "Most Compatible.")
            paths = [p for p in paths if Path(p).suffix.lower() not in (".heic", ".heif")]
            if not paths:
                return
        self.log(f"Counting {len(paths)} photo(s) on this computer, about 20 s each…")
        self.counting = True
        self.update_buttons()

        def work():
            # Runs in a background thread, so the window does not freeze (about 20 s per phone photo).
            for i, p in enumerate(paths, start=1):
                self.events.put(("progress", f"Counting photo {i} of {len(paths)}…"))
                try:
                    self.events.put(("photo", self.counter.count(p)))
                except Exception as e:  # shown in the window, not lost in the thread
                    self.events.put(("error", e))
            self.events.put(("counting_done", len(paths)))
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
        writer = XlsxSheetWriter(SHEET_PATH)
        try:
            where = writer.write_attendance(self.lesson.id, rows)
            writer.write_lesson_summary(self.lesson.id, len(self.checkins.counts.accepted),
                                        self.attendance.lesson_count())
            writer.write_comments(self.lesson.id, self.comments.rows())
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
        self.delete_photos()
        if self.poll_window:
            self.poll_window.destroy()
            self.poll_window = None
        self.lesson = self.checkins = self.attendance = self.comments = self.polls = None
        self.sheet_written = False
        self.photo_paths = []
        self.update_buttons()

    def set_comment_mode(self):
        self.comments.set_mode(self.comment_mode.get())
        self.log(f"Comments: {self.comment_mode.get()}")

    def open_poll(self):
        question = simpledialog.askstring("Open a poll", "Question:", parent=self.root)
        if not question:
            return
        options = simpledialog.askstring("Open a poll", "Options, separated by ; (at least two):", parent=self.root)
        if not options:
            return
        duration = simpledialog.askinteger("Open a poll", "Duration in seconds:", initialvalue=DEFAULT_DURATION_S,
                                           minvalue=10, maxvalue=600, parent=self.root)
        if not duration:
            return
        self.polls = PollService(self.db, self.lesson)
        try:
            self.polls.open_poll(question, options.split(";"), duration,
                                 on_answer=lambda results: self.events.put(("answer", results)))
        except ValueError as e:
            messagebox.showerror("Open a poll", str(e))
            self.polls = None
            return
        self.log(f"Poll opened for {duration} s: {question}")
        # The fixed code on the projector opens the lesson page, for phones that do not have it open (FR-8.2).
        if self.poll_window:
            self.poll_window.destroy()
        self.poll_window = tk.Toplevel(self.root, bg="white")
        self.poll_window.title("Poll: scan to answer")
        tk.Label(self.poll_window, text=question, font=("Segoe UI", 26, "bold"), bg="white",
                 wraplength=700).pack(pady=(20, 5))
        self.poll_qr = ImageTk.PhotoImage(qrcode.make(f"{LESSON_URL}?l={self.lesson.id}",
                                                      box_size=10, border=3).get_image())
        tk.Label(self.poll_window, image=self.poll_qr, bg="white").pack()
        self.poll_label = tk.Label(self.poll_window, text="", font=("Segoe UI", 20), bg="white", justify="left")
        self.poll_label.pack(pady=(5, 20))
        self.show_poll(self.polls.results(), header=f"Open for {duration} s")
        self.root.after(duration * 1000, self.end_poll)

    def show_poll(self, results, header=None):
        if not self.poll_window or not self.polls:
            return
        header = header or f"{sum(c for _, c in results)} answers"
        self.poll_label["text"] = header + "\n" + "\n".join(f"{text}: {count}" for text, count in results)

    def end_poll(self):
        if not self.polls:
            return
        results = self.polls.close_poll()
        self.log("Poll closed. Results: " + ", ".join(f"{t} {c}" for t, c in results))
        self.show_poll(results, header=f"Closed: {sum(c for _, c in results)} answers")

    def delete_photos(self):
        """After the head count is saved in the sheet, delete this lesson's photos from the computer."""
        if not self.photo_paths:
            return
        if not self.sheet_written:
            self.log("Photos were kept: the head count is not saved in a sheet yet.")
            return
        names = "\n".join(Path(p).name for p in self.photo_paths)
        if not messagebox.askyesno("Delete class photos",
                                   f"The head count is saved in the sheet.\nDelete these "
                                   f"{len(self.photo_paths)} photo(s) from this computer?\n\n{names}"):
            self.log("Photos were kept, at the lecturer's choice.")
            return
        for p in self.photo_paths:
            try:
                os.remove(p)
                self.log(f"Deleted photo: {Path(p).name}")
            except OSError as e:
                self.log(f"Could not delete {Path(p).name}: {e}")

    def run(self):
        self.root.mainloop()
