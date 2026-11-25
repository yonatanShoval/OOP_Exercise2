"""Start the lecturer's window.

Usage (from the repository root):
    .venv\\Scripts\\python.exe app\\run_lecturer.py
"""
from teaching_tool.firestore_db import FirestoreDatabase
from teaching_tool.window import LecturerWindow

if __name__ == "__main__":
    LecturerWindow(FirestoreDatabase()).run()
