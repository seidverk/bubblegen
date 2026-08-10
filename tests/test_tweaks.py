from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bubblegen.errors import TweaksError
from bubblegen.tweaks import DeepenOp, StretchOp, ThickenOp, apply_tweaks, load_tweaks


def square(side: float = 100.0) -> list[np.ndarray]:
    """One square contour with midpoints, so edges carry assertable vertices."""
    s, h = side, side / 2
    points = [(0, 0), (h, 0), (s, 0), (s, h), (s, s), (h, s), (0, s), (0, h)]
    return [np.asarray(points, dtype=np.float64)]


def moved(before: list[np.ndarray], after: list[np.ndarray], point: tuple[float, float]) -> float:
    """Displacement magnitude of the vertex that started at `point`."""
    b, a = before[0], after[0]
    idx = int(np.argmin(np.hypot(b[:, 0] - point[0], b[:, 1] - point[1])))
    return float(np.hypot(*(a[idx] - b[idx])))


def test_the_tip_moves_by_the_full_delta() -> None:
    op = StretchOp(band=(0.0, 1.0), beyond=0.5, dx=10.0, feather=0.0)
    out = apply_tweaks(square(), (op,))
    assert out[0][:, 0].max() == pytest.approx(110.0)
    assert out[0][:, 0].min() == pytest.approx(0.0)


def test_points_before_the_threshold_stay_put() -> None:
    op = StretchOp(band=(0.0, 1.0), beyond=0.5, dx=10.0, feather=0.0)
    contours = square()
    assert moved(contours, apply_tweaks(contours, (op,)), (50.0, 0.0)) == pytest.approx(0.0)


def test_the_band_limits_the_pull() -> None:
    op = StretchOp(band=(0.4, 0.6), beyond=0.2, dx=10.0, feather=0.0)
    contours = square()
    out = apply_tweaks(contours, (op,))
    assert moved(contours, out, (100.0, 100.0)) == pytest.approx(0.0)
    assert moved(contours, out, (100.0, 50.0)) == pytest.approx(10.0)


def test_the_feather_ramps_the_pull() -> None:
    op = StretchOp(band=(0.4, 0.6), beyond=0.2, dx=10.0, feather=50.0)
    contours = square()
    pull = moved(contours, apply_tweaks(contours, (op,)), (100.0, 100.0))
    assert 0.0 < pull < 10.0


def test_a_negative_delta_pulls_the_low_side_outward() -> None:
    op = StretchOp(band=(0.0, 1.0), beyond=0.5, dy=-10.0, feather=0.0)
    out = apply_tweaks(square(), (op,))
    assert out[0][:, 1].min() == pytest.approx(-10.0)
    assert out[0][:, 1].max() == pytest.approx(100.0)


def test_an_op_needs_exactly_one_axis() -> None:
    with pytest.raises(ValueError, match="dx or dy"):
        StretchOp(band=(0.0, 1.0), beyond=0.5, dx=1.0, dy=1.0)
    with pytest.raises(ValueError, match="dx or dy"):
        StretchOp(band=(0.0, 1.0), beyond=0.5)


def test_op_fractions_are_validated() -> None:
    with pytest.raises(ValueError, match="band"):
        StretchOp(band=(0.9, 0.1), beyond=0.5, dx=1.0)
    with pytest.raises(ValueError, match="beyond"):
        StretchOp(band=(0.0, 1.0), beyond=1.0, dx=1.0)
    with pytest.raises(ValueError, match="feather"):
        StretchOp(band=(0.0, 1.0), beyond=0.5, dx=1.0, feather=-1.0)


def slab() -> list[np.ndarray]:
    """A 100 mm square whose right edge carries vertices at the band boundaries."""
    points = [(0, 0), (100, 0), (100, 30), (100, 70), (100, 100), (0, 100)]
    return [np.asarray(points, dtype=np.float64)]


def test_thicken_pushes_the_band_edges_apart() -> None:
    """The band's top edge rises and its bottom edge drops, so the stroke widens."""
    op = ThickenOp(band=(0.3, 0.7), beyond=0.4, dy=5.0, feather=0.0)
    contours = slab()
    out = apply_tweaks(contours, (op,))

    assert moved(contours, out, (100.0, 70.0)) == pytest.approx(5.0)
    assert moved(contours, out, (100.0, 30.0)) == pytest.approx(5.0)
    assert out[0][:, 1].max() == pytest.approx(100.0)  # the letter does not grow overall


def test_thicken_leaves_the_anchor_side_alone() -> None:
    op = ThickenOp(band=(0.3, 0.7), beyond=0.6, dy=5.0, feather=0.0)
    contours = slab()
    assert moved(contours, apply_tweaks(contours, (op,)), (0.0, 100.0)) == pytest.approx(0.0)


def test_thicken_moves_the_two_sides_in_opposite_directions() -> None:
    """A point above the band's centre rises, one below it drops."""
    op = ThickenOp(band=(0.2, 0.8), beyond=0.4, dy=4.0, feather=0.0)
    after = apply_tweaks(slab(), (op,))

    assert after[0][2, 1] == pytest.approx(26.0)  # started at y = 30
    assert after[0][3, 1] == pytest.approx(74.0)  # started at y = 70


def test_thicken_needs_a_positive_delta() -> None:
    with pytest.raises(ValueError, match="dy"):
        ThickenOp(band=(0.3, 0.7), beyond=0.4, dy=0.0)
    with pytest.raises(ValueError, match="dy"):
        ThickenOp(band=(0.3, 0.7), beyond=0.4, dy=-2.0)


