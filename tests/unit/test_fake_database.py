"""The fake database must behave like the real one, or tests that use it prove nothing."""
from datetime import datetime, timezone

from teaching_tool.database import FakeDatabase


def fixed_clock():
    return datetime(2026, 11, 26, 9, 5, 27, tzinfo=timezone.utc)


def test_add_stamps_server_time_and_lists():
    db = FakeDatabase(clock=fixed_clock)
    doc_id = db.add("lessons/L1/checkins", {"email": "student01@demo.test"})
    docs = db.list("lessons/L1/checkins")
    assert len(docs) == 1
    assert docs[0]["id"] == doc_id
    assert docs[0]["server_time"] == fixed_clock()


def test_listen_gets_new_documents():
    db = FakeDatabase()
    seen = []
    db.listen("lessons/L1/checkins", seen.append)
    db.add("lessons/L1/checkins", {"email": "student02@demo.test"})
    assert [d["email"] for d in seen] == ["student02@demo.test"]


def test_list_does_not_mix_collections():
    db = FakeDatabase()
    db.add("lessons/L1/checkins", {"email": "a@demo.test"})
    db.add("lessons/L2/checkins", {"email": "b@demo.test"})
    assert len(db.list("lessons/L1/checkins")) == 1


def test_delete_collection_removes_only_that_collection():
    db = FakeDatabase()
    db.add("lessons/L1/checkins", {"email": "a@demo.test"})
    db.add("lessons/L1/checkins", {"email": "b@demo.test"})
    db.set("lessons/L1", {"date": "2026-11-26"})
    assert db.delete_collection("lessons/L1/checkins") == 2
    assert db.list("lessons/L1/checkins") == []
    assert db.get("lessons/L1") == {"date": "2026-11-26"}
