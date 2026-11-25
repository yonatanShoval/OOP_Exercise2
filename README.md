# Web-based Teaching Tool

Ex2 in Introduction to Software Engineering (OOP, OOD), Ariel University.
Author: Yonatan Shoval

A simple web app that helps lecturers take attendance, run quick polls, and get AI summaries and homework reviews.

## The problem

Current online teaching tools are too complicated to use quickly in class, and most of them are not built to work with LLMs.

Attendance is the biggest problem: checking it by hand takes class time, and the lecturer has no simple way to get an accurate record.

During a lecture, there is no easy way for students to ask questions or give feedback, or for the lecturer to quickly check if the material is understood.

Automatic class summaries, like the one Zoom generates, are generic and not very useful for studying. Homework feedback rarely shows students how their solution compares to other approaches.

None of this needs a big system. It needs a few small tools that work from a phone.

## Who uses it

- **The lecturer** wants to know who is in the room without spending class time on it, get quick feedback during the lecture, and get useful summaries and reviews after it.
- **The student** wants to open a link on their phone, with no app to install.

## What I'm building

One web app with two views: a phone view for students and a dashboard for the lecturer.

1. **Attendance** (the main feature). Students check in from their phone. The lecturer can take a photo of the class to get a head count, and gets the attendance details in an online or offline spreadsheet.
2. **Comments and suggestions** that students can send during class or later.
3. **Quick polls** the lecturer can open on the spot about the current material.
4. **Lecture summary**: an ML/LLM summary of a recorded class (Zoom, Meet, Google Classroom).
5. **Homework review**: an LLM review of a submission, including how it compares to other students' work. Comparisons are anonymous.

The exact details of each feature (how check-in works, what the lecturer uploads, and so on) will be decided in the SRS.

## Out of scope

- No integration with Moodle or Zoom. Files are uploaded by hand.
- No personal information about students.
- Only features that can be shown working in a 10-minute live demo in class.

## Progress

- [x] 1. Repository, problem and scope (this README)
- [ ] 2. Submit the repository
- [x] 3. Tools report (every tool tested for real): [docs/tools-report.md](docs/tools-report.md)
- [x] 4. SoW: [docs/sow.md](docs/sow.md)
- [ ] 5. SRS
- [ ] 6. Use cases
- [ ] 7. Main software components
- [ ] 8. Class diagrams and sequence diagrams
- [ ] 9. Testing strategy
- [ ] 10. Demo web app
- [ ] 11. Demo in class
- [ ] 12. Summary of results

## License

License: AGPL-3.0 (required by Ultralytics YOLO, see docs/tools-report.md)
