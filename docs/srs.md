# Software Requirements Specification (SRS)

Ex2 in Introduction to Software Engineering (OOP, OOD), Ariel University.
Project: Web-based Teaching Tool.

## 1. Introduction

### 1.1 Purpose
This document lists what the system must do (functional requirements) and how well it must do it (non-functional requirements). It is the base for the components, the diagrams, the tests and the demo.

### 1.2 Scope
The scope is defined in the SoW ([sow.md](sow.md)). In short, the system has five features:
1. Attendance, the main feature
2. Comments and suggestions
3. Quick polls
4. Lecture summary
5. Homework review

The client stories are in the use cases ([use-cases.md](use-cases.md)). The evidence that each tool works is in the tools report ([tools-report.md](tools-report.md)).

### 1.3 Glossary

| Term | Meaning |
|---|---|
| **Lesson** | One class meeting. All check-ins, comments and polls belong to one lesson. |
| **Course list** | The participant list the lecturer downloads from the course site, as `.xlsx`. It has the first name, last name, email and group of each student. |
| **Check-in** | A student marks themselves present from the phone, by scanning the code on the projector. |
| **Rotating code** | A QR code on the projector that changes every 10 seconds. It opens the check-in page. |
| **Head count** | The number of people that the model finds in a photo of the class. |
| **Mismatch** | A gap that the lecturer must look at. For example, the number of check-ins differs from the head count, or an email is not on the course list. |
| **Challenge** | After a mismatch, each checked-in student points to themselves in the class photo, by the number of their box. |
| **Box** | A frame that the model draws around one person in the photo. Each box has a number. |
| **Lecturer's window** | A simple desktop window in Python (tkinter) on the lecturer's computer. The lecturer runs everything from it and writes no code. |
| **Bundle** | One text file that holds one repository: its file tree, and then its text files. |
| **LlmEngine** | The interface that sends a text to an LLM and returns its answer. The homework review and the lecture summary both use it. It has two implementations: Gemini (automatic, the main one) and manual (the backup). |

## 2. Overall description

### 2.1 Users

| User | Device | Needs |
|---|---|---|
| **Lecturer** | Their own computer, connected to the projector | To run every feature from one window, quickly, with no code. |
| **Student** | Their own phone, with any browser. For the homework review only: their own computer, with Python. | To open a link, with no app to install and no account. To get a review of their homework before they submit it. |

### 2.2 Operating environment
- **The student's phone:** a static web page served by Firebase Hosting. The page only shows and sends data, and holds no logic. Tested on an iPhone with Chrome.
- **The cloud:** Firebase on the free Spark plan. It has two parts:
  - Firestore, a real-time database in region `me-west1`.
  - Hosting, which serves the page.

  Google Sheets is the online spreadsheet. The Gemini API is used on its free tier.
- **The lecturer's computer:** Python 3.14 runs all the logic:
  - the window,
  - the head count,
  - the transcription,
  - the spreadsheets,
  - the review.

  It connects to Firestore with a service account key, kept in a folder blocked by `.gitignore`.

### 2.3 Assumptions and constraints
- **Free accounts only.**
- **Network:** there is a network in the classroom.
- **Local data:**
  - The class photo and the recording never leave the lecturer's computer.
  - The real course list stays on the lecturer's computer.
- **Simplicity (KISS):** the design includes only what can be implemented and shown in the demo.
- **License:** the project is licensed under AGPL-3.0, because the head count library requires it.

## 3. Functional requirements

Each requirement has an ID. The use case column links it to the use cases document.

### 3.1 Lessons and the course list (UC-1)

