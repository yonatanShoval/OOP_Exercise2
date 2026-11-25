"""Writing the attendance sheet (component C12).

`SheetWriter` is the interface. In this demo only the local `.xlsx` implementation is
built, because a sheet with real names is kept only as a file on the lecturer's
computer, never in Google Sheets (D49).
"""
from abc import ABC, abstractmethod


class SheetWriter(ABC):
    """What the logic needs to write the attendance."""

    @abstractmethod
    def write_attendance(self, lesson_name: str, rows: list[dict]) -> str:
        """Write one row per student, with a column for this lesson's status.

        Each row has: first_name, last_name, email, group, status.
        Returns where the sheet was written.
        """
