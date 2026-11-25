# Use Cases (Client Stories)

Ex2 in Introduction to Software Engineering (OOP, OOD), Ariel University.
Project: Web-based Teaching Tool.

Each use case is a client story, written as "As a ... I want ... so that ...". It has a happy path, step by step, and the edge cases. The requirements it covers are listed by their IDs in the SRS ([srs.md](srs.md)). Edge cases that are rare are left to the lecturer by design, and are not solved automatically.

## Actors

| Actor | Who | Uses |
|---|---|---|
| **Lecturer** | The course lecturer | The lecturer's window, on their computer and the projector |
| **Student** | A student in the classroom | Their phone browser, and for UC-13 also their own computer |
| **System** | Our software | The Python logic on the lecturer's computer, the phone page, Firestore |
| **External services** | Google Sheets, the Gemini API, an LLM chat | Called by the system or by the lecturer |

## Overview

| ID | Use case | Feature | Main actor | Requirements |
|---|---|---|---|---|
| UC-1 | Load the course list and open a lesson | Attendance | Lecturer | FR-1.x |
| UC-2 | Check in | Attendance | Student | FR-2.x |
| UC-3 | Take photos and count the class | Attendance | Lecturer | FR-3.x |
| UC-4 | Get a mismatch alert | Attendance | Lecturer | FR-4.x |
| UC-5 | Run a challenge | Attendance | Lecturer, Student | FR-5.x |
| UC-6 | Decide and write the attendance sheet | Attendance | Lecturer | FR-6.x |
| UC-7 | Write a comment | Comments | Student | FR-7.1–7.4 |
| UC-8 | Read comments and set when they are open | Comments | Lecturer | FR-7.3, 7.5, 7.6 |
| UC-9 | Open a poll | Polls | Lecturer | FR-8.1–8.3 |
| UC-10 | Answer a poll | Polls | Student | FR-8.3–8.5 |
| UC-11 | Close a poll and see the results | Polls | Lecturer | FR-8.6, 8.7 |
| UC-12 | Get a lecture summary | Summary | Lecturer, Gemini API | FR-9.x |
| UC-13 | Review homework | Homework review | Lecturer, Student | FR-10.x |

---

## Feature 1: Attendance

### UC-1: Load the course list and open a lesson

**Story:** As a lecturer, I want to load my course list once and open today's lesson, so that check-ins, comments and polls are saved under the right lesson.

**Preconditions:** the lecturer downloaded the course participant list as `.xlsx`. The lecturer's computer has a network.

**Happy path:**
1. The lecturer opens the window and loads the course list.
2. The system reads each student's first name, last name, email and group, and shows how many students it read.
3. The lecturer clicks "Open lesson".
4. The system creates a lesson record in the database, with the date and the server time.
5. The window shows that the lesson is open, with the buttons for check-in, photos, comments and polls.

**Edge cases:**
1. **The file is not a participant list** (a missing column or a different format): the system shows an error and loads nothing.
2. **A row with no email:** the system loads the row and shows a warning. That student cannot be matched to a check-in, so the lecturer will handle them in UC-6.
3. **The same email twice in the list:** the system shows a warning, and keeps one row.
4. **No network when opening the lesson:** the lesson cannot be created. The window says so, and the lecturer tries again.

**Outcome:** an open lesson, and a course list in memory on the lecturer's computer only.

### UC-2: Check in

**Story:** As a student, I want to mark myself present with my phone in a few seconds, so that class time is not spent on attendance.

**Preconditions:** a lesson is open (UC-1). The lecturer started check-in, and the rotating code is on the projector.

**Happy path:**
1. The student scans the code on the projector with the phone camera.
2. The phone opens the check-in page of this lesson.
3. The first time only, the student types their email, and the phone remembers it.
4. The student taps "Check in".
5. The phone sends the email, the code and the lesson. The database adds the server time.
6. The phone shows "Check-in received".
7. The system checks that the code was shown in the 20 seconds before the check-in, and that the email is on the course list. It accepts the check-in.
8. The window shows the number of accepted check-ins.

