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

## Working with Claude Code

Notes collected during the tests. This section will be completed at the end of step 3.

What worked well:
- It proposed a plan and showed every change before saving it.
- It checked that the JS SDK version exists on the CDN and contains the functions the code uses, before using it.
- It checked with `git check-ignore` that the secret key folder is blocked before the key was downloaded.

What did not work well:
- In step 1 it wrote facts about the class that were not in the assignment (an estimated number of students). I caught and removed them.
- In the first draft of `app.js` it used an old version of the JS SDK, 10.12.2. I asked it to check the latest version.
- It wrote in the code that pending messages survive "a page refresh" without testing it, and planned a refresh test without noticing that the page does not load without a network. The test was redesigned before it was run.
- It did not anticipate that the iPhone turns Wi-Fi back on automatically. I found it, and the tests were repeated.