| ID | Requirement |
|---|---|
| FR-1.1 | The lecturer loads the course list (`.xlsx`) in the window. The system reads the first name, last name, email and group of each student. |
| FR-1.2 | The lecturer opens a new lesson. The system creates a lesson record in the database, with the date and the server time. |
| FR-1.3 | Every check-in, comment and poll is saved under its lesson. The phone page knows the lesson from the link that the code opens. |
| FR-1.4 | The course list itself is not uploaded to the cloud. The system uses it only on the lecturer's computer. |
| FR-1.5 | After the lesson, when the sheet has been written, the lecturer closes the lesson. The system then deletes the lesson's data from the cloud: the codes, the check-ins with their emails, and the challenge answers. |

### 3.2 Attendance: check-in (UC-2)

| ID | Requirement |
|---|---|
| FR-2.1 | The lecturer starts and stops check-in from the window. While it is on, the window shows a rotating code on the projector. The code changes every 10 seconds. |
| FR-2.2 | Each code is saved in the database with the server time at which it was shown. |
| FR-2.3 | When a student scans the code, the phone opens the check-in page of that lesson. |
| FR-2.4 | The first time, the student types their email. The phone remembers it. Later check-ins send it with no typing. The student can change it. |
| FR-2.5 | The phone sends the check-in: the email, the code, and the lesson. The database adds the server time. |
| FR-2.6 | A check-in is accepted only if its code exists and was saved less than 60 seconds before the check-in's server time. The security rules check this at the entrance, so an expired code is rejected before it is saved. Python checks it again as a backup, and the lecturer sees how many check-ins were rejected. 60 seconds, not 20: in the phone test on 25/11, a first check-in with email typing took up to about 30 seconds, and was rejected with 20. |
| FR-2.7 | Python checks the email against the course list. An email that is not on the list is a mismatch (FR-4.1). |
| FR-2.8 | A second check-in with the same email in the same lesson is counted once. |
| FR-2.9 | The phone shows the student the result: "Check-in received", "The code expired. Scan the code on the projector again.", or "Check-in is closed." The saved email stays on the phone. A check-in is never shown as received when it was rejected. |

### 3.3 Attendance: photo and head count (UC-3)

| ID | Requirement |
|---|---|
| FR-3.1 | The lecturer takes the photos with their own phone, as the lecturer described ("he can pick up his phone and take a photo", attendance transcript, lines 29–33). The photo reaches the computer in the lecturer's usual way, and the lecturer adds it to the lesson with "Add class photos". Our system never uploads the photo to any cloud: uploading from the phone to our cloud was considered and rejected, for privacy (D8). A local transfer (cable, or a transfer on the local network) is recommended. If the lecturer uses their own cloud, for example an email to themselves or Google Photos, the photo is in the lecturer's own account, under the lecturer's responsibility (D53). |
| FR-3.2 | Python counts the people in each photo with a local model (YOLO26x, at an image size of 1280). The photo is never sent to any cloud service. |
| FR-3.3 | A software rule merges two boxes of the same person into one. For example, when the desk splits a student into an upper body and legs (D28). |
| FR-3.4 | Each photo is counted on its own. The lesson's head count is the highest count of its photos. |
| FR-3.5 | The window shows the count of each photo and the lesson's head count. |

### 3.4 Attendance: mismatch (UC-4)

| ID | Requirement |
|---|---|
| FR-4.1 | The system raises a mismatch alert in the lecturer's window in each of these cases:<br>(a) the number of accepted check-ins differs from the lesson's head count;<br>(b) a check-in email is not on the course list;<br>(c) in a challenge, more than one student chose the same box;<br>(d) in a challenge, a student chose "I am not in the photo". |
| FR-4.2 | The alert shows the numbers and the items involved, for example the email or the box number. |
| FR-4.3 | After case (a), the lecturer decides whether to start a challenge (UC-5) or to decide directly (UC-6). The system does not decide by itself. |

### 3.5 Attendance: challenge (UC-5)

