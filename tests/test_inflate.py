from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import numpy as np
import pytest

from bubblegen.config import BubbleParams, Profile
from bubblegen.inflate import height_field
from bubblegen.raster import rasterize, signed_distance

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from bubblegen.raster import Raster
    from conftest import SquareFactory


def inflated(
    contours: list[NDArray[np.float64]], params: BubbleParams
) -> tuple[NDArray[np.float64], NDArray[np.float64], Raster]:
    raster = rasterize(contours, params)
    sd = signed_distance(raster.mask, params.resolution)
    return height_field(sd, params), sd, raster


def test_each_stroke_inflates_to_its_own_width(params: BubbleParams, square: SquareFactory) -> None:
    """A thin stroke next to a fat one must not borrow the fat one's profile, or it
    comes out as a tall sausage with a tent ridge down the middle."""
    p = dataclasses.replace(params, puff_mm=20.0)
    h, _sd, raster = inflated([square(6.0), square(20.0, offset=10.0)], p)

    thin = raster.to_pixel((3.0, 3.0))
    fat = raster.to_pixel((20.0, 20.0))
    assert h[thin[1], thin[0]] == pytest.approx(3.0, abs=0.5)
    assert h[fat[1], fat[0]] == pytest.approx(10.0, abs=0.7)


def test_surface_arrives_flat_at_the_centre_line(
    params: BubbleParams, square: SquareFactory
) -> None:
    """The centre line is the top of the bubble: the surface has to level off there
    rather than meeting itself at an angle."""
    p = dataclasses.replace(params, puff_mm=20.0)
    h, _sd, raster = inflated([square(6.0), square(20.0, offset=10.0)], p)

    row = raster.to_pixel((3.0, 3.0))[1]
    across = h[row]
    peak = int(np.argmax(across[: raster.to_pixel((6.0, 3.0))[0]]))
    slope = np.abs(np.diff(across))[peak - 1 : peak + 1].max() * p.resolution

    assert slope < 0.2  # mm of rise per mm across; a tent ridge is around 1


def test_puff_caps_the_thickness(params: BubbleParams, square: SquareFactory) -> None:
    p = dataclasses.replace(params, puff_mm=3.0)
    h, _sd, _raster = inflated([square(40.0)], p)

    assert h.max() == pytest.approx(3.0, abs=0.05)


def test_field_sign_follows_the_silhouette(params: BubbleParams, square: SquareFactory) -> None:
    h, sd, _raster = inflated([square(10.0)], params)

    assert np.all(h[sd < 0] < 0)
    assert np.all(h[sd > 0] >= 0)


def test_explicit_roll_saturates_early(params: BubbleParams, square: SquareFactory) -> None:
    """A short explicit roll is the old behaviour: full thickness a millimetre in,
    flat from there. Useful for a sharp shoulder, wrong as a default."""
    base = dataclasses.replace(params, puff_mm=3.0)
    auto, _sd, raster = inflated([square(20.0)], base)
    early, _sd2, _raster2 = inflated([square(20.0)], dataclasses.replace(base, roll_mm=1.0))

    probe = raster.to_pixel((2.0, 10.0))  # 2 mm inside a 10 mm half-width stroke
    assert early[probe[1], probe[0]] == pytest.approx(base.puff_mm, abs=0.1)
    assert auto[probe[1], probe[0]] < 0.7 * base.puff_mm


def test_profiles_are_ordered_by_shoulder_fullness(
    params: BubbleParams, square: SquareFactory
) -> None:
    base = dataclasses.replace(params, puff_mm=20.0)
    heights = {
        profile: inflated([square(10.0)], dataclasses.replace(base, profile=profile))[0]
        for profile in Profile
    }
    _h, sd, _raster = inflated([square(10.0)], base)
    inside = sd > 0
    assert np.all(heights[Profile.SUPER][inside] >= heights[Profile.SPHERE][inside] - 1e-9)
    assert np.all(heights[Profile.SPHERE][inside] >= heights[Profile.SMOOTH][inside] - 1e-9)