**Edge cases:**
1. **An old code** (for example, a photo of the code sent to a friend at home, used after more than 20 seconds): the system rejects the check-in, and the window shows how many were rejected.
2. **A fresh code passed to someone at home** (for example, in a video call): the code check passes. The head count and the challenge catch it (UC-4, UC-5). The lecturer said that cheaters do not worry him, because the count and the challenge are the check.
3. **An email that is not on the course list** (for example, a typo): the check-in is saved, and it becomes a mismatch (UC-4).
4. **The same student checks in twice:** counted once.
5. **Two students on one phone:** the second student changes the saved email and checks in. Both are counted.
6. **No network on the phone:** the check-in waits on the phone and is sent when the network returns. If more than 20 seconds have passed, the code is old, and the check-in is rejected. The student scans again.
7. **Check-in is stopped:** the page says that check-in is closed.
8. **A participant from Zoom:** out of scope. Only students in the classroom check in.

**Outcome:** an accepted check-in, saved under the lesson.

### UC-3: Take photos and count the class

**Story:** As a lecturer, I want to count the people in the class from a photo, so that I know if the number of check-ins is right, without checking each student.

**Preconditions:** a lesson is open. The lecturer took one or more photos of the class and saved them on the computer.

**Happy path:**
1. The lecturer adds the photos to the lesson in the window.
2. The system counts the people in each photo with the local model.
3. The rule merges two boxes of the same person into one.
4. The window shows the count of each photo, and the lesson's head count: the highest count.

**Edge cases:**
1. **The desk splits a student** into an upper body and legs: the rule merges the two boxes (D28).
2. **Several photos of the same class:** the lesson's count is the highest one, not the sum, so no one is counted twice.
3. **The same photo added twice:** the highest count does not change. This happened in the test: two of the lecturer's photos were the same file.
4. **Photos of different parts of the class:** the highest count would be too low. Summing such photos is out of scope. The lecturer takes photos of the whole class.
5. **A dark or blurry photo:** the count is low, and the gap shows as a mismatch. The lecturer looks and decides.
6. **People who are not students** (for example, a guest standing at the side): they are counted. The lecturer's target is ±10%, and the lecturer decides.

**Outcome:** a head count for the lesson. The photos never leave the lecturer's computer.

### UC-4: Get a mismatch alert

**Story:** As a lecturer, I want to be alerted when the attendance does not add up, so that I look only at the cases that need me.

**Preconditions:** check-ins were received (UC-2), and a head count exists (UC-3).

**Happy path:**
1. The system compares the number of accepted check-ins with the head count.
2. They differ, so the window shows a mismatch alert, with both numbers.
3. The lecturer looks at the alert, and decides whether to run a challenge (UC-5) or to decide directly (UC-6).

**Edge cases:**
1. **The numbers are equal:** no alert. The lecturer can still look at the details.
2. **More check-ins than people:** someone may have checked in from outside the class. The lecturer runs a challenge.
3. **Fewer check-ins than people:** some students did not check in, or there are guests. The lecturer can remind the class to check in, or decide directly.
4. **An email that is not on the course list:** a separate alert line, with the email. The lecturer decides in UC-6.
5. **Rare cases** that do not fit any rule: the system does not try to solve them. The lecturer decides by hand.

**Outcome:** the lecturer knows what needs a decision. The system decides nothing by itself.

### UC-5: Run a challenge

**Story:** As a lecturer, I want each checked-in student to point to themselves in the class photo, so that I can find who checked in without being in the room.

**Preconditions:** a mismatch alert (UC-4). The lesson is still running, because the photo is shown on the projector.

**Happy path:**
1. The lecturer starts the challenge in the window.
2. The window shows the photo with the highest count on the projector, with a number on each box.
3. Each checked-in student types the number of their own box on the phone, and sends it.
4. The lecturer closes the challenge.
5. The window lists the results:
   - boxes chosen by more than one student,
   - students who chose "I am not in the photo",
   - checked-in students who did not answer,
   - boxes that no one chose.

**Edge cases:**
1. **Several students choose the same box:** a mismatch. A human decides, not the system. The lecturer gave the example of eight people who all say they are the same figure.
2. **"I am not in the photo":** the model missed the student, so there is no box. The student chooses this option, and it becomes a mismatch for the lecturer.
3. **A student does not answer:** listed for the lecturer.
4. **A box that no one chose:** a person who did not check in, or a guest. Listed for the lecturer.
5. **A wrong number by mistake:** it shows up as a box chosen twice, or a box that no one chose, and the lecturer decides.
6. **An answer after the challenge is closed:** rejected.
7. **After the lesson:** no challenge is possible, because the photo is shown only on the projector. This is a deliberate trade-off for privacy: the photo is never sent to the phones or to the cloud.

**Outcome:** a short list of cases for the lecturer's decision.

### UC-6: Decide and write the attendance sheet