def comb() -> list[np.ndarray]:
    """A 100x80 block with one notch cut in from the right, floor at x = 40."""
    points = [
        (0, 0),
        (100, 0),
        (100, 30),
        (40, 30),
        (40, 40),
        (40, 50),
        (100, 50),
        (100, 80),
        (0, 80),
    ]
    return [np.asarray(points, dtype=np.float64)]


def test_deepen_moves_the_notch_floor_inward() -> None:
    op = DeepenOp(band=(0.4, 0.6), beyond=0.1, dx=15.0, feather=0.0)
    contours = comb()
    out = apply_tweaks(contours, (op,))

    assert moved(contours, out, (40.0, 40.0)) == pytest.approx(15.0)
    assert out[0][:, 0].max() == pytest.approx(100.0)  # the arms keep their reach


def test_deepen_spares_the_spine() -> None:
    op = DeepenOp(band=(0.4, 0.6), beyond=0.45, dx=15.0, feather=0.0)
    contours = comb()
    out = apply_tweaks(contours, (op,))

    assert moved(contours, out, (40.0, 40.0)) == pytest.approx(0.0)  # floor is inside the spine
    assert moved(contours, out, (0.0, 0.0)) == pytest.approx(0.0)


def test_deepen_leaves_the_arm_tips_alone_inside_the_feather() -> None:
    """The feather reaches the arms; without an x window it would shorten them."""
    op = DeepenOp(band=(0.4, 0.6), beyond=0.1, dx=15.0, feather=8.0)
    before = [np.asarray([(40.0, 40.0), (95.0, 28.0), (0.0, 0.0), (100.0, 80.0)], dtype=np.float64)]
    after = apply_tweaks(before, (op,))

    assert before[0][1, 0] - after[0][1, 0] == pytest.approx(0.0)
    assert before[0][0, 0] - after[0][0, 0] > 0.0


def test_deepen_needs_a_positive_delta() -> None:
    with pytest.raises(ValueError, match="dx"):
        DeepenOp(band=(0.4, 0.6), beyond=0.1, dx=0.0)
    with pytest.raises(ValueError, match="dx"):
        DeepenOp(band=(0.4, 0.6), beyond=0.1, dx=-3.0)


def test_load_tweaks_orders_deepen_first(tmp_path: Path) -> None:
    """Deepen, then thicken, then stretch: each works on the shape the last one left."""
    file = tmp_path / "tweaks.toml"
    file.write_text(
        """
[E]
[[E.stretch]]
band = [0.42, 0.56]
beyond = 0.5
dx = 8.0

[[E.thicken]]
band = [0.42, 0.56]
beyond = 0.34
dy = 4.0

[[E.deepen]]
band = [0.34, 0.42]
beyond = 0.24
dx = 8.0
""",
        encoding="utf-8",
    )
    first, second, third = load_tweaks(file)["E"]
    assert isinstance(first, DeepenOp)
    assert isinstance(second, ThickenOp)
    assert isinstance(third, StretchOp)


def test_load_tweaks_reads_thicken_before_stretch(tmp_path: Path) -> None:
    """Widening first, then pulling: a stretch works on the arm it will lengthen."""
    file = tmp_path / "tweaks.toml"
    file.write_text(
        """
[E]
[[E.stretch]]
band = [0.42, 0.56]
beyond = 0.4
dx = 16.0

[[E.thicken]]
band = [0.42, 0.56]
beyond = 0.34
dy = 5.0
""",
        encoding="utf-8",
    )
    first, second = load_tweaks(file)["E"]
    assert isinstance(first, ThickenOp)
    assert isinstance(second, StretchOp)


def test_load_tweaks_reads_ops_per_char(tmp_path: Path) -> None:
    file = tmp_path / "tweaks.toml"
    file.write_text(
        """
[E]
[[E.stretch]]
band = [0.35, 0.62]
beyond = 0.45
dx = 8.0
feather = 5.0

[[E.stretch]]
band = [0.0, 0.2]
beyond = 0.5
dy = -3.0
""",
        encoding="utf-8",
    )
    tweaks = load_tweaks(file)
    assert set(tweaks) == {"E"}
    first, second = tweaks["E"]
    assert first == StretchOp(band=(0.35, 0.62), beyond=0.45, dx=8.0, feather=5.0)
    assert isinstance(second, StretchOp)
    assert second.dy == -3.0
    assert second.feather == StretchOp(band=(0.0, 1.0), beyond=0.0, dx=1.0).feather


def test_load_tweaks_rejects_an_unknown_key(tmp_path: Path) -> None:
    file = tmp_path / "tweaks.toml"
    file.write_text("[E]\n[[E.stretch]]\nband = [0, 1]\nbeyond = 0.5\ndz = 3\n", encoding="utf-8")
    with pytest.raises(TweaksError, match="dz"):
        load_tweaks(file)


def test_load_tweaks_rejects_a_multi_char_key(tmp_path: Path) -> None:
    file = tmp_path / "tweaks.toml"
    file.write_text("[EE]\n[[EE.stretch]]\nband = [0, 1]\nbeyond = 0.5\ndx = 1\n", encoding="utf-8")
    with pytest.raises(TweaksError, match="EE"):
        load_tweaks(file)


def test_load_tweaks_wraps_a_bad_op_with_its_char(tmp_path: Path) -> None:
    file = tmp_path / "tweaks.toml"
    file.write_text("[E]\n[[E.stretch]]\nband = [1, 0]\nbeyond = 0.5\ndx = 1\n", encoding="utf-8")
    with pytest.raises(TweaksError, match="E"):
        load_tweaks(file)
