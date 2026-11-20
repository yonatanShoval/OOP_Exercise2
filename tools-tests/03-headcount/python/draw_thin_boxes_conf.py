"""Head count tools test: draw the saved YOLO26x @ 1280 boxes thin, with only the confidence above each box.

Boxes changed by the double-count rule (apply_rule.py) are drawn in magenta, the others in green.
Uses the saved boxes, so the model is NOT run again.
Output: course-materials/headcount-output/yolo26x-1280-thin-conf/ (not in git).
Usage: python draw_thin_boxes_conf.py [p1 p11 ...]   (default: all photos)
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from apply_rule import BOXES_FILE, is_legs_only, same_person

REPO_ROOT = Path(__file__).resolve().parents[3]
PHOTOS_DIR = REPO_ROOT / "course-materials"
OUT_DIR = PHOTOS_DIR / "headcount-output" / "yolo26x-1280-thin-conf"

NORMAL = (0, 200, 0)      # green
CHANGED = (255, 0, 255)   # magenta: dropped or merged by the rule
WIDTH = 2
FONT = ImageFont.load_default(size=13)

data = json.loads(BOXES_FILE.read_text(encoding="utf-8"))
names = sys.argv[1:] or list(data)
OUT_DIR.mkdir(parents=True, exist_ok=True)

for name in names:
    photo = data[name]
    boxes = photo["boxes"]
    # Find the boxes the rule changes: legs-only boxes (part 2), then merged pairs (part 1).
    changed = {i for i, b in enumerate(boxes) if is_legs_only(b, photo["height"])}
    kept = [i for i in range(len(boxes)) if i not in changed]
    for n, i in enumerate(kept):
        for j in kept[n + 1:]:
            if same_person(boxes[i], boxes[j]):
                changed |= {i, j}

    image = Image.open(PHOTOS_DIR / f"{name}.jpeg").convert("RGB")
    draw = ImageDraw.Draw(image)
    # Normal boxes first, changed boxes last so they are on top.
    for i in sorted(range(len(boxes)), key=lambda i: i in changed):
        x1, y1, x2, y2 = boxes[i]["xyxy"]
        color = CHANGED if i in changed else NORMAL
        draw.rectangle([x1, y1, x2, y2], outline=color, width=WIDTH)
        # Small confidence number above the box; a thin white outline keeps it readable.
        draw.text((x1 + 1, y1 - 15), f"{boxes[i]['conf']:.2f}", fill=color, font=FONT,
                  stroke_width=1, stroke_fill=(255, 255, 255))
    image.save(OUT_DIR / f"{name}.jpeg", quality=95)
    print(f"{name}: {len(boxes)} boxes, {len(changed)} changed by the rule -> {OUT_DIR / (name + '.jpeg')}")