**Story:** As a lecturer, I want to settle the open cases and get the attendance as a spreadsheet, so that I have an accurate record.

**Preconditions:** a lesson with check-ins. Any mismatches and challenge results are listed.

**Happy path:**
1. The lecturer goes over each open case, and marks each student involved as present or absent.
2. The lecturer clicks "Write sheet", and chooses an offline `.xlsx` file or an online Google Sheet.
3. The system writes one row per student, with the name, email and group, and adds a column for this lesson with the status.
4. The window shows where the sheet was written.

**Edge cases:**
1. **A rare case**, like a student who was away for a long time: the lecturer decides by hand. The system does not try to solve it.
2. **No network:** the `.xlsx` file works with no network. Google Sheets waits until the network returns.
3. **A student who is not on the course list at all:** the lecturer adds them to the course list and loads it again.
4. **In tests and in the demo:** only invented data goes to Google Sheets.

**Outcome:** an attendance sheet, with one status per student for the lesson.

---

## Feature 2: Comments and suggestions

### UC-7: Write a comment

**Story:** As a student, I want to write a short comment or suggestion about the lesson, so that the lecturer knows what to explain again or what to improve, without me raising my hand.

**Preconditions:** a lesson is open, and comments are open for it (UC-8). The student has the lesson's page, from the code on the projector.

**Happy path:**
1. The student types a comment, for example "I did not understand the last example".
2. The student taps "Send".
3. The phone sends the comment with the lesson. The database adds the server time. No email is saved.
4. The phone shows "Sent".

**Edge cases:**
1. **Comments are open only after the lesson:** during the lesson, the page says that comments open after the lesson. The lecturer decides this, for example so that students do not play with their phones in class.
2. **No network:** the comment waits on the phone, and is sent when the network returns, even if the browser was closed in between.
3. **An empty comment, or more than 200 characters:** the page does not send it, and says why.
4. **The lecturer closed comments for the lesson:** the comment is rejected, and the page says so.

**Outcome:** an anonymous comment, saved under the lesson.

### UC-8: Read comments and set when they are open

**Story:** As a lecturer, I want to choose when students can comment, and see the comments of this lesson, so that I get feedback without distraction.

**Preconditions:** a lesson is open.

**Happy path:**
1. The lecturer sets the comments of this lesson to "open during the lesson", or "only after the lesson".
2. New comments appear in the window in real time.
3. At the end of the lesson, Python writes the lesson's comments to the "Comments" tab of the sheet, with the date, the time and the text.

**Edge cases:**
1. **The lecturer changes the setting during the lesson:** it applies to new comments from that moment.
2. **After the lesson:** comments stay open until the lecturer closes them. Late comments are written to the sheet when the lecturer asks.
3. **No comments:** the tab says that there were no comments for the lesson.

**Outcome:** the lecturer sees the comments, and has them in the sheet.

---

## Feature 3: Quick polls

### UC-9: Open a poll

**Story:** As a lecturer, I want to ask the class a quick question on the spot, so that I know if the material is understood.

**Preconditions:** a lesson is open.

**Happy path:**
1. The lecturer types one question and a few answer options in the window, and keeps the default duration of 2 minutes or changes it.
2. The lecturer clicks "Open poll".
3. The system saves the poll under the lesson.
4. The window shows a fixed QR code on the projector that opens the poll page.

**Edge cases:**
1. **No network on the lecturer's computer:** the poll cannot be opened. The window says so.
2. **The lecturer gives fewer than two options:** the window asks for at least two.

**Outcome:** an open poll, with a code on the projector.

### UC-10: Answer a poll

**Story:** As a student, I want to answer the poll in one tap, so that it takes me only a few seconds.

**Preconditions:** a poll is open (UC-9).

**Happy path:**
1. The poll appears on the student's phone, which already has the lesson's page open.
2. The student taps one option.
3. The phone sends the answer. The database adds the server time. No email is saved.
4. The phone remembers that it answered, and shows "Answer received".

**Edge cases:**
1. **The page is not open on the phone** (the tab was closed, or the poll came before the check-in): the student scans the fixed code on the projector, and the poll page opens.
2. **A second answer from the same phone:** the page blocks it. This stops double votes by mistake, but not cheating. For example, a different browser can answer again.
3. **The poll is already closed:** the answer is rejected, and the page says so.
4. **No network:** the answer waits on the phone. If the poll closes before it arrives, it is rejected.

