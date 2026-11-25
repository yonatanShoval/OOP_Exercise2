"""One class meeting (FR-1.2, FR-1.3, FR-1.5).

Everything of a lesson is saved under its record: lessons/<id>/codes, lessons/<id>/checkins.
"""
from datetime import datetime
import secrets

from .database import Database

PERSONAL_COLLECTIONS = ("codes", "checkins")  # deleted from the cloud when the lesson closes


class Lesson:
    def __init__(self, db: Database, lesson_id: str):
        self.db = db
        self.id = lesson_id

    @classmethod
    def open(cls, db: Database, now: datetime | None = None) -> "Lesson":
        """Create a new lesson record. The id holds the date and a random part."""
        now = now or datetime.now()
        lesson_id = f"{now:%Y-%m-%d-%H%M}-{secrets.token_hex(2)}"
        db.set(f"lessons/{lesson_id}", {"date": f"{now:%Y-%m-%d}", "checkin_open": False, "closed": False})
        return cls(db, lesson_id)

    def path(self, collection: str = "") -> str:
        return f"lessons/{self.id}/{collection}" if collection else f"lessons/{self.id}"

    def set_checkin_open(self, is_open: bool) -> None:
        """The security rules accept a check-in only while this is True (FR-2.1)."""
        record = self.db.get(self.path()) or {}
        self.db.set(self.path(), {**record, "checkin_open": is_open})

    def close(self) -> int:
        """Stop check-in and delete the lesson's personal data from the cloud (FR-1.5).

        Returns how many documents were deleted. Write the sheet before closing.
        """
        deleted = sum(self.db.delete_collection(self.path(c)) for c in PERSONAL_COLLECTIONS)
        record = self.db.get(self.path()) or {}
        self.db.set(self.path(), {**record, "checkin_open": False, "closed": True})
        return deleted
