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
- The assignment says comments work "in real time / offline". Testing without a network is our interpretation, not an explicit requirement, and will be confirmed with the lecturer.
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

## Working with Claude Code

Notes collected during the tests. This section will be completed at the end of step 3.

What worked well:
- It proposed a plan and showed every change before saving it.
- It checked that the JS SDK version exists on the CDN and contains the functions the code uses, before using it.
- It checked with `git check-ignore` that the secret key folder is blocked before the key was downloaded.
- It checked how the `qrcode` image connects to tkinter before writing the code.
- At my request, it checked the Ultralytics documentation for the latest model, the license and the analytics setting before installing.
- It suggested redrawing the saved boxes for the visual check, without running the model again.
- It noticed that p12 and p15 had identical boxes, which led to finding that they are the same file.
- The plan first said 17 photos, a number from my message that was not counted. Claude Code counted the files, corrected it to 16, and later found that two of them are the same file.

What did not work well:
- In step 1 it wrote facts about the class that were not in the assignment (an estimated number of students). I caught and removed them.
- In the first draft of `app.js` it used an old version of the JS SDK, 10.12.2. I asked it to check the latest version.
- It wrote in the code that pending messages survive "a page refresh" without testing it, and planned a refresh test without noticing that the page does not load without a network. The test was redesigned before it was run.
- It did not anticipate that the iPhone turns Wi-Fi back on automatically. I found it, and the tests were repeated.
- It did not anticipate that the window's timer drifts. The drift was found in the terminal log during testing.
- It used `2>&1` in the installation command, although its own instructions say not to do this in Windows PowerShell 5.1. This made a successful installation look like a failure.
- Its first version of the double-count rule merged two different people in p13 and p23. The visual check found it.
