"""Quick polls (component C14): open, collect anonymous answers, close, count (FR-8.1 – FR-8.7).

The poll is saved with the server time. The security rules accept an answer only while
the poll is open: not closed, and less than duration_s seconds after it was opened.
"""
import secrets

from .database import Database
from .lesson import Lesson

DEFAULT_DURATION_S = 120


class PollService:
    def __init__(self, db: Database, lesson: Lesson):
        self.db = db
        self.lesson = lesson
        self.poll_id = None
        self.options: list[str] = []
        self.counts: list[int] = []

    def path(self) -> str:
        return f"{self.lesson.path('polls')}/{self.poll_id}"

    def open_poll(self, question: str, options: list[str], duration_s: int = DEFAULT_DURATION_S, on_answer=None):
        options = [o.strip() for o in options if o.strip()]
        if len(options) < 2:
            raise ValueError("A poll needs at least two options.")
        self.poll_id = secrets.token_hex(4)
        self.options, self.counts = options, [0] * len(options)
        self.db.set_stamped(self.path(), {"question": question.strip(), "options": options,
                                          "duration_s": int(duration_s), "closed": False})

        def handle(doc):
            i = doc.get("option")
            if isinstance(i, int) and 0 <= i < len(self.counts):
                self.counts[i] += 1
                if on_answer:
                    on_answer(self.results())
        self.db.listen(f"{self.path()}/answers", handle)
        return self.poll_id

    def close_poll(self) -> list[tuple[str, int]]:
        record = self.db.get(self.path()) or {}
        self.db.set(self.path(), {**record, "closed": True})
        return self.results()

    def results(self) -> list[tuple[str, int]]:
        return list(zip(self.options, self.counts))
