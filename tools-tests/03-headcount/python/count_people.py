"""Head count tools test: count people in the class photos with YOLO26, locally.

Runs only on this computer. The photos never leave it (see docs/tools-report.md, section 3).
Annotated copies are saved to course-materials/headcount-output/, which is not in git.
"""
import argparse
from pathlib import Path

from ultralytics import YOLO, settings

REPO_ROOT = Path(__file__).resolve().parents[3]
PHOTOS_DIR = REPO_ROOT / "course-materials"
OUTPUT_DIR = PHOTOS_DIR / "headcount-output"
MODELS_DIR = Path(__file__).resolve().parents[1] / "models"  # model weights, not in git
PERSON_CLASS = 0  # "person" in the COCO classes

parser = argparse.ArgumentParser(description="Count people in class photos with YOLO26.")
parser.add_argument("--model", default="yolo26n.pt", help="yolo26n.pt or yolo26x.pt")
parser.add_argument("--imgsz", type=int, default=640, help="processing size, 640 or 1280")
parser.add_argument("--conf", type=float, default=0.25, help="confidence threshold")
parser.add_argument("photos", nargs="*", help="photo names, e.g. p1 p11 (default: all p*.jpeg)")
args = parser.parse_args()

if settings["sync"]:
    raise SystemExit("Ultralytics analytics are on. Turn them off first: settings.update({'sync': False})")

if args.photos:
    photos = [PHOTOS_DIR / f"{name}.jpeg" for name in args.photos]
else:
    photos = sorted(PHOTOS_DIR.glob("p*.jpeg"), key=lambda p: int(p.stem[1:]))
missing = [p.name for p in photos if not p.exists()]
if missing:
    raise SystemExit(f"Photos not found in {PHOTOS_DIR}: {missing}")

MODELS_DIR.mkdir(exist_ok=True)
# On first use the weights are downloaded once. Only the model is downloaded; no photo is sent.
model = YOLO(str(MODELS_DIR / args.model))
out_dir = OUTPUT_DIR / f"{Path(args.model).stem}-{args.imgsz}"
out_dir.mkdir(parents=True, exist_ok=True)

print(f"Model: {args.model}, imgsz: {args.imgsz}, conf: {args.conf}")
total_ms = 0.0
for photo in photos:
    result = model.predict(str(photo), imgsz=args.imgsz, conf=args.conf,
                           classes=[PERSON_CLASS], device="cpu", verbose=False)[0]
    count = len(result.boxes)
    ms = sum(result.speed.values())  # preprocess + inference + postprocess
    total_ms += ms
    result.save(filename=str(out_dir / photo.name))  # annotated copy, stays out of git
    print(f"{photo.stem:>4}: {count:3d} people   ({ms:.0f} ms)")
print(f"Done: {len(photos)} photos, average {total_ms / len(photos):.0f} ms per photo")
