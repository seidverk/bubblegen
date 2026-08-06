from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import numpy as np
import pytest
from scipy import ndimage

from bubblegen.config import BubbleParams
from bubblegen.fonts import Font
from bubblegen.inflate import height_field
from bubblegen.raster import rasterize, round_silhouette, signed_distance

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


def valley_pixels(h: NDArray[np.float64], mask: NDArray[np.bool_], px_per_mm: float) -> int:
    """Interior pixels where the surface curves upwards.

    An inflated membrane is concave everywhere inside, so a valley means the profile
    dented instead of blending: exactly the crease that shows up where strokes meet.
    """
    inner = ndimage.binary_erosion(mask, iterations=5)
    curvature = ndimage.laplace(h) * px_per_mm**2
    return int(((curvature > 0.5) & inner).sum())


def test_each_stroke_inflates_to_its_own_width(params: BubbleParams, rect: RectFactory) -> None:
    """A stroke rises to its own half-width, so a thin one next to a fat one stays
    proportional instead of borrowing the fat one's profile."""
    p = dataclasses.replace(params, puff_mm=20.0)
    h, _sd, raster = inflated([rect(6.0, 40.0), rect(20.0, 40.0, x=14.0)], p)

    thin = raster.to_pixel((3.0, 20.0))
    fat = raster.to_pixel((24.0, 20.0))
    assert h[thin[1], thin[0]] == pytest.approx(3.0, rel=0.15)
    assert h[fat[1], fat[0]] == pytest.approx(10.0, rel=0.15)


def test_junctions_bulge_instead_of_denting(
    params: BubbleParams, elbow: NDArray[np.float64]
) -> None:
    """Where two strokes meet there is more room, so the surface rises there and stays
    convex; a per-stroke profile creases along the junction instead."""
    p = dataclasses.replace(params, puff_mm=20.0)
    h, _sd, raster = inflated([elbow], p)

    corner = raster.to_pixel((5.0, 5.0))
    along = raster.to_pixel((25.0, 5.0))
    assert h[corner[1], corner[0]] > h[along[1], along[0]]
    assert valley_pixels(h, raster.mask, p.resolution) == 0


def test_a_letter_surface_stays_convex(font: Font, params: BubbleParams) -> None:
    """K has the sharpest junctions in the alphabet: no creases allowed there either."""
    p = dataclasses.replace(params, size_mm=60.0, puff_mm=8.0, resolution=4.0)
    contours = font.contours_mm("K", p.size_mm, p.bezier_steps)
    raster = rasterize(contours, p)
    mask, _used = round_silhouette(raster.mask, p.resolution, p.round_radius)
    h = height_field(signed_distance(mask, p.resolution), p)

    assert valley_pixels(h, mask, p.resolution) == 0


def test_puff_caps_the_thickness(params: BubbleParams, rect: RectFactory) -> None:
    p = dataclasses.replace(params, puff_mm=3.0)
    h, _sd, _raster = inflated([rect(40.0, 40.0)], p)

    assert h.max() == pytest.approx(3.0, abs=0.05)


def test_thin_strokes_are_not_scaled_up_to_the_puff(
    params: BubbleParams, rect: RectFactory
) -> None:
    """`--puff` is a ceiling: a 6 mm stroke stays a 3 mm bubble, not a sausage."""
    p = dataclasses.replace(params, puff_mm=20.0)
    h, _sd, _raster = inflated([rect(6.0, 40.0)], p)

    assert h.max() == pytest.approx(3.0, rel=0.15)


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
    p = dataclasses.replace(params, puff_mm=20.0, fullness=2.0)
    h, _sd, raster = inflated([rect(20.0, 60.0)], p)

    # a semicircle of radius 10 stands 8.66 mm tall 5 mm in from the edge
    probe = raster.to_pixel((5.0, 30.0))
    assert h[probe[1], probe[0]] == pytest.approx(8.66, rel=0.1)


def test_field_sign_follows_the_silhouette(params: BubbleParams, rect: RectFactory) -> None:
    h, sd, _raster = inflated([rect(10.0, 10.0)], params)

    assert np.all(h[sd < 0] < 0)
    assert np.all(h[sd > 0] >= 0)