| ID | Requirement |
|---|---|
| FR-5.1 | The challenge runs during the lesson. The lecturer starts it from the window. |
| FR-5.2 | The window shows the photo with the highest count on the projector only, with a number on each box. The photo is not sent to the phones or to the cloud. |
| FR-5.3 | Each checked-in student types the number of their own box on the phone, or chooses "I am not in the photo". |
| FR-5.4 | The lecturer closes the challenge. After that, answers are rejected. |
| FR-5.5 | After the challenge, the window lists:<br>- boxes chosen by more than one student,<br>- students who chose "I am not in the photo",<br>- checked-in students who did not answer,<br>- boxes that no one chose. |

### 3.6 Attendance: the lecturer's decision and the spreadsheet (UC-6)

| ID | Requirement |
|---|---|
| FR-6.1 | For every open mismatch, the lecturer marks each student involved as present or absent. Rare edge cases are always left to the lecturer. |
| FR-6.2 | The system writes the attendance to a spreadsheet: one row per student, with the name, email and group, and one column per lesson with the status. |
| FR-6.3 | The spreadsheet can be an offline `.xlsx` file on the lecturer's computer (openpyxl), or an online Google Sheet (gspread). After the `.xlsx` file is written, it opens in Excel automatically. |
| FR-6.4 | Only invented data is written to Google Sheets. A sheet with real names is kept only as an `.xlsx` file on the lecturer's computer, also in the demo. |

### 3.7 Comments and suggestions (UC-7, UC-8)

| ID | Requirement |
|---|---|
| FR-7.1 | A student writes a short comment on the lesson's page, of 1 to 200 characters. |
| FR-7.2 | Comments are anonymous. The comment is saved with its lesson and the server time, without the email. |
| FR-7.3 | For each lesson, the lecturer sets whether comments are open during the lesson, or only after it. After the lesson, comments stay open until the lecturer closes them. When comments are closed, new comments are rejected. |
| FR-7.4 | A comment written with no network is saved on the phone. It is sent when the network returns, even if the browser was closed in between. |
| FR-7.5 | The lecturer sees each new comment of the current lesson in the window, in real time. |
| FR-7.6 | At the end of the lesson, or when the lecturer asks, Python writes the lesson's comments to a "Comments" tab in the spreadsheet, with the date, the time and the text. |

### 3.8 Quick polls (UC-9, UC-10, UC-11)

| ID | Requirement |
|---|---|
| FR-8.1 | The lecturer opens a poll from the window. A poll has one question and a few answer options, and a duration. The default duration is 2 minutes. |
| FR-8.2 | While the poll is open, the window shows a fixed QR code on the projector. The code opens the poll page. |
| FR-8.3 | A phone that already has the lesson's page open shows the poll right away. |
| FR-8.4 | The student chooses one option. The answer is saved with the poll and the server time, without the email. |
| FR-8.5 | The phone remembers that it answered the poll, and does not let the same phone answer it again. This does not stop cheating, but it stops double votes by mistake, so the lecturer gets a reliable number. |
| FR-8.6 | The poll closes when its time ends, or earlier if the lecturer closes it. After that, the database rejects new answers. |
| FR-8.7 | When the poll closes, the window shows the number of answers for each option. |

### 3.9 Lecture summary (UC-12)

| ID | Requirement |
|---|---|
| FR-9.1 | The lecturer chooses a class recording, an audio or video file downloaded by hand from Zoom or a similar tool. |
| FR-9.2 | Python transcribes the recording on the lecturer's computer (faster-whisper, model `large-v3-turbo`). The recording is not sent to any cloud service. |
| FR-9.3 | The transcript is saved as a text file on the lecturer's computer. |
| FR-9.4 | Before anything is sent, the window asks the lecturer to confirm sending the transcript. It explains why: the transcript may hold names and voices of students, and on the free tier Google uses the content to improve its products. |
| FR-9.5 | If the lecturer confirms, the system sends the transcript through the `LlmEngine` interface, the same as the homework review. The main implementation is the Gemini API (`gemini-4-hydrogen`). The summary is saved next to the transcript. |
| FR-9.6 | If the lecturer does not confirm, nothing is sent, and the transcript stays on the lecturer's computer. The manual engine is only a backup for when the Gemini API is not available, after the lecturer confirmed: it writes the request to a file, for the lecturer to paste into an LLM chat. |
| FR-9.7 | The transcript and the summary stay with the lecturer. The system has no screen for sharing them. The summary uses its own Google project and key, separate from the review, because the free quota is per project, not per key. So it has its own 20 requests per day, and one summary per day is enough. It uses the same retry rule as the review (FR-10.5): at most three tries, with a growing wait between them. Unlike the review, the summary compares no students, so it may switch models: after three failed tries on `gemini-4-hydrogen`, it tries `gemini-3.6-flash`, and records in the summary file which model made it. |

