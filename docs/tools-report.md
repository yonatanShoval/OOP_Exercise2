# Tools Report

## Purpose and method

This report tests, in real life, the tools proposed for the project. Every tool in this report was tried hands-on, and each section shows what was done and what came out.

Criteria: simplicity, cost (free plans only), works from a phone, privacy.

Test environment:
- Phone: iPhone, Chrome, cellular network with Wi-Fi off. Android was not tested.
- Computer: Windows 10 Pro, version 22H2, Chrome, Python 3.14.0, Node.js 24.18.0.

## 1. Infrastructure: Firebase, HTML/JS and Python

### Tools

| Tool | Version | Role |
|---|---|---|
| Firebase Firestore | Standard edition, region `me-west1`, production mode | Real-time database, keeps messages sent without a network |
| Firebase Hosting | | Public URL for the phone page |
| Firebase JS SDK | 13.4.0 (from the CDN) | Connects the page to Firestore |
| HTML/JS | | Thin phone page, no framework and no build step |
| Firebase Admin SDK for Python | `firebase-admin` 7.8.0 | Python reads the same data |
| Firebase CLI (`firebase-tools`) | 15.37.0 | Publishing the page and the rules |

Test code: `tools-tests/01-infrastructure/`
- `public/index.html`, `public/app.js`: the phone page
- `firestore.rules`: security rules
- `python/listen_messages.py`: Python listener

Live page: https://oop-exercise2.web.app

### Setup

- Free Firebase plan (Spark).
- Security rules allow only reading and adding messages in one test collection. A message must have fixed fields and 1 to 200 characters of text. Editing and deleting are blocked, and every other collection is closed.
- Python connects with a service account key. The key is kept in a folder that is blocked in `.gitignore` and never enters the repository.

### Free plan limits

