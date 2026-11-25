"""DoubleCountRule (D28): one box per person, even when the desk splits a student."""
from teaching_tool.headcount import Box, DoubleCountRule

H = 1200  # photo height in pixels
rule = DoubleCountRule()


def test_upper_body_and_full_body_of_one_person_are_merged():
    upper = Box((100, 300, 200, 420), 0.80)
    full = Box((98, 305, 205, 600), 0.55)  # same left edge, top edges 5 px apart
    assert len(rule.apply([upper, full], H)) == 1


def test_a_wide_low_legs_box_in_the_bottom_third_is_dropped():
    person = Box((100, 300, 200, 600), 0.80)
    legs = Box((90, 900, 300, 1000), 0.31)  # 210 x 100, center at y = 950 > 800
    assert rule.apply([person, legs], H) == [person]


def test_two_people_side_by_side_are_not_merged():
    left = Box((100, 300, 200, 600), 0.80)
    right = Box((190, 310, 290, 610), 0.75)  # small overlap only
    assert len(rule.apply([left, right], H)) == 2


def test_a_confident_wide_box_is_kept():
    wide = Box((90, 900, 300, 1000), 0.85)  # wide and low, but the model is sure
    assert len(rule.apply([wide], H)) == 1
