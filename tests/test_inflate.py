from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import numpy as np
import pytest
from scipy import ndimage

from bubblegen.config import BubbleParams
from bubblegen.inflate import height_field, uniform_limit
from bubblegen.raster import rasterize, signed_distance

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from bubblegen.raster import Raster
    from conftest import RectFactory


def inflated(
    contours: list[NDArray[np.float64]], params: BubbleParams
) -> tuple[NDArray[np.float64], NDArray[np.float64], Raster]:
    raster = rasterize(contours, params)
    sd = signed_distance(raster.mask, params.resolution)
    return height_field(sd, params), sd, raster


def ring_spread(h: NDArray[np.float64], raster: Raster) -> float:
    """How much the tube height varies around the `uneven_ring`, as a share of its peak.

    The tube of a doughnut is the same height all the way round. Variation here is the
    groove that shows up across the top of an O, where the ring happens to be narrower.
    """
    angles = np.linspace(0.0, 2.0 * np.pi, 120)
    radius = (30.0 + 14.0 * 18.0 / np.hypot(18.0 * np.cos(angles), 14.0 * np.sin(angles))) / 2
    heights = [
        h[py, px]
        for px, py in (
            raster.to_pixel((40 + r * np.cos(a), 40 + r * np.sin(a)))
            for a, r in zip(angles, radius, strict=True)
        )
    ]
    return float((max(heights) - min(heights)) / max(heights))


def test_strokes_reach_the_same_thickness(params: BubbleParams, rect: RectFactory) -> None:
    """A doughnut has one tube thickness however its outline wanders. Scaling the height
    with the local stroke width instead pinches every narrow section into a groove."""
    p = dataclasses.replace(params, puff_mm=5.0)
    h, _sd, raster = inflated([rect(12.0, 40.0), rect(30.0, 40.0, x=20.0)], p)

    thin = raster.to_pixel((6.0, 20.0))
    fat = raster.to_pixel((35.0, 20.0))
    assert h[thin[1], thin[0]] == pytest.approx(5.0, rel=0.05)
    assert h[fat[1], fat[0]] == pytest.approx(5.0, rel=0.05)


def test_a_stroke_too_thin_for_the_puff_stops_at_its_own_width(
    params: BubbleParams, rect: RectFactory
) -> None:
    p = dataclasses.replace(params, puff_mm=20.0)
    h, _sd, raster = inflated([rect(8.0, 40.0), rect(30.0, 40.0, x=16.0)], p)

    thin = raster.to_pixel((4.0, 20.0))
    fat = raster.to_pixel((31.0, 20.0))
    assert h[thin[1], thin[0]] == pytest.approx(8.0, rel=0.2)
    assert h[fat[1], fat[0]] == pytest.approx(20.0, rel=0.05)


def test_junctions_stay_level(params: BubbleParams, elbow: NDArray[np.float64]) -> None:
    """A junction has more room than the strokes it joins, but a doughnut does not swell
    there: it stays level, and above all it does not crease."""
    p = dataclasses.replace(params, puff_mm=8.0)
    h, _sd, raster = inflated([elbow], p)

    corner = raster.to_pixel((5.0, 5.0))
    along = raster.to_pixel((25.0, 5.0))
    assert h[corner[1], corner[0]] == pytest.approx(h[along[1], along[0]], rel=0.1)


def test_a_narrowing_ring_keeps_one_thickness(
    params: BubbleParams, uneven_ring: list[NDArray[np.float64]]
) -> None:
    """The ring of an O is narrower at top and bottom. The tube must not be pinched
    there: that is the groove that shows up across the top of an O."""
    p = dataclasses.replace(params, puff_mm=10.0)
    h, _sd, raster = inflated(uneven_ring, p)

    side = raster.to_pixel((18.0, 40.0))  # ring is 16 mm wide here
    top = raster.to_pixel((40.0, 64.0))  # and 12 mm wide here
    assert h[side[1], side[0]] == pytest.approx(h[top[1], top[0]], rel=0.05)
    assert ring_spread(h, raster) < 0.1


