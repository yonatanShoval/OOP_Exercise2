"""Head count tools test: run YOLO26x @ 1280 once on all class photos and save every person box.

The boxes are saved to course-materials/headcount-output/ (not in git), so the
double-count rule (apply_rule.py) can be applied without running the model again.
Runs only on this computer; the photos never leave it.
"""
import json
from pathlib import Path

from ultralytics import YOLO, settings

REPO_ROOT = Path(__file__).resolve().parents[3]
PHOTOS_DIR = REPO_ROOT / "course-materials"
OUT_FILE = PHOTOS_DIR / "headcount-output" / "boxes-yolo26x-1280-all.json"
MODEL_FILE = Path(__file__).resolve().parents[1] / "models" / "yolo26x.pt"
PERSON_CLASS = 0  # "person" in the COCO classes

if settings["sync"]:
    raise SystemExit("Ultralytics analytics are on. Turn them off first: settings.update({'sync': False})")

model = YOLO(str(MODEL_FILE))
photos = sorted(PHOTOS_DIR.glob("p*.jpeg"), key=lambda p: int(p.stem[1:]))
data = {}
for photo in photos:
    result = model.predict(str(photo), imgsz=1280, conf=0.25,
                           classes=[PERSON_CLASS], device="cpu", verbose=False)[0]
    height, width = result.orig_shape
    data[photo.stem] = {
        "width": width,
        "height": height,
        "boxes": [{"conf": round(c, 4), "xyxy": [round(v, 1) for v in box]}
                  for c, box in zip(result.boxes.conf.tolist(), result.boxes.xyxy.tolist())],
    }
    print(f"{photo.stem}: {len(data[photo.stem]['boxes'])} boxes")

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text(json.dumps(data, indent=1), encoding="utf-8")
print(f"Saved to {OUT_FILE}")
