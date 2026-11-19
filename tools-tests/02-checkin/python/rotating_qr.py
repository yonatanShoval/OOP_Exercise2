"""Check-in tools test: show a QR code that changes every 10 seconds.

Each code holds a link to the check-in page with a new random token.
The token is only displayed. It is not saved or validated: that is designed in the SRS.
"""
import secrets
import time
import tkinter as tk

import qrcode
from PIL import ImageTk

CHECKIN_URL = "https://oop-exercise2.web.app/checkin.html"
ROTATE_SECONDS = 10  # test value only; the real value is decided in the SRS

root = tk.Tk()
root.title("Check-in QR test")
root.configure(bg="white")
qr_label = tk.Label(root, bg="white")
qr_label.pack(padx=20, pady=20)
info_label = tk.Label(root, bg="white", fg="black", font=("Segoe UI", 20))
info_label.pack(pady=(0, 20))

current_image = None  # tkinter needs a reference to the image, or it disappears
token = ""
seconds_left = 0


def new_code():
    """Create a new random token and show its QR code."""
    global token, current_image, seconds_left
    token = secrets.token_urlsafe(6)  # random, contains no personal information
    url = f"{CHECKIN_URL}?t={token}"
    image = qrcode.make(url, box_size=12, border=4).get_image()
    current_image = ImageTk.PhotoImage(image)
    qr_label.configure(image=current_image)
    seconds_left = ROTATE_SECONDS
    print(f"{time.strftime('%H:%M:%S')}  new code: {token}")


def tick():
    """Runs every second: update the countdown and rotate the code when it reaches zero."""
    global seconds_left
    if seconds_left <= 0:
        new_code()
    info_label.configure(text=f"Code: {token}   ·   changes in {seconds_left} s")
    seconds_left -= 1
    root.after(1000, tick)


tick()
try:
    root.mainloop()
except KeyboardInterrupt:
    root.destroy()
    print("Stopped.")
