# Statement of Work (SoW)

Ex2 in Introduction to Software Engineering (OOP, OOD), Ariel University.
Project: Web-based Teaching Tool.

This document defines what this project will deliver, what it will not deliver, and how we will know it is done. The detailed requirements are in the SRS ([srs.md](srs.md)), and the client stories are in the use cases ([use-cases.md](use-cases.md)). Every tool named here was tested for real in the tools report ([tools-report.md](tools-report.md)).

## 1. Purpose and background

Online teaching tools are too complicated to use quickly in class, and most of them do not work with LLMs. Attendance is the biggest problem: checking it by hand takes class time, and the lecturer has no simple, accurate record. During a lecture, students have no easy way to give feedback, and the lecturer has no quick way to check if the material is understood. After the lecture, generic summaries and homework feedback are of little help.

The goal is a few small tools that work from a phone, are simple to use in a real class, and are shown working in a live demo.

## 2. Objectives

The assignment defines five features. Attendance is the main one.

| # | Feature | What success looks like |
|---|---|---|
| 1 | **Attendance** | Students check in from their phone. A photo of the class gives a head count. When the count and the check-ins do not match, the lecturer is alerted and decides. The result is a spreadsheet. |
| 2 | **Comments and suggestions** | A student writes a short comment from the phone. The lecturer sees the comments of the current lesson, during the lesson or after it, as the lecturer decides. |
| 3 | **Quick polls** | The lecturer opens a short poll on the spot. Students answer from the phone. The lecturer sees the results when the poll closes. |
| 4 | **Lecture summary** | From a class recording, the lecturer gets a transcript and a summary. |
| 5 | **Homework review** | From a list of repository links, the lecturer gets a review of each submission, a ranking, and a class comparison. Each student gets their own report, and can also review their own repository before submitting. |

## 3. Users

- **The lecturer** runs the system from a simple window on their own computer and does not write code.
- **The student** uses only a phone browser: no app to install and no account. For the homework review only, a student can also run the review script on their own computer.

## 4. Deliverables

1. **Documents** in this repository:
   - README (problem and scope)
   - Tools report
   - This SoW
   - SRS
   - Use cases
   - Main software components
   - Class diagrams and sequence diagrams
   - Testing strategy
   - Summary of results
2. **A demo system:**
   - A phone web page for students, served from Firebase Hosting.
   - A Python program with a simple window (tkinter) for the lecturer, on the lecturer's computer.
3. **A live demo in class**, about 10 minutes, that shows the features working for real.

## 5. In scope

### Feature 1: Attendance
- **Course list:** the lecturer loads the course participant list (an `.xlsx` file) and opens a lesson.
- **Check-in:**
  - The lecturer's window shows a rotating QR code on the projector. The student scans it and checks in.
  - The student types their email once. The phone remembers it.
  - Python checks the code's time against the server time, and checks the email against the course list.
- **Photo and head count:**
  - The lecturer takes one or more photos of the class.
  - A local model (YOLO26) counts the people, and a software rule removes double counts.
  - The lesson's count is the highest count of its photos.
- **Mismatch:** when the number of check-ins and the head count differ, or an email is not on the course list, the lecturer gets an alert.
- **Challenge:**
  - The photo is shown only on the projector, with a number on each box.
  - Each checked-in student types the number of their own box, or "I am not in the photo".
- **Lecturer's decision:** the lecturer resolves every mismatch by hand.
- **Spreadsheet:** the result is written to an offline `.xlsx` file, or to an online Google Sheet.

### Feature 2: Comments and suggestions
- The student writes a short, anonymous comment on the lesson's page.
- The lecturer sets, for each lesson, whether comments are open during the lesson or only after it.
- The lecturer sees new comments in real time.
- At the end of the lesson, Python writes the comments to a "Comments" tab in the spreadsheet.
- A comment written with no network is saved on the phone and sent when the network returns.

### Feature 3: Quick polls
- The lecturer opens a poll from the window, with a duration. The default is 2 minutes, and the lecturer can close it early.
- A fixed QR code on the projector opens the poll page. Phones that already have the page open get the poll right away.
- After the poll closes, answers are rejected, and the lecturer sees the results.

### Feature 4: Lecture summary
- The lecturer downloads the class recording and gives it to the system by hand.
- The recording is transcribed on the lecturer's computer (faster-whisper).
- The summary is automatic, through the Gemini API, with the same engine interface (`LlmEngine`) and the same manual backup as the homework review.
- Before the transcript is sent, the lecturer's window asks the lecturer to confirm, because the transcript may hold names and voices of students, and on the free tier Google uses the content. If the lecturer does not confirm, the transcript stays on the lecturer's computer.
- The transcript and the summary stay with the lecturer. The lecturer can share them through the channel they already use.