def test_the_reported_limit_is_the_thickness_that_comes_out_even(
    params: BubbleParams, uneven_ring: list[NDArray[np.float64]]
) -> None:
    raster = rasterize(uneven_ring, params)
    sd = signed_distance(raster.mask, params.resolution)

    limit = uniform_limit(sd, params)
    even = height_field(sd, dataclasses.replace(params, puff_mm=limit))
    greedy = height_field(sd, dataclasses.replace(params, puff_mm=limit * 2.0))

    assert ring_spread(even, raster) < 0.1
    assert ring_spread(greedy, raster) > 0.15


def test_the_limit_ignores_accents(params: BubbleParams, rect: RectFactory) -> None:
    """An acute or a dot is a small piece of its own and has to stay thin. It must not
    drag down the thickness reported for the letter it sits over."""
    body_only = rasterize([rect(30.0, 40.0)], params)
    with_accent = rasterize([rect(30.0, 40.0), rect(6.0, 6.0, x=12.0, y=48.0)], params)

    plain = uniform_limit(signed_distance(body_only.mask, params.resolution), params)
    accented = uniform_limit(signed_distance(with_accent.mask, params.resolution), params)

    assert accented == pytest.approx(plain, rel=0.1)


def test_concave_corners_do_not_grow_pimples(
    params: BubbleParams, fat_elbow: NDArray[np.float64]
) -> None:
    """The medial axis runs into every concave corner, but the letter is not at its
    thickest there. Taking those pixels for crests puts a pimple on each junction."""
    p = dataclasses.replace(params, puff_mm=24.0)
    h, sd, raster = inflated([fat_elbow], p)

    at_full_height = raster.mask & (h >= 0.99 * h.max()) & (sd < 10.0)

    assert ndimage.label(at_full_height)[1] <= 2


def test_puff_caps_the_thickness(params: BubbleParams, rect: RectFactory) -> None:
    p = dataclasses.replace(params, puff_mm=3.0)
    h, _sd, _raster = inflated([rect(40.0, 40.0)], p)

    assert h.max() == pytest.approx(3.0, abs=0.05)


def test_thickness_stops_at_the_stroke_width(params: BubbleParams, rect: RectFactory) -> None:
    """As tall as it is wide is a doughnut; taller is a sausage. A 6 mm stroke tops out
    at 6 mm no matter what `--puff` asks for."""
    p = dataclasses.replace(params, puff_mm=40.0)
    h, _sd, _raster = inflated([rect(6.0, 40.0)], p)

    assert h.max() == pytest.approx(6.0, rel=0.2)


def test_puff_can_go_past_the_natural_peak(params: BubbleParams, rect: RectFactory) -> None:
    """The membrane on its own only reaches half the stroke width, which reads as
    flattened. Asking for more has to be allowed, up to the doughnut limit."""
    p = dataclasses.replace(params, puff_mm=25.0)
    h, _sd, _raster = inflated([rect(30.0, 60.0)], p)

    assert h.max() == pytest.approx(25.0, rel=0.05)


def test_fullness_steepens_the_flanks_without_moving_the_peak(
    params: BubbleParams, rect: RectFactory
) -> None:
    """A real balloon is fuller than a semicircle: steep sides, broad top. That is what
    reads as inflated rather than as a plain dome."""
    lean = dataclasses.replace(params, puff_mm=20.0, fullness=2.0)
    full = dataclasses.replace(lean, fullness=5.0)

    thin_h, _sd, raster = inflated([rect(30.0, 60.0)], lean)
    full_h, _sd2, _raster2 = inflated([rect(30.0, 60.0)], full)

    flank = raster.to_pixel((3.0, 30.0))
    assert full_h[flank[1], flank[0]] > 1.3 * thin_h[flank[1], flank[0]]
    assert full_h.max() == pytest.approx(thin_h.max(), rel=0.05)


def test_fullness_two_is_a_semicircle(params: BubbleParams, rect: RectFactory) -> None:
    p = dataclasses.replace(params, puff_mm=10.0, fullness=2.0)
    h, _sd, raster = inflated([rect(20.0, 60.0)], p)

    # a semicircle of radius 10 stands 8.66 mm tall 5 mm in from the edge
    probe = raster.to_pixel((5.0, 30.0))
    assert h[probe[1], probe[0]] == pytest.approx(8.66, rel=0.1)


def test_field_sign_follows_the_silhouette(params: BubbleParams, rect: RectFactory) -> None:
    h, sd, _raster = inflated([rect(10.0, 10.0)], params)

    assert np.all(h[sd < 0] < 0)
    assert np.all(h[sd > 0] >= 0)