From the official Firebase pricing page (https://firebase.google.com/pricing), Spark plan. The page states: "No payment method needed."

| Service | Limit |
|---|---|
| Firestore (Standard edition): stored data | 1 GiB total |
| Firestore (Standard edition): network egress | 10 GiB/month |
| Firestore (Standard edition): document writes | 20K writes/day |
| Firestore (Standard edition): document reads | 50K reads/day |
| Firestore (Standard edition): document deletes | 20K deletes/day |
| Hosting: storage | 10 GB |
| Hosting: data transfer | 360 MB/day |

### Results

| # | Test | Result |
|---|---|---|
| 1 | The page opens on a real phone over a cellular network | **Pass.** The page shows `Device: phone` and `Network: Online`. |
| 2 | A message from the phone appears in the computer browser in real time | **Pass.** Phone: saved after 0.88 s. Computer browser: 3.76 s. |
| 3 | The Python script receives the phone message in real time | **Pass.** 3.64 s. |
| 4 | A message sent with no network waits and is sent when the network returns | **Pass.** In airplane mode the page shows `Offline` and the message is marked pending. Nothing appears on the computer. Phone: saved after 49.54 s. Computer browser: 52.58 s. |
| 5 | The Python script receives the message sent with no network | **Pass.** 52.57 s. |
| 6 | A pending message survives closing the tab and the browser | **Pass.** Before the page was reopened, nothing appeared on the computer. After reopening it with a network: phone 75.20 s, computer browser 78.23 s, Python 78.22 s. |

### About the numbers

- The phone's delay uses one clock, so it is accurate.
- The computer's delay compares the phone's clock with the computer's clock. The difference between the phone and the computer was 2.88 s, 3.04 s and 3.03 s in tests 2, 4 and 6. The difference is constant, so most of it is probably a clock difference and not slowness.
- In tests 4, 5 and 6 the delay includes the time the phone had no network.

### Limitations and difficulties

- Only iPhone with Chrome was tested. Android was not tested.
- The page itself does not load without a network, because there is no Service Worker. Whether the app must open without a network is an open question for the SRS.
- The assignment says comments work "in real time / offline". In class, the lecturer explained that comments during the lesson are allowed only if the lecturer allows them, and otherwise only "offline". From the context, offline means after the lesson, not without a network. Testing without a network is therefore our addition, not a requirement.
- Anyone can read the test messages, and there is no limit on how many can be added. Test messages contain no personal information. The real system will need authentication.
- The first offline attempts were discarded: the iPhone may have turned Wi-Fi back on automatically when airplane mode was switched. The tests were repeated with Wi-Fi off the whole time.
- On Windows, the Firebase CLI sometimes prints an internal error when it closes (`Assertion failed ... src\win\async.c`). It happened after `firebase login` and after a read-only command. In both cases the command had already finished its work: the login was saved and the output was complete. Publishing was not affected.

### Conclusion

Firebase covers real time, sending after the network returns, and hosting the page with one free platform. Python reads the same data in real time through the Admin SDK, so the system's logic can be written in Python while the phone page stays thin HTML/JS.

## 2. Check-in: rotating QR code

### Tools

| Tool | Version | Role |
|---|---|---|
| `qrcode` for Python, with Pillow | `qrcode` 8.2, Pillow 13.0.0 | Creates the QR image |
| tkinter | 8.6 (comes with Python) | Shows the code in a window on the computer |
| Firebase Hosting | | The check-in page that the phone opens |

Test code:
- `tools-tests/02-checkin/python/rotating_qr.py`: creates and rotates the code
- `tools-tests/01-infrastructure/public/checkin.html`: the check-in page

Live page: https://oop-exercise2.web.app/checkin.html

### Setup

- Every 10 seconds the script creates a new random token, builds a link to the check-in page with the token, and shows the link as a QR code. The token contains no personal information.
- The check-in page only shows the token from the link and the time it was opened. It does not save anything. Saving and validating check-ins will be designed in the SRS.
- 10 seconds is a test value. The final value will be decided in the SRS.

### Results

Phone: iPhone, built-in camera app, cellular network with Wi-Fi off.

| # | Test | Result |
|---|---|---|
| 1 | The iPhone camera scans the code and opens the check-in page | **Pass.** The code on the phone matched the code on the screen and in the terminal (checked by eye, the codes were not recorded). |
| 2 | The code changes | **Pass.** After a change, a second scan gave a different code, matching the new code on the screen. |
| 3 | Scan time | **Pass, not measured exactly.** Every scan finished before the code changed, so in less than 10 seconds. |
| 4 | Distance | **Pass** from 1, 3 and 5 meters, from a laptop screen. |

### Timing of the rotation

- In one run, the terminal log showed 33 changes from 21:28:19 to 21:33:53: 334 seconds, 10.12 seconds on average.
- The cause: `root.after(1000, ...)` waits one second after each tick's work is done, so small delays add up.
- The average is the evidence for this drift. The log shows whole seconds only, so the single gaps of 11 seconds are partly rounding.
- In a real system, a code's validity must be checked by the server's time, not by the window's timer.

### Limitations

- Tested on a laptop screen, not on a classroom projector.
- Only iPhone with the built-in camera app was tested. Android was not tested.
- Scan time was not measured exactly.
- A rotating code makes copying harder but does not prevent it: a video call or a forwarded link can bypass it. It will be combined with the head count from the class photo, and in a real system with a login for each student.

### Conclusion

The Python `qrcode` library creates codes that the iPhone camera reads in less than 10 seconds from up to 5 meters on a laptop screen, with no app to install. The rotation works, but the timing of a code must not depend on the window's timer.

## 3. Head count: YOLO26 (Ultralytics)

### Tools

| Tool | Version | Role |
|---|---|---|
| Ultralytics (Python package) | 8.4.216 | Runs the model |
| YOLO26n (`yolo26n.pt`) | weights 5.3 MB | Small, fast model |
| YOLO26x (`yolo26x.pt`) | weights 113.2 MB | Large, slower model |
| PyTorch | 2.15.0, CPU only | Used by Ultralytics |

The original plan was YOLOv8. Before installing, the official documentation was checked. It says: "Start with YOLO26 for a new project: it is the latest Ultralytics release." (https://docs.ultralytics.com/models/). The documentation also says YOLO26 improves detection of small objects, which matters for the far rows of a lecture hall.

Test code:
- `tools-tests/03-headcount/python/count_people.py`: counts people with one model setting
- `tools-tests/03-headcount/python/save_all_boxes.py`: runs YOLO26x @ 1280 once and saves all boxes
- `tools-tests/03-headcount/python/apply_rule.py`: applies the double-count rule to the saved boxes
- `tools-tests/03-headcount/python/draw_thin_boxes_conf.py`: draws the saved boxes thin, with confidence, and marks the boxes the rule changed

### Setup

- 16 photo files from the lecturer, from four lessons: 7/11 (p1 to p3), 8/11 (p11 to p15), 11/11 (p21 to p24), 19/11 (p31 to p34). p12 and p15 are the same file (identical SHA-256), so there are 15 different photos. The photos are not in the repository and never leave the computer.
- Only the class "person" is counted. Confidence threshold: 0.25 (the default).
- Two settings of the same tool: YOLO26n at image size 640, and YOLO26x at image size 1280.
- Privacy: Ultralytics usage analytics are turned off with `settings.update({"sync": False})`. According to the Ultralytics privacy page, "Ultralytics does not collect, process, or view any training or inference images." `sentry-sdk` is not installed, so no crash reports are sent.
- The model weights were downloaded once from the official Ultralytics GitHub releases. They are not in the repository.
- The package `ultralytics-platform` was installed as a dependency. It is not used, and no Ultralytics account was connected.

### Results: accuracy

Manual count rule: every person of whom any part is visible, if it is clearly a separate person. The lecturer is not in the photos.

| Photo | Manual | YOLO26x @ 1280 | Difference | YOLO26n @ 640 | Difference |
|---|---|---|---|---|---|
| p1 | 38 | 39 | +1 | 7 | −31 |
| p11 | 44 | 45 | +1 | 12 | −32 |
| p21 | 43 | 43 | 0 | 10 | −33 |
| p31 | 46 | 46 | 0 | 11 | −35 |
| **Total** | **171** | **173** | **+2** | **40** | **−131** |

### Results: run time and offline run

| | YOLO26n @ 640 | YOLO26x @ 1280 |
|---|---|---|
| Average time per photo (CPU) | 99 ms | 5,256 ms |

Offline: with the computer disconnected from the internet (checked in a browser first), YOLO26n @ 640 counted p1 again with the same result (7). No message, warning or error appeared, and nothing was downloaded. YOLO26x was not tested offline.

### Visual check

- The boxes were redrawn thin and without labels, because the default labels hid people in the far rows.
- In p1 and p11, the extra box of YOLO26x (the one with the lowest confidence: 0.31 and 0.36) contains only the legs of a student who was already counted. The desk separates the upper body from the legs, and the model detected the two parts as two people. This explains the +1 in both photos.
- No person without a box was found in p1 or p11.
- p21 and p31 were not checked visually. A difference of 0 does not prove that every box is correct: a missed person and an extra box can cancel each other out.

### A rule against double counting

The lecturer does not change the way the photos are taken, so the fix must be in software. A rule was added on top of the model's boxes (the model is not changed):

- **Part 1, merge:** two boxes are one person if the horizontal overlap is at least 80% of the narrower box, at least 80% of the smaller box's area is inside the larger box, and the top edges differ by at most 20% of the smaller box's height. The last condition is relative to the box height, not a fixed number of pixels, because boxes in the far rows are small.
- **Part 2, drop:** a box is not counted if it is at least 1.5 times wider than tall, its center is in the bottom third of the photo, and its confidence is below 0.40 (a legs-only box).

The first version of the rule merged two boxes that were two different people (in p13 and p23), found in a visual check. The top-edge condition was added and the legs threshold was changed once, and then the tuning was stopped. In p24, the visual check confirmed that both merges were correct: three boxes of one student, and two boxes of another student in a far row. After the corrected rule, every change it made in all photos was checked visually and found correct: 12 merges (not counting p15, the copy of p12), each of one person, and 2 dropped boxes (in p1 and p24), each with the legs of a student who was already counted. In p13 and p23, the students that the first version merged by mistake are now counted separately.

| Lesson | Photo | YOLO26x @ 1280 | After the rule | Manual |
|---|---|---|---|---|
| 7/11 | p1 / p2 / p3 | 39 / 39 / 25 | 38 / 38 / 25 | 38 / – / – |
| 8/11 | p11 / p12 / p13 / p14 | 45 / 31 / 30 / 43 | 44 / 30 / 28 / 40 | 44 / – / – / – |
| 11/11 | p21 / p22 / p23 / p24 | 43 / 43 / 38 / 41 | 43 / 43 / 38 / 38 | 43 / – / – / – |
| 19/11 | p31 / p32 / p33 / p34 | 46 / 46 / 47 / 47 | 46 / 46 / 46 / 46 | 46 / – / – / – |

(p15 is the same file as p12 and is not shown.)

After the rule, all four manually counted photos match the manual count. **All thresholds of the rule were set after seeing the errors in these photos, so there is a risk of overfitting.** The real test will be on new photos, in the demo.

Photos of the same lesson still give different counts (for example 28 to 44 on 8/11). This does not come from the desk. Combining several photos of one lesson without counting a student twice is an open question for the SRS.

### Limitations

- The manual count was done after the model's results were already seen, which may have influenced it.
- Only 4 photos were counted by hand, by one person.
- Only the CPU was used. A GPU was not tested.

### License

Ultralytics YOLO is licensed under AGPL-3.0 (https://www.ultralytics.com/license). According to the license page, using YOLO code or models means you "must either: Open-source your entire project under AGPL-3.0, or Obtain an Ultralytics Enterprise License." The free option was chosen: this repository is public, and a `LICENSE` file with the AGPL-3.0 text was added to it.

### Conclusion

YOLO26x at 1280 was within 0 to 1 of the manual count on all four checked photos, in about 5 seconds per photo on a regular CPU, fully on the local computer. YOLO26n at 640 is about 50 times faster but found only about a quarter of the people, so it is not suitable for a lecture hall of this size. The main error was a student split in two by the desk. A simple rule on the boxes fixed it in these photos, but its thresholds still need to be tested on new photos.

## 4. Attendance sheet: openpyxl and Google Sheets

### Tools

| Tool | Version | Role |
|---|---|---|
| openpyxl | 3.1.5 | Writes an .xlsx file on the computer, no network needed |
| gspread, with the Google Sheets API | 6.2.1 | Writes to a Google Sheet online |

Test code:
- `tools-tests/04-spreadsheet/python/make_xlsx.py`: builds the .xlsx file
- `tools-tests/04-spreadsheet/python/write_google_sheet.py`: writes to the Google Sheet and reads it back

### Setup

- **.xlsx (offline):** the script reads the lecturer's participant list and writes a new attendance sheet with first name, last name, group and one lesson column. The email column is not copied. The attendance marks are invented and the column is labeled "TEST DATA". The participant list and the output file stay outside the repository.
- **Google Sheets (online):** only invented data (Student 01 to Student 10). The real participant list is never sent to the cloud.
- **Access:** the script uses the existing Firebase service account key. The sheet is shared with the service account's email as an editor. The Google Sheets API had to be enabled in the Google Cloud project first.

### Free plan limits

From the Google Sheets API usage limits page:
- "All standard use of the Google Sheets API is available at no additional cost."
- Read requests: 300 per minute per project, 60 per minute per user per project. Write requests have the same limits.
- The page says charges for going over the limits are planned for later in 2026.

### Results

| # | Test | Result |
|---|---|---|
| 1 | Build an .xlsx file from the participant list | **Pass.** 104 students, 84 marked present (invented). Two students have an empty group cell, as in the source file. The file opened correctly in Excel, without an email column. |
| 2 | Write to a Google Sheet and read it back | **Pass.** 10 invented students written in 3.36 s, including login. The 10 rows read back matched exactly. The rows were also checked by eye in the sheet itself. |

### Limitations and difficulties

- The first run of `make_xlsx.py` crashed: when the last cells of a row are empty, the row comes back shorter. Fixed by padding short rows.
- The first Google Sheets run failed with "404: Requested entity was not found". The cause was the link: it was typed by hand from a screenshot, and it had a lowercase "l" in place of a capital "I" in two places. A link copied straight from the browser worked. The lesson: copy links straight from the browser. A 404 here can mean either a wrong link or a sheet that was not shared.
- Only one small write was tested. The quota was not tested.

### Conclusion

openpyxl creates an attendance file that opens in Excel with no network and no account. gspread writes the same kind of table to Google Sheets in a few seconds with the existing service account. Real student data stays only in the local file.

## 5. Existing poll tool: Google Forms

### Purpose

The README says that current teaching tools are too complicated to use quickly in class. This test measures one existing tool, Google Forms, from both sides: how long it takes the lecturer to create a one-question poll, and how long it takes a student to answer it on a phone.

### Setup

- One multiple-choice question, no personal details.
- Settings: "Collect email addresses" off and "Limit to 1 response" off, so that no Google sign-in is required.
- The link was sent to the phone over WhatsApp.
- Phone: iPhone, Chrome, cellular network with Wi-Fi off.
- Times were read from screen recordings, frame by frame, to about 0.5 s.

### Results

| # | Test | Result |
|---|---|---|
| 1 | Create the form, first time (including learning the tool) | 6:03 min |
| 2 | Create the form, second time | 1:21 min |
| 3 | Answer on the phone, Chrome signed in to a Google account | **Pass.** 3 taps (the link, an answer, Submit), about 7 s from tapping the link to the confirmation. Loading took about 2.5 s. |
| 4 | Answer on the phone, Chrome incognito, no account (like a student without Google) | **Pass.** No sign-in was required. After the form loaded: 2 taps (an answer, Submit), the same as test 3 without the tap on the link. Loading took about 1 s. Total time not reported: the recording had about 4 s with no action. |
| 5 | The answers reach the lecturer | **Pass.** The responses tab showed 3 responses: the two tests and one earlier try before the recordings. |

### Notes

- **An extra step for the lecturer:** the form must be published. Before that, a student who opens the link sees that the form is not published.
- In test 3, the signed-in account's email was shown at the top of the form but was not collected.
- In test 4, Google only suggested signing in to save progress. It was not required.
- In test 4 the link was pasted into the incognito window. These taps are not counted, because a real student opens the link directly.
- No other obstacles appeared.

### Limitations

- One question and one phone. Android was not tested.
- In test 4, the total time was not measured.
- The time for the lecturer to send the link to a whole class was not measured.

### Conclusion

For the student, Google Forms is fast: about 7 seconds and 3 taps, with no sign-in. The cost is on the lecturer's side: even after learning the tool, creating and publishing a one-question poll took over a minute, and the link still has to reach the students. A quick poll in our app should therefore focus on the lecturer: opening a question in a few seconds, on a page the students already have open.

## 6. Lecture summary: Whisper (local) and Claude (chat)

### Tools

| Tool | Version | Role |
|---|---|---|
| faster-whisper | 1.2.1 | Transcribes the recording on the computer |
| Whisper model `large-v3-turbo` | int8, 1,547 MB on disk | The speech-to-text model (not `large-v3`) |
| PyAV | 18.1.1 | Reads the audio from the video file (comes with its own FFmpeg) |
| Claude (chat, free) | | Summarizes the transcript, by hand |

Test code: `tools-tests/06-transcription/python/transcribe.py`

### Setup

- **Why faster-whisper:** the original `openai-whisper` needs the `ffmpeg` command-line tool installed separately. faster-whisper reads audio through PyAV, which includes FFmpeg, so nothing else had to be installed.
- **Model:** one model only, `large-v3-turbo`, to save time. Language set to Hebrew. CPU only.
- **Computer:** Intel Core i3-1005G1, 7.8 GB RAM, no graphics card.
- **Clip:** 4:43 minutes of the lesson in which the lecturer explained this assignment (the part on features 2 and 3). Only the lecturer speaks in it.
- **Privacy:** the recording stays on the computer. Only the model weights are downloaded, once. The transcript was pasted into the Claude chat by hand, which is why a clip with only the lecturer was chosen. The recording, the transcript and the Zoom materials are not in the repository.
- **Measurement:** the script times model loading, audio decoding and transcription separately. It divides the transcription time by the clip length, and multiplies by the length of the full recording (01:33:52, from the Zoom summary) to estimate a whole lesson. The script prints only the timing numbers, not the transcript.

### Results

| # | Test | Result |
|---|---|---|
| 1 | Short check on a 5.7 s video | **Pass.** Model load 11.5 s, transcription 18.9 s. Too short to measure speed per minute: the model always processes at least a 30-second window. |
| 2 | Transcribe the 4:43 clip | **Pass.** Model load 12.5 s, audio decoding 1.1 s, transcription 314.0 s = **66.5 s of processing per minute of recording**. 89 segments. |
| 3 | Estimate for a full 93.9-minute lesson | **About 104 minutes**, a little longer than the lesson itself. |
| 4 | Summary in the Claude chat | **Pass.** Five points: free-text comments, maybe next to attendance, no emojis; the lecturer reads the comments of each lesson by hand; the lecturer decides if comments are allowed during the lesson or only after it; polls are started by the lecturer, multiple choice, closed after about two minutes, unlike comments, which the student starts; principles: simplicity, no invented features, a good metaphor. It also spotted a transcription error: "כהות" is probably "Kahoot". |

### Comparison with the Zoom summary

- Zoom's summary of the whole lesson caught the main points of this part, but missed five details: the lecturer's control over when comments are allowed, comments grouped by lesson, closing a poll, the difference between a comment and a poll, and the warning against inventing extra features.
- Zoom's summary also numbers the features incorrectly.
- Caveat: Zoom summarized an hour and a half, and we summarized five minutes. A short summary can naturally keep more detail.

### Comparison with Zoom's own transcript

- Whisper was better with English terms, and wrote the sentence quoted from the assignment correctly.
- But in the first 30 seconds Whisper wrote only "תודה רבה" ("thank you very much") and missed the opening. At the end it invented "תודה" four times over silence. This is a known problem of Whisper models on silence.
- Conclusion: a Whisper transcript must be checked before it is trusted.

### Problems and fixes

- **Version clash:** the first run failed with `TypeError: open() got an unexpected keyword argument 'metadata_errors'`. faster-whisper 1.2.1 passes this argument to PyAV, and PyAV 19.0.0 removed it ("Remove the `metadata_encoding` and `metadata_errors` arguments to av.open"). faster-whisper only asks for `av>=11`, so pip installed PyAV 19. **Fix:** pin `av==18.1.1` in `requirements.txt`.
- On Windows, the model download prints a warning that symlinks are not supported. The cache still works, and only uses more disk space.

### Limitations

- One clip of 4:43 minutes, one model, one computer. The estimate for a full lesson is linear, so silence and several speakers in a real lesson can change it.
- Filtering out silence before transcription (faster-whisper has a `vad_filter` option) may prevent the invented words, but it was not tested.
- In this test, the summary was made by hand in the chat. **Later decision:** in the system, the summary is automatic, through the Gemini API, after the lecturer confirms sending the transcript. The manual chat is only a backup. The Gemini call itself was tested in section 7, on the homework bundles, but not yet on a transcript.

### Conclusion

faster-whisper transcribes Hebrew locally with no separate installs, and handles English terms better than Zoom's transcript. On a regular laptop CPU it takes about as long as the lesson itself, so a summary will be ready about two hours after the lesson, not right at its end. The transcript can contain invented words over silence, so it must be checked. The Claude summary of the clip kept details that the Zoom summary missed.

## 7. Homework review: Claude (chat) and the Gemini API

### Tools

| Tool | Version | Role |
|---|---|---|
| git | | Downloads each repository (`git clone --depth 1`) |
| `bundle_repo.py` (our script) | | Packs each repository into one text file |
| Claude (chat) | | Reviews and compares the two repositories, by hand |
| Gemini API, free tier | `gemini-4-hydrogen`, `gemini-3.5-flash-lite` | The same review, sent automatically from Python |
| `google-genai` | 3.6.1 | The Python library for the Gemini API |

Test code:
- `tools-tests/07-homework-review/python/bundle_repo.py`: packs one repository, or a whole list of repository links (`--list`)
- `tools-tests/07-homework-review/review_prompt.md`: the review request, exactly as sent
- `tools-tests/07-homework-review/python/gemini_review.py`: sends the request and the bundles to the Gemini API. It takes the model name as a parameter, saves the answer outside the repository, and prints the time and the token counts.

### Setup

- **Repositories:** two public Ex1 submissions from the lecturer's list. In this report they are called **Repo A** and **Repo B**, with no names or links, because comparisons are anonymous.
- **Criteria:** taken from the Ex1 assignment: the to-do list, the implementation requirements, the plane definition (|dist(a,b) − dist(a,c)| < 0.001), invalid input (an exception, and an error frame in the demo), and the submission rules.
- **Focus:** the review looks mainly at the text, meaning the README and the documentation: do they cover the requirements, the algorithm, and how to run? It also ranks the repos. It supports a human grader and does not replace one.
- **Why a bundle:** the chat cannot read a GitHub repository by itself. The script writes the full file tree with sizes (data files are listed, not included), then the text files, most important first: the README, the main documents, `Ex0.py`, the main code, the other documents, the tests, and the helper scripts. It stops at a character budget and lists the files that did not fit. The request tells the reviewer not to treat those files as missing.
- **Input and output:** with `--list`, the script reads a file with one repository link per line, and writes one bundle per link, named Repo A, Repo B and so on. The key from name to link stays outside the repository.
- **Why also an API:** the lecturer wants a machine that goes through all the submissions. A hundred manual pastes into a chat do not meet that. So we also tested the Gemini API, which has a free tier.
- **Gemini setup:**
  - An API key from Google AI Studio, in a separate Google project used only for the review, so that its quota is not shared with other uses.
  - The key is kept in `secrets/`, which is blocked by `.gitignore`.
  - The exact model names were taken from the list the library returns (`client.models.list()`) and match the version the API reports in each answer.
- **Free tier limits** (from the AI Studio limits page, per project):

| Model | Requests per minute | Tokens per minute | Requests per day |
|---|---|---|---|
| `gemini-4-hydrogen` | 5 | about 250K | 20 |
| `gemini-3.5-flash-lite` | 15 | about 250K | 500 |

Most other models show a limit of 0, which means they are not available on the free tier. On the free tier, Google uses the content to improve its products. We accept this here, because the repositories are public and are sent under anonymous names.

### Results: Claude (chat)

| # | Test | Result |
|---|---|---|
| 1 | Download both repositories | **Pass.** 27.9 s for both. |
| 2 | Pack them | **Pass.** Repo A: all 18 text files, 110,254 characters. Repo B: 25 of 62 text files, 155,849 characters. Its 13 test files, the data-generation and tool scripts, the raw experiment results and `docs/DATA.md` were left out. |
| 3 | Attach both bundles in the chat and send the request | **Pass.** Both files were accepted, and the answer took 65 s. |
| 4 | The answer | **Pass.** For each repo: a table with each to-do item and requirement, then strengths and weaknesses of the documentation, each with a file name. Then a comparison by topic, a ranking (Repo B documented better, Repo A second, with reasons), and what each repo could learn from the other. It said "not visible in the bundle" where it could not check, for example the commit history and the real fps. |
| 5 | Check three of its claims against the code (read only) | **3 of 3 correct.** (1) In Repo B, unequal legs of the triangle only give a warning, at a tolerance of 0.5 voxels (`plane_projection/geometry.py`). (2) In Repo A, `_validate` rejects legs that differ by more than 0.001, so a difference of exactly 0.001 is accepted, while the assignment requires less than 0.001 (`src/projection.py`). This matters only at the exact boundary. (3) Repo B's SRS cites a `test_video` test file that does not exist in the repository (`docs/SRS.md`). |

### Results: Gemini API (automatic)

The same request and the same two bundles were sent to each model, once.

| | `gemini-4-hydrogen` | `gemini-3.5-flash-lite` |
|---|---|---|
| Time | 21.8 s | 14.0 s. The first try failed with an error 503: the model was under high demand. The second try passed. |
| Tokens | 91,136 in, 2,215 out, and 2,279 thinking | 91,748 in, 2,050 out |
| Claim 1: Repo B's tolerance is 0.5, and it only warns | **Found**, in three places in the answer | **Missed.** It marked Repo B's invalid-input handling as "done". |
| Claim 2: Repo A accepts a difference of exactly 0.001 | Missed | Missed |
| Claim 3: Repo B's SRS cites a test file that does not exist | Missed, although the full file tree was in the bundle | Missed |
| Speed (30 / 100 fps) | "Not visible in the bundle", as the request asks | **Invented:** "done" for both repositories, with no way to check it from the bundle |
| A new claim | Repo A's loader does not check the voxel type or the size limits. **Partly correct:** we checked `src/io_utils.py`, and these checks are indeed missing. But its SRS does not promise them, so "claims ... that ... does not enforce" overstates it. | None |
| Ranking | Repo B first, as in the chat | Repo B first, as in the chat |
| Length | 1,065 words. The request asked for under 900. | 1,151 words. The request asked for under 900. |

**In short:** Claude in the chat found 3 of 3 claims. Hydrogen found 1. Flash Lite found 0, and it invented a result. Each model ran only once, so these numbers are a single sample.

**What the limits mean:** one repository is about 45,000 tokens.
- **Hydrogen:** 20 requests per day, so 20 submissions per day. A hundred submissions take about five days.
- **Flash Lite:** a hundred submissions would fit in one day.

### Problems and fixes

- **An unfair first bundle:** with a budget of 100,000 characters, Repo B's long documents filled the bundle and its main code was left out, while Repo A's code was in. **Fix:** the main code is now packed before the other documents, and the budget is 150,000 characters per repository.
- **Error 503 from Flash Lite:** the model was under high demand. One retry, soon after, passed. A real run needs to retry.

### Limitations

- Two repositories, one run per tool, and three claims checked. The rest of the reviews was not verified.
- Repo B's tests were not in its bundle, so the review could not judge them. A larger repository will lose more files.
- The bundles do not include the address of the repository itself. So the review's point that Repo A shows "no public repo link" may come partly from our packing, not only from the repository.
- The bundles are sent as they are, to the chat or to the API. These are public repositories, but any names in the files reach the service. On the Gemini free tier, Google also uses them to improve its products.
- Only the time and the tokens of one request per model were measured. The time to get an API key was not measured.
- Both Gemini answers were longer than the request allowed.

### Conclusion

Claude, with a simple packing script, produced a structured, anonymous review and ranking of two submissions in about a minute, and all three claims we checked against the code were correct. The packing step matters: it decides what the reviewer sees, so it must be fair to every repository, and the review must say what it could not see.

The Gemini API makes the review automatic and free, but in our single run it found fewer problems than the chat. **Decision:** `gemini-4-hydrogen` is the main model. A review that invents results, like Flash Lite with the speed, does more harm than a slow review. When the daily quota runs out, the review continues the next day with the same model. It does not switch to another model, so that every submission is reviewed by the same model, and the comparison and the ranking stay fair. The model name is a parameter of the Gemini engine. The manual chat stays as a backup. Every review supports a human grader and does not replace one.

## 8. Summary

| Need | Tool chosen | What worked | What did not work, or was not tested | Conclusion for the design |
|---|---|---|---|---|
| Real time, offline, hosting | Firebase (Firestore + Hosting), free plan | Phone to computer in real time. A message sent with no network waits on the phone and arrives later, even after the browser is closed. | The page itself does not load with no network. Only iPhone was tested. | One platform for comments and polls. Python reads the same data. |
| Phone page | Plain HTML/JS | Opens on a real phone with no app. | | The phone only shows and sends. The logic stays in Python. |
| Check-in | `qrcode` + tkinter (Python) | The iPhone camera scans in under 10 s, from up to 5 m. | The window's timer drifts. Not tested on a projector. | A rotating code is an addition. A code's validity must use the server's time. |
| Head count | YOLO26x @ 1280, local | Within 0 to 1 of the manual count, about 5 s per photo, with no cloud. A rule fixed students split by the desk. | YOLO26n missed about three quarters of the people. The rule's thresholds were set on these photos. | Count people, do not recognize them. The real test is on new photos. |
| Attendance sheet | openpyxl (.xlsx) and gspread (Google Sheets) | An offline file that opens in Excel, and an online sheet written in a few seconds. | Only a small write was tested. | Real student data only in the local file. |
| Existing poll tool | Google Forms | About 7 s and 3 taps for the student, with no sign-in. | Over a minute for the lecturer to create and publish a poll. | Our polls should make the lecturer's side fast. |
| Lecture summary | faster-whisper (`large-v3-turbo`), local, + the Gemini API after the lecturer confirms. The Claude chat, used in this test, is the backup. | Hebrew transcribed locally, with English terms better than Zoom's transcript. The chat summary kept details that Zoom missed. | About 104 minutes of processing for a 94-minute lesson. Invented words over silence. A version clash with PyAV 19. Gemini not yet tested on a transcript. | The summary is ready about two hours after the lesson. The transcript must be checked, and is sent only with the lecturer's OK. |
| Homework review | Our packing script + the Gemini API (`gemini-4-hydrogen`, free tier). The Claude chat is the backup. | Claude chat: a review and ranking in about a minute, 3 of 3 checked claims found. Gemini: automatic and free, about 22 s per request. | Hydrogen found 1 of 3 claims, and Flash Lite found 0 and invented a result. One run per model. Hydrogen allows 20 requests per day. Large repositories lose files to the size budget. | List of links in, one report per link out, all with the same model. It supports a human grader and does not replace one. |

Every tool in this table was tested hands-on, as described in its section.

## Working with Claude Code

Notes collected during the tests of step 3.

### Vibe coding and find & compose

The heavy parts use existing tools: Firebase, `qrcode`, YOLO26, openpyxl, gspread, faster-whisper and Claude. This is "find & compose". Claude Code wrote the small code that connects them: the test pages, the listener, the rotating code, the double-count rule, the transcription timer and the packing script. This is "vibe coding". In every case the result was checked by a real test or by eye, and several mistakes were found that way (listed below).

### What worked well
- It proposed a plan and showed every change before saving it.
- It checked that the JS SDK version exists on the CDN and contains the functions the code uses, before using it.
- It checked with `git check-ignore` that the secret key folder is blocked before the key was downloaded.
- It checked how the `qrcode` image connects to tkinter before writing the code.
- At my request, it checked the Ultralytics documentation for the latest model, the license and the analytics setting before installing.
- It suggested redrawing the saved boxes for the visual check, without running the model again.
- It noticed that p12 and p15 had identical boxes, which led to finding that they are the same file.
- The plan first said 17 photos, a number from my message that was not counted. Claude Code counted the files, corrected it to 16, and later found that two of them are the same file.
- It checked both Whisper packages with `pip install --dry-run` before installing anything, to see that they work with Python 3.14.
- It read the video file's header and found that `m21.mp4` is 5.68 seconds long, not the lesson recording, with no extra tools.
- When the transcription failed, it found the cause in PyAV's changelog and explained it before fixing anything.
- It noticed that the first homework bundle left out one repository's main code, which would have made the comparison unfair, and fixed it before the review was run.
- It checked every transcript line number I cited against the saved file.
- The transcription script prints only timing numbers, not the transcript, because recordings can contain voices of students.

### What did not work well
- In step 1 it wrote facts about the class that were not in the assignment (an estimated number of students). I caught and removed them.
- In the first draft of `app.js` it used an old version of the JS SDK, 10.12.2. I asked it to check the latest version.
- It wrote in the code that pending messages survive "a page refresh" without testing it, and planned a refresh test without noticing that the page does not load without a network. The test was redesigned before it was run.
- It did not anticipate that the iPhone turns Wi-Fi back on automatically. I found it, and the tests were repeated.
- It did not anticipate that the window's timer drifts. The drift was found in the terminal log during testing.
- It used `2>&1` in the installation command, although its own instructions say not to do this in Windows PowerShell 5.1. This made a successful installation look like a failure.
- Its first version of the double-count rule merged two different people in p13 and p23. The visual check found it.
- The first `make_xlsx.py` crashed on rows that end early when the last cells are empty.
- It installed faster-whisper without pinning PyAV, so pip took a newer PyAV that breaks it. The first run failed.
- In a study note, it gave 0.88 s as the time for a message to reach the lecturer. That number is the time to save the message, measured on the phone. I asked it to check the report, and it corrected the note.
- Its first character budget for the homework bundles, 100,000 characters, was too small for one of the repositories.

### Lessons

- Every claim needs a source: the assignment, the official documentation, or a test that was actually run.
- A test is not passed until a person has looked at the result: the phone screen, the boxes on the photo, the sheet, the transcript.
- Pin the versions that matter, including dependencies of dependencies.
