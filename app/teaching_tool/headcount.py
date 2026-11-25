"""Head count (component C10): count people in a class photo, locally (FR-3.1 – FR-3.5).

Our system never uploads the photo. The model is YOLO26x at image size 1920, then
DoubleCountRule (strict version) removes double counts (D28, D55).

Why 1920 and the strict rule: in the combined experiment of 25/11 (5 class photos + 15
SCUT-HEAD images), this was the only option within ±10% on all 5 class photos (worst +2.6%).
At 1280 with today's rule, an iPhone photo with 17 people gave 13 (-23.5%). See
docs/tools-report.md, section 3.
"""
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WEIGHTS = REPO_ROOT / "tools-tests" / "03-headcount" / "models" / "yolo26x.pt"
PERSON_CLASS = 0  # "person" in the COCO classes


@dataclass(frozen=True)
class Box:
    xyxy: tuple  # x1, y1, x2, y2 in pixels
    conf: float


@dataclass
class Photo:
    path: str
    height: int
    boxes: list  # the boxes after the rule, numbered 1..n in this order

    def count(self) -> int:
        return len(self.boxes)


class DoubleCountRule:
    """A desk can split one student into two boxes (D28, strict version D55).

    Part 2, drop a legs-only box: width >= 1.5 x height, center in the bottom third,
    confidence < 0.40. Part 1, merge two boxes of one person: horizontal overlap >= 95% of
    the narrower box, >= 95% of the smaller box inside the larger one, and top edges within
    10% of the smaller box's height. Part 2 runs first.

    The first version merged at 80% / 80% / 20%. On an iPhone photo it merged two real
    people, one sitting behind the other, so the thresholds were made stricter.
    """

    MIN_OVERLAP = 0.95  # of the narrower box's width
    MIN_INSIDE = 0.95   # of the smaller box's area
    MAX_TOP_GAP = 0.10  # of the smaller box's height

    @staticmethod
    def is_legs_only(box: Box, image_height: int) -> bool:
        x1, y1, x2, y2 = box.xyxy
        width, height = x2 - x1, y2 - y1
        return width >= 1.5 * height and (y1 + y2) / 2 > image_height * 2 / 3 and box.conf < 0.40

    @classmethod
    def same_person(cls, a: Box, b: Box) -> bool:
        ax1, ay1, ax2, ay2 = a.xyxy
        bx1, by1, bx2, by2 = b.xyxy
        overlap_w = max(0.0, min(ax2, bx2) - max(ax1, bx1))
        overlap_h = max(0.0, min(ay2, by2) - max(ay1, by1))
        narrower = min(ax2 - ax1, bx2 - bx1)
        smaller_area = min((ax2 - ax1) * (ay2 - ay1), (bx2 - bx1) * (by2 - by1))
        smaller_height = min(ay2 - ay1, by2 - by1)
        return (overlap_w >= cls.MIN_OVERLAP * narrower
                and overlap_w * overlap_h >= cls.MIN_INSIDE * smaller_area
                and abs(ay1 - by1) <= cls.MAX_TOP_GAP * smaller_height)

    def apply(self, boxes: list[Box], image_height: int) -> list[Box]:
        """Return one box per person: legs-only boxes dropped, merged groups kept as their largest box."""
        kept = [b for b in boxes if not self.is_legs_only(b, image_height)]
        parent = list(range(len(kept)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for i in range(len(kept)):
            for j in range(i + 1, len(kept)):
                if self.same_person(kept[i], kept[j]):
                    parent[find(i)] = find(j)
        groups: dict[int, list[Box]] = {}
        for i, box in enumerate(kept):
            groups.setdefault(find(i), []).append(box)
        area = lambda b: (b.xyxy[2] - b.xyxy[0]) * (b.xyxy[3] - b.xyxy[1])
        people = [max(group, key=area) for group in groups.values()]
        return sorted(people, key=lambda b: (b.xyxy[1], b.xyxy[0]))  # top to bottom, then left to right


class HeadCounter:
    """Runs the local model on a photo. The model is loaded once, on first use."""

    def __init__(self, weights: str | Path = DEFAULT_WEIGHTS, imgsz: int = 1920, conf: float = 0.25):
        self.weights, self.imgsz, self.conf = str(weights), imgsz, conf
        self.rule = DoubleCountRule()
        self._model = None

    def _load(self):
        from ultralytics import YOLO, settings
        if settings["sync"]:
            raise RuntimeError("Ultralytics analytics are on. Turn them off: settings.update({'sync': False})")
        self._model = YOLO(self.weights)

    def count(self, photo_path: str | Path) -> Photo:
        if self._model is None:
            self._load()
        result = self._model.predict(str(photo_path), imgsz=self.imgsz, conf=self.conf,
                                     classes=[PERSON_CLASS], device="cpu", verbose=False)[0]
        boxes = [Box(tuple(float(v) for v in xyxy), float(c))
                 for xyxy, c in zip(result.boxes.xyxy.tolist(), result.boxes.conf.tolist())]
        height = int(result.orig_shape[0])
        return Photo(str(photo_path), height, self.rule.apply(boxes, height))