### 3.10 Homework review (UC-13)

| ID | Requirement |
|---|---|
| FR-10.1 | The lecturer gives a text file with one public repository link per line. |
| FR-10.2 | Python downloads each repository and packs it into one bundle. The bundle holds the full file tree, and then the text files, most important first, up to 150,000 characters. Files that did not fit are listed at its end. |
| FR-10.3 | Each repository gets an anonymous name: Repo A, Repo B, and so on. The key from name to link is saved only on the lecturer's computer. |
| FR-10.4 | The review goes through the `LlmEngine` interface. The main implementation sends each bundle with the review request to the Gemini API. The model is `gemini-4-hydrogen`, and the model name is a parameter. |
| FR-10.5 | When the daily free quota runs out, the review stops and continues the next day with the same model. The system does not switch models in the middle of a list. When the model is busy (error 503), the system tries each request at most three times, and waits longer before each new try: 30 seconds, then 60 seconds. On 2026-11-25, three tries 6 seconds apart all failed, so tries without a growing wait do not help. |
| FR-10.6 | The backup implementation writes the request to a file, for the lecturer to paste into a free LLM chat. The answer is then saved the same way. |
| FR-10.7 | Stage 1, one review per repository: the output is one Markdown report per link, with a score for each criterion, and one sheet that ranks all the links by score. |
| FR-10.8 | Every report states that it supports a human grader and does not replace one. It also states what it could not check from the bundle. |
| FR-10.9 | Stage 2, a class comparison: after all the reviews, the system sends one request with a short summary of each review, under the anonymous names. The answer is a class comparison: where each submission stands, and what others did well. It is saved as one Markdown report. |
| FR-10.10 | The lecturer runs the review on the whole course and gives each student their own report, together with the class comparison. |
| FR-10.11 | A student can run the same script on their own repository before submitting, with their own free Gemini key. They get a stage 1 report. Stage 2 needs the whole course, so only the lecturer runs it. |

## 4. Non-functional requirements

