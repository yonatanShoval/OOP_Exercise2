"""Comments (component C13): anonymous comments of one lesson (FR-7.1 – FR-7.6), simple version.

The lecturer sets the mode on the lesson record. The security rules read it, and accept
a comment only when the mode allows it:
  "during": open now.  "after": open only after the lesson is closed.  "closed": never.
"""
from datetime import datetime

from .database import Database
from .lesson import Lesson

MODES = ("during", "after", "closed")


class CommentService:
    def __init__(self, db: Database, lesson: Lesson):
        self.db = db
        self.lesson = lesson
        self.comments: list[dict] = []  # {"text", "server_time"}, never an email

    def set_mode(self, mode: str) -> None:
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
        record = self.db.get(self.lesson.path()) or {}
        self.db.set(self.lesson.path(), {**record, "comment_mode": mode})

    def listen(self, on_comment) -> None:
        def handle(doc):
            comment = {"text": doc.get("text", ""), "server_time": doc.get("server_time")}
            self.comments.append(comment)
            on_comment(comment)
        self.db.listen(self.lesson.path("comments"), handle)

    def rows(self) -> list[dict]:
        """Rows for the "Comments" tab: lesson, time, text (FR-7.6)."""
        def when(t):
            return t.astimezone().strftime("%Y-%m-%d %H:%M") if isinstance(t, datetime) else ""
        return [{"lesson": self.lesson.id, "time": when(c["server_time"]), "text": c["text"]}
                for c in self.comments]