**Outcome:** one answer from this phone, saved under the poll.

### UC-11: Close a poll and see the results

**Story:** As a lecturer, I want the poll to close by itself and show me the results, so that I can continue the lesson right away.

**Preconditions:** a poll is open.

**Happy path:**
1. The poll's time ends.
2. The system closes the poll. The database rejects new answers.
3. The window shows the number of answers for each option.

**Edge cases:**
1. **The lecturer closes the poll early:** the same as the end of time.
2. **No answers:** the window shows zero for each option.

**Outcome:** the results of the poll, in the window.

---

## Feature 4: Lecture summary

### UC-12: Get a lecture summary

**Story:** As a lecturer, I want a transcript and a summary of my recorded lesson, so that I have useful notes after the lesson.

**Preconditions:** the lecturer downloaded the class recording by hand from Zoom, Meet or Google Classroom. A free Gemini key for the summary in `secrets/`, from its own Google project.

**Happy path:**
1. The lecturer chooses the recording in the window.
2. The system transcribes it on the lecturer's computer. For a lesson of about an hour and a half, this takes about an hour and three quarters.
3. The system saves the transcript as a text file.
4. The window asks: "Send the transcript to Gemini for a summary?" It explains that the transcript may hold names and voices of students, and that on the free tier Google uses the content.
5. The lecturer clicks "OK".
6. The system sends the transcript through `ReviewEngine` to the Gemini API, and saves the summary next to the transcript.
7. The lecturer shares the summary with the students through the channel they already use, if they want to.

**Edge cases:**
1. **Silence in the recording:** the model may invent words, as in the test ("thank you", four times). The lecturer checks the transcript.
2. **The first seconds are missed:** in the test, the first 30 seconds were missing. The lecturer checks the start.
3. **A file type that cannot be read:** the window shows an error.
4. **The lecturer does not confirm** (for example, students' names appear in the transcript): nothing is sent. The transcript stays on the lecturer's computer. The lecturer can still use the manual backup and paste it into an LLM chat by their own choice.
5. **The daily free quota has run out:** the summary has its own Google project and key, with its own 20 requests per day, so the homework review does not use them up. One summary per day is enough. If the quota still runs out, the summary is sent the next day.
6. **The model is busy** (error 503): the system tries again, at most three times in all. After that, the window says that the summary failed, and the transcript stays.
7. **A summary screen for students:** out of scope. The transcript and the summary stay with the lecturer.

**Outcome:** a transcript and a summary on the lecturer's computer, about two hours after the lesson.

---

## Feature 5: Homework review

### UC-13: Review homework

**Story (lecturer):** As a lecturer, I want a machine that goes through all the submissions and reviews each one, so that I get a report per submission, a ranking, and a class comparison.

**Story (student):** As a student, I want to review my own repository before I submit it, so that I can fix problems in time.

**Preconditions:** a text file with one public repository link per line. A free Gemini key in `secrets/`.

**Happy path (lecturer):**
1. The lecturer chooses the links file in the window.
2. The system downloads each repository, and packs it into a bundle with an anonymous name (Repo A, Repo B, and so on).
3. Stage 1: for each bundle, the system sends the review request to the Gemini API (`gemini-4-hydrogen`). It saves one Markdown report per link, with a score for each criterion.
4. The system writes one sheet that ranks all the links by score.
5. Stage 2: the system sends one request with a short summary of each review, and saves the class comparison: where each submission stands, and what others did well.
6. The lecturer gives each student their own report, with the class comparison.

**Alternative path (student):**
1. The student runs the same script on their own repository link, with their own free key.
2. The student gets a stage 1 report. Stage 2 needs the whole course, so only the lecturer runs it.

**Edge cases:**
1. **A link that cannot be downloaded** (a private repository, or a wrong link): the report for that link says so, and the review continues with the next link.
2. **A large repository:** files that did not fit in the bundle are listed at its end. The review is told not to treat them as missing.
3. **The daily free quota runs out** (20 requests): the review stops, and continues the next day with the same model, so that every submission is reviewed by the same model.
4. **The model is busy** (error 503): the system waits and tries again, at most three times in all. After that, the submission is marked as failed, and the system continues with the next one.
5. **The Gemini API is not available:** the manual engine writes the request to a file, and the lecturer pastes it into a free LLM chat.
6. **The review misses a problem, or invents one:** every report says that it supports a human grader and does not replace one, and what it could not check.

**Outcome:** one report per submission, a ranking sheet, and a class comparison.