### Feature 5: Homework review
- The lecturer gives a text file with one repository link per line.
- A script downloads each repository and packs it into one text file, under an anonymous name (Repo A, Repo B, and so on).
- The review is automatic: the system sends each packed repository to the Gemini API (free tier) and saves the answer. This is the "machine" that goes through all the submissions.
- The design has one interface, `LlmEngine`, with two implementations:
  - **Gemini API:** the main one, automatic. The model is `gemini-4-hydrogen`, and the model name is a parameter. When the daily free quota (20 requests) runs out, the review continues the next day with the same model, so that every submission is reviewed by the same model and the ranking stays fair.
  - **Manual:** the backup. The script prepares the request, and the lecturer pastes it into a free LLM chat.
- The output, in two stages:
  - **Stage 1:** one Markdown report per link, with a score for each criterion, and one sheet that ranks all the links by score.
  - **Stage 2:** one request with a short summary of each review gives a class comparison: where each submission stands, and what others did well.
- **Students and teachers:** the lecturer runs the review on the whole course and gives each student their own report. A student can run the same script on their own repository before submitting, with their own free key.

The review supports a human grader and does not replace one.

## 6. Out of scope

- **Participants from Zoom:** the system covers only the students in the classroom.
- **A screen for sharing summaries** with students: the lecturer shares through their existing channel.
- **Integrations with Zoom or Moodle:** files are moved by hand.
- **Rare edge cases:** they are not solved automatically. The lecturer decides by hand.
- **Photos of different parts of the class**, which would need a sum of counts instead of the highest count.
- **Face recognition:** the system only counts people and never identifies them.
- **Loading the page with no network** (no Service Worker / PWA).
- **Teaching-quality analysis** of the lecture, for example language mistakes or voice quality.
- **Student accounts and sign-in.**
- **Personal information in the cloud:**
  - The real participant list stays on the lecturer's computer.
  - Tests use invented data only.

## 7. Assumptions and constraints

- **Free accounts only:** Firebase Spark plan, the free Google Sheets API, the Gemini API free tier, and a free LLM chat.
- **Data on the Gemini free tier:** Google uses the content to improve its products. For the homework review, we accept this, because only public repositories are sent, under anonymous names. For the lecture summary, the transcript may hold students' names and voices, so it is sent only after the lecturer confirms.
- **Network:** there is a network in the classroom. Check-in and polls need it.
- **One computer:** the lecturer's computer runs all the logic in Python. The class photo and the recording never leave it.
- **Phones:** the student needs only a phone browser and a camera to scan a QR code.
- **Tested tools only:** every tool in this document was tested in the tools report.
- **Simplicity:** the design keeps to what can be implemented and shown in the demo.

## 8. Schedule

The submission date is Monday 30/11/2026. It was moved from 25/11. Our target is to finish everything by Friday 27/11.

| Date | Work |
|---|---|
| Done | 1. README<br>3. Tools report |
| Wed 25/11 | 4. SoW<br>5. SRS<br>6. Use cases |
| Thu 26/11 | 7. Main software components<br>8. Class and sequence diagrams<br>9. Testing strategy<br>The start of 10. Demo system |
| Fri 27/11 | The end of 10. Demo system<br>12. Summary of results<br>2. Submit the repository form |
| In class | 11. Live demo |

## 9. Acceptance criteria

The work is done when all of the following are true:

1. Every document in section 4 is in the repository and linked from the README.
2. In the live demo, attendance works end to end:
   - check-in from a phone,
   - a head count from a new photo,
   - a mismatch alert,
   - a challenge,
   - the lecturer's decision,
   - the spreadsheet.
3. Features 2–5 are each shown working at least once in the live demo. The live demo is the main proof. A recorded run, linked from the README, is a backup only.
4. No secret key, class photo, recording or real student data is in the repository.
5. Every requirement in the SRS links to a use case and to a test.

## 10. Risks

| Risk | Effect | What we do |
|---|---|---|
| The head count is wrong on new photos. The double-count rule was tuned on 16 photos. | The lecturer gets false mismatch alerts. | The lecturer's target is ±10%. The challenge and the lecturer's decision catch the errors. The demo is the real test. |
| The head count is slow. It took about 5.3 s per photo on a regular CPU. | The lecturer waits. | Photos are counted after they are taken, not live. |
| The transcript has errors. In the test, the model invented words over silence and missed the first 30 seconds. | The summary can be wrong. | The lecturer checks the summary. The summary is ready about 2 hours after the lesson. |
| The rotating QR code is forwarded to someone at home. | There is a false check-in. | The code is valid for 20 seconds only. The head count and the challenge are the real check. |
| The Gemini free tier allows only 20 requests per day, or it changes. | A hundred submissions take about five days. | The review continues the next day with the same model. If the API is not available, the manual engine is the backup. Both use the same `LlmEngine` interface. |
| The review misses problems or invents results. In the test, Hydrogen found 1 of 3 checked claims, in a single run. | A wrong review misleads the grader and the student. | The main model was chosen because it did not invent results. The review supports a human grader and does not replace one. |
| The service account key leaks. | Someone gets full access to the project. | The key is kept in a folder blocked by `.gitignore`, and `git status` is checked before each commit. |
