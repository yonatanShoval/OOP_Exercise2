"""Infrastructure test: listen in real time to messages sent from the phone page.

Reads the Firestore collection 'test-messages' with the Firebase Admin SDK
and prints every new message with its delay since it was sent. Read-only.
"""
import time
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

# Fixed path to the secret key: <repo root>/secrets/serviceAccountKey.json
KEY_PATH = Path(__file__).resolve().parents[3] / "secrets" / "serviceAccountKey.json"

if not KEY_PATH.exists():
    raise SystemExit(f"Key file not found: {KEY_PATH}\n"
                     "Download it from Firebase Console > Project settings > Service accounts.")

firebase_admin.initialize_app(credentials.Certificate(str(KEY_PATH)))
db = firestore.client()

is_first_snapshot = True


def on_change(docs, changes, read_time):
    """Called by Firestore in a background thread whenever the collection changes."""
    global is_first_snapshot
    now_ms = time.time() * 1000
    for change in changes:
        if change.type.name != "ADDED":
            continue
        msg = change.document.to_dict()
        device = msg.get("device", "unknown")
        text = msg.get("text", "")
        client_time = msg.get("clientTime")
        if is_first_snapshot:
            print(f"[existing] from {device}: {text}")
        elif client_time is None:
            print(f"[new] from {device} (no send time): {text}")
        else:
            # The delay compares the sender's clock (phone) with this computer's clock.
            # The two clocks are not perfectly in sync, so the delay is not fully accurate.
            delay = (now_ms - client_time) / 1000
            print(f"[new] from {device} after {delay:.2f}s: {text}")
    is_first_snapshot = False


watch = db.collection("test-messages").on_snapshot(on_change)
print("Listening to 'test-messages'... press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    watch.unsubscribe()
    print("Stopped.")
