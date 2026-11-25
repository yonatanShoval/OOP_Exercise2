"""Check-in (component C9): rotating codes, and the check of each check-in (FR-2.1 – FR-2.8).

The age of a code is measured with server times only: the time the code was saved, and
the time the check-in was saved. The window's own timer is never trusted, because it drifts.

The security rules check the code first, at the entrance, so the phone learns at once if
its code expired. This class checks again, as a backup (D52).

Why 60 seconds: in the phone test on 25/11, a first check-in took up to about 30 seconds
(the code is on screen up to 10 s before the scan, typing the email 10–15 s, sending about
3 s), and was rejected with a window of 20 s.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import secrets

from .course import Course, normalize_email
from .database import Database
from .lesson import Lesson

ROTATE_SECONDS = 10
MAX_CODE_AGE = timedelta(seconds=60)  # must match the security rules (app/firestore.rules)


@dataclass
class CheckInResult:
    status: str  # "accepted", "duplicate", "unknown_email", "old_code", "unknown_code"
    email: str


@dataclass
class CheckInCounts:
    accepted: set = field(default_factory=set)       # emails on the course list
    unknown_emails: set = field(default_factory=set)  # valid code, email not on the list
    rejected: int = 0                                 # old or unknown codes


class CheckInService:
    def __init__(self, db: Database, course: Course, lesson: Lesson):
        self.db = db
        self.course = course
        self.lesson = lesson
        self._codes: dict[str, datetime] = {}  # code -> server time it was saved
        self.counts = CheckInCounts()

    def next_code(self) -> str:
        """Make a new random code, and save it with the server time (FR-2.2)."""
        value = secrets.token_urlsafe(6)  # letters, digits, "-" and "_": a valid document id
        path = f"{self.lesson.path('codes')}/{value}"  # stored under its value, so the rules can find it
        self.db.set_stamped(path, {})
        self._codes[value] = self.db.get(path)["server_time"]
        return value

    def handle(self, checkin: dict) -> CheckInResult:
        """Check one check-in record: {"email", "code", "server_time"} (FR-2.6 – FR-2.8)."""
        email = normalize_email(checkin.get("email", ""))
        shown_at = self._codes.get(checkin.get("code", ""))
        if shown_at is None:
            self.counts.rejected += 1
            return CheckInResult("unknown_code", email)
        age = checkin["server_time"] - shown_at
        if age < timedelta(0) or age > MAX_CODE_AGE:
            self.counts.rejected += 1
            return CheckInResult("old_code", email)
        if self.course.find(email) is None:
            self.counts.unknown_emails.add(email)
            return CheckInResult("unknown_email", email)
        if email in self.counts.accepted:
            return CheckInResult("duplicate", email)
        self.counts.accepted.add(email)
        return CheckInResult("accepted", email)

    def listen(self, on_result) -> None:
        """Handle each new check-in as it arrives, and report the result."""
        self.db.listen(self.lesson.path("checkins"), lambda doc: on_result(self.handle(doc)))
