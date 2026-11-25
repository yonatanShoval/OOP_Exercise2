"""The only door from Python to the data (component C8).

`Database` is the interface. The other classes depend only on it, so a test can give
them `FakeDatabase` (in memory, no network, no key) instead of the real Firestore.

Paths look like Firestore paths: a collection is "lessons" or "lessons/<id>/checkins",
and a document is "lessons/<id>".
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
import itertools


class Database(ABC):
    """What the logic needs from a database."""

    @abstractmethod
    def add(self, collection: str, data: dict) -> str:
        """Add a document with a new id, stamped with the server time. Returns the id."""

    @abstractmethod
    def set(self, path: str, data: dict) -> None:
        """Create or replace the document at path."""

    @abstractmethod
    def get(self, path: str) -> dict | None:
        """The document at path, or None."""

    @abstractmethod
    def list(self, collection: str) -> list[dict]:
        """All documents in a collection, each with its id under "id"."""

    @abstractmethod
    def listen(self, collection: str, callback) -> None:
        """Call callback(document) for each new document in the collection."""

    @abstractmethod
    def delete_collection(self, collection: str) -> int:
        """Delete every document in a collection. Returns how many were deleted."""


class FakeDatabase(Database):
    """A database in a Python dictionary, for unit tests.

    The "server time" comes from a clock function, so a test can set it.
    """

    def __init__(self, clock=None):
        self._docs: dict[str, dict] = {}
        self._listeners: dict[str, list] = {}
        self._ids = itertools.count(1)
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def add(self, collection, data):
        doc_id = f"doc{next(self._ids)}"
        doc = {**data, "server_time": self.clock()}
        self._docs[f"{collection}/{doc_id}"] = doc
        for callback in self._listeners.get(collection, []):
            callback({**doc, "id": doc_id})
        return doc_id

    def set(self, path, data):
        self._docs[path] = dict(data)

    def get(self, path):
        doc = self._docs.get(path)
        return dict(doc) if doc is not None else None

    def list(self, collection):
        prefix = collection + "/"
        return [
            {**doc, "id": path[len(prefix):]}
            for path, doc in self._docs.items()
            if path.startswith(prefix) and "/" not in path[len(prefix):]
        ]

    def listen(self, collection, callback):
        self._listeners.setdefault(collection, []).append(callback)

    def delete_collection(self, collection):
        prefix = collection + "/"
        paths = [p for p in self._docs if p.startswith(prefix) and "/" not in p[len(prefix):]]
        for p in paths:
            del self._docs[p]
        return len(paths)