| ID | Type | Requirement | Evidence or target |
|---|---|---|---|
| NFR-1 | Simplicity | A student checks in with a scan and at most 3 taps, with no app and no account. | Target. Google Forms took 3 taps (tools report, section 5). |
| NFR-2 | Simplicity | The lecturer runs every feature from one window and writes no code. | Design. |
| NFR-3 | Accuracy | The head count is within ±10% of a manual count. | The lecturer's target. In the test, after the rule, the count matched the manual count exactly on all 4 photos (section 3). The real test is on new photos in the demo. |
| NFR-4 | Performance | The head count takes about 6 s or less per photo, on a regular laptop CPU. | Measured: an average of 5.3 s (section 3). |
| NFR-5 | Performance | A comment appears in the lecturer's window within a few seconds. | Measured: 0.88 s to save on the phone, and about 3.7 s to the computer, including the clock gap (section 1). |
| NFR-6 | Performance | The summary is ready about 2 hours after the lesson. | Measured: 66.5 s of processing per minute of recording (section 6). |
| NFR-7 | Performance | A review of one repository takes under a minute. 20 requests can be sent per day: one per repository, plus one for the class comparison. | Measured: 21.8 s per request. The free quota is 20 requests per day (section 7). |
| NFR-8 | Reliability | A comment written with no network is not lost. | Tested: it arrives after the network returns, even after the browser is closed (section 1). |
| NFR-9 | Privacy | The class photo and the recording never leave the lecturer's computer. No face recognition is done. | Design (D8). |
| NFR-10 | Privacy | The real course list and the sheet with names are kept only on the lecturer's computer. Tests use invented data. In the live demo, students check in with their real course email, so emails reach Firestore for the length of the lesson only. The phones cannot read check-ins, and the lesson's data is deleted from the cloud after the lesson (FR-1.5). Comments and poll answers are anonymous. | Design (D30, D37, D49). |
| NFR-11 | Privacy | Only two kinds of text are sent to the Gemini API: public repositories, under anonymous names, and a lesson transcript, only after the lecturer confirms. On the free tier, Google uses the content to improve its products. | Accepted (D38, D42). |
| NFR-12 | Security | The database rules allow only the fields each record needs, with the server time. They never allow a client to update or delete, and never allow a phone to read check-ins: only Python reads them. Everything else is blocked. | Tested on the test collection (section 1). |
| NFR-13 | Security | The service account key and the two Gemini keys (one for the review, one for the summary, each in its own Google project) are kept in `secrets/`, which is blocked by `.gitignore`. They never enter git. | Checked before each commit. |
| NFR-14 | Cost | Running the system costs nothing. | Free plans only. |
| NFR-15 | Portability | The student page works in a phone browser. | Tested on an iPhone with Chrome. Android was not tested. |

## 5. Data requirements

| Data | Where it is kept | Content |
|---|---|---|
| Course list | The lecturer's computer | Name, email, group |
| Lesson | Firestore | Date, server time, the comment mode |
| Rotating codes | Firestore, under the lesson | The code, and the server time at which it was shown |
| Check-ins | Firestore, under the lesson | The email, the code, and the server time |
| Challenge answers | Firestore, under the lesson | The email, and the box number or "not in the photo" |
| Comments | Firestore, under the lesson | The text and the server time, with no email |
| Polls and answers | Firestore, under the lesson | The question, the options and the duration; each answer with the server time, and no email |
| Class photos and their boxes | The lecturer's computer | The photos and the counts |
| Attendance sheet | The lecturer's computer (`.xlsx`) or Google Sheets | Name, email, group, and the status per lesson. The comments are in a separate tab. |
| Recordings, transcripts, summaries | The lecturer's computer | Files |
| Bundles, the name-to-link key, the reviews | The lecturer's computer | Files, plus the ranking sheet and the class comparison |
| A poll answered on this phone | The student's phone | A mark per poll, with no answer and no email |

## 6. Traceability

Every requirement links to a use case and to the tools report section where its tool was tested. The tests of the system itself are defined in the testing strategy (step 9).

| Requirements | Use case | Tool tested in the tools report |
|---|---|---|
| FR-1.x | UC-1 | Section 4: reading the participant list with openpyxl |
| FR-2.x | UC-2 | Section 1: Firestore and the page; section 2: the rotating code |
| FR-3.x | UC-3 | Section 3: YOLO26 and the double-count rule |
| FR-4.x | UC-4 | Built on sections 2 and 3 |
| FR-5.x | UC-5 | Section 3: the boxes; section 2: the window |
| FR-6.x | UC-6 | Section 4: `.xlsx` and Google Sheets |
| FR-7.x | UC-7, UC-8 | Section 1: real time and no network; section 4: the sheet |
| FR-8.x | UC-9, UC-10, UC-11 | Section 1: real time; section 5: Google Forms as a comparison |
| FR-9.x | UC-12 | Section 6: faster-whisper and the summary; section 7: the Gemini API |
| FR-10.x | UC-13 | Section 7: the bundles and the Gemini API |
| NFR-1 to NFR-15 | All | See the evidence column in section 4 |
