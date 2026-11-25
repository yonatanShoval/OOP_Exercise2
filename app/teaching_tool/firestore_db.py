"""The real Database: Firestore through the Firebase Admin SDK (component C8).

Note: the Admin SDK uses the service account and bypasses the security rules. The rules
protect the data only against the phones, so they are tested as a client, without this key.
"""
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

from .database import Database

REPO_ROOT = Path(__file__).resolve().parents[2]
KEY_FILE = REPO_ROOT / "secrets" / "serviceAccountKey.json"


class FirestoreDatabase(Database):
    def __init__(self, key_file: str | Path = KEY_FILE):
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(str(key_file)))
        self._db = firestore.client()
        self._watches = []

    def add(self, collection, data):
        ref = self._db.collection(collection).document()
        ref.set({**data, "server_time": firestore.SERVER_TIMESTAMP})
        return ref.id

    def set(self, path, data):
        self._db.document(path).set(data)

    def set_stamped(self, path, data):
        self._db.document(path).set({**data, "server_time": firestore.SERVER_TIMESTAMP})

    def get(self, path):
        snap = self._db.document(path).get()
        return snap.to_dict() if snap.exists else None

    def list(self, collection):
        return [{**d.to_dict(), "id": d.id} for d in self._db.collection(collection).stream()]

    def listen(self, collection, callback):
        def on_snapshot(docs, changes, read_time):
            for change in changes:
                if change.type.name == "ADDED":
                    callback({**change.document.to_dict(), "id": change.document.id})
        self._watches.append(self._db.collection(collection).on_snapshot(on_snapshot))

    def delete_collection(self, collection):
        count = 0
        for doc in self._db.collection(collection).stream():
            doc.reference.delete()
            count += 1
        return count

    def stop(self):
        for watch in self._watches:
            watch.unsubscribe()
        self._watches.clear()
