"""Head count tools test: apply the double-count rule to the saved boxes (see docs/tools-report.md, section 3).

A desk can split one student into two boxes (upper body and legs). The rule:
  Part 2, drop a legs-only box: width >= 1.5 x height AND center in the bottom third
          of the photo AND confidence < 0.40.
  Part 1, merge two boxes into one person: horizontal overlap >= 80% of the narrower box
          AND >= 80% of the smaller box's area inside the larger box
          AND top edges differ by <= 20% of the smaller box's height.
Part 2 runs first, then part 1 on the remaining boxes. The model is NOT run here.
All thresholds were set after seeing the errors in these photos: risk of overfitting.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BOXES_FILE = REPO_ROOT / "course-materials" / "headcount-output" / "boxes-yolo26x-1280-all.json"
MANUAL = {"p1": 38, "p11": 44, "p21": 43, "p31": 46}  # manual counts, for comparison


def is_legs_only(box, image_height):
    """Part 2: a wide, low, low-confidence box in the bottom third of the photo."""
    x1, y1, x2, y2 = box["xyxy"]
    width, height = x2 - x1, y2 - y1
    return (width >= 1.5 * height
            and (y1 + y2) / 2 > image_height * 2 / 3
            and box["conf"] < 0.40)


def same_person(a, b):
    """Part 1: one box is almost inside the other, and both start at about the same height."""
    ax1, ay1, ax2, ay2 = a["xyxy"]
    bx1, by1, bx2, by2 = b["xyxy"]
    overlap_w = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    overlap_h = max(0.0, min(ay2, by2) - max(ay1, by1))
    narrower = min(ax2 - ax1, bx2 - bx1)
    smaller_area = min((ax2 - ax1) * (ay2 - ay1), (bx2 - bx1) * (by2 - by1))
    smaller_height = min(ay2 - ay1, by2 - by1)
    return (overlap_w >= 0.8 * narrower
            and overlap_w * overlap_h >= 0.8 * smaller_area
            and abs(ay1 - by1) <= 0.20 * smaller_height)


def describe(box):
    x1, y1, x2, y2 = box["xyxy"]
    return f"conf {box['conf']:.2f}, x {x1:.0f}-{x2:.0f}, y {y1:.0f}-{y2:.0f}, {x2 - x1:.0f}x{y2 - y1:.0f}"


def main():
    data = json.loads(BOXES_FILE.read_text(encoding="utf-8"))
    print(f"{'photo':>5} {'before':>6} {'part2':>6} {'part1':>6} {'after':>6} {'manual':>6}")
    details = []
    for name, photo in data.items():
        boxes = photo["boxes"]
        dropped = [b for b in boxes if is_legs_only(b, photo["height"])]
        kept = [b for b in boxes if not is_legs_only(b, photo["height"])]

        # Part 1: group boxes of the same person (union-find), and count each group once.
        parent = list(range(len(kept)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        merged_pairs = []
        for i in range(len(kept)):
            for j in range(i + 1, len(kept)):
                if same_person(kept[i], kept[j]):
                    merged_pairs.append((kept[i], kept[j]))
                    parent[find(i)] = find(j)
        after = len({find(i) for i in range(len(kept))})
        part1 = len(kept) - after
        print(f"{name:>5} {len(boxes):>6} {-len(dropped):>6} {-part1:>6} {after:>6} {MANUAL.get(name, ''):>6}")
        details += [f"{name} part2 dropped: {describe(b)}" for b in dropped]
        details += [f"{name} part1 merged: [{describe(a)}] + [{describe(b)}]" for a, b in merged_pairs]

    print("\nDetails:")
    print("\n".join(details) if details else "(no changes)")


if __name__ == "__main__":
    main()
