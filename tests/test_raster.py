from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

from bubblegen.config import BubbleParams
from bubblegen.raster import (
    dilate,
    erode,
    rasterize,
    round_silhouette,
    signed_distance,
    soften,
)

if TYPE_CHECKING:
    from conftest import SquareFactory


def test_mask_area_matches_contour_area(params: BubbleParams, square: SquareFactory) -> None:
    raster = rasterize([square(10.0)], params)
    area_mm2 = raster.mask.sum() / params.resolution**2
    assert area_mm2 == pytest.approx(100.0, rel=0.02)


def test_origin_is_offset_by_margin(params: BubbleParams, square: SquareFactory) -> None:
    raster = rasterize([square(10.0)], params)
    assert raster.origin[0] == pytest.approx(-params.margin, abs=0.5)
    assert raster.origin[1] == pytest.approx(-params.margin, abs=0.5)


def test_nested_contour_becomes_a_hole(params: BubbleParams, square: SquareFactory) -> None:
    raster = rasterize([square(10.0), square(4.0, offset=3.0)], params)
    area_mm2 = raster.mask.sum() / params.resolution**2
    assert area_mm2 == pytest.approx(100.0 - 16.0, rel=0.03)

    px, py = raster.to_pixel((5.0, 5.0))
    assert not raster.mask[py, px]


def test_to_pixel_round_trips(params: BubbleParams, square: SquareFactory) -> None:
    raster = rasterize([square(10.0)], params)
    px, py = raster.to_pixel((5.0, 5.0))
    x, y = raster.to_mm((px, py))
    assert (x, y) == pytest.approx((5.0, 5.0), abs=1.0 / params.resolution)


def test_soften_is_a_noop_at_zero_radius(params: BubbleParams, square: SquareFactory) -> None:
    mask = rasterize([square(10.0)], params).mask
    assert np.array_equal(soften(mask, params.resolution, 0.0), mask)


def test_soften_rounds_corners_but_keeps_the_body(
    params: BubbleParams, square: SquareFactory
) -> None:
    raster = rasterize([square(10.0)], params)
    rounded = soften(raster.mask, params.resolution, 1.5)

    corner = raster.to_pixel((0.1, 0.1))
    centre = raster.to_pixel((5.0, 5.0))
    assert raster.mask[corner[1], corner[0]]
    assert not rounded[corner[1], corner[0]]
    assert rounded[centre[1], centre[0]]
    assert rounded.sum() > 0.85 * raster.mask.sum()


def test_rounding_keeps_the_requested_radius_when_it_fits(
    params: BubbleParams, square: SquareFactory
) -> None:
    raster = rasterize([square(20.0)], params)

    rounded, used = round_silhouette(raster.mask, params.resolution, 2.0)

    assert used == 2.0
    assert rounded.sum() > 0.9 * raster.mask.sum()


def test_rounding_backs_off_rather_than_filling_a_counter(
    params: BubbleParams, square: SquareFactory
) -> None:
    """Closing bridges any gap narrower than its radius, which would swallow the
    counters of O, R and the aperture of G."""
    raster = rasterize([square(20.0), square(4.0, offset=8.0)], params)

    rounded, used = round_silhouette(raster.mask, params.resolution, 4.0)

    counter = raster.to_pixel((10.0, 10.0))
    assert used < 2.0
    assert not rounded[counter[1], counter[0]]


def test_rounding_backs_off_rather_than_erasing_a_thin_stroke(
    params: BubbleParams, square: SquareFactory
) -> None:
    raster = rasterize([square(1.5)], params)

    rounded, used = round_silhouette(raster.mask, params.resolution, 3.0)

    assert rounded.any()
    assert used < 3.0


def test_dilating_an_empty_mask_keeps_it_empty(params: BubbleParams) -> None:
    """scipy's EDT has no background to measure against, so this needs its own guard."""
    empty = np.zeros((20, 20), dtype=bool)
    assert not dilate(empty, params.resolution, 2.0).any()


def test_eroding_a_full_mask_keeps_it_full(params: BubbleParams) -> None:
    full = np.ones((20, 20), dtype=bool)
    assert erode(full, params.resolution, 2.0).all()


def test_soften_erases_a_stroke_thinner_than_the_radius(
    params: BubbleParams, square: SquareFactory
) -> None:
    thin = rasterize([square(1.0)], params).mask
    assert not soften(thin, params.resolution, 3.0).any()


def test_signed_distance_signs_and_magnitude(params: BubbleParams, square: SquareFactory) -> None:
    raster = rasterize([square(10.0)], params)
    sd = signed_distance(raster.mask, params.resolution)

    centre = raster.to_pixel((5.0, 5.0))
    outside = raster.to_pixel((-3.0, 5.0))
    assert sd[centre[1], centre[0]] == pytest.approx(5.0, abs=0.4)
    assert sd[outside[1], outside[0]] == pytest.approx(-3.0, abs=0.4)
    assert sd[raster.mask].min() > 0
    assert sd[~raster.mask].max() < 0
