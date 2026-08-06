from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import trimesh

from bubblegen.config import BubbleParams
from bubblegen.hole import drill_hole, find_hole_center
from bubblegen.raster import Raster, rasterize, signed_distance

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray

    from conftest import SquareFactory


def sdf_of_square(
    square: SquareFactory, params: BubbleParams, size: float
) -> tuple[NDArray[np.float64], Raster]:
    raster = rasterize([square(size)], params)
    return signed_distance(raster.mask, params.resolution), raster


def test_hole_sits_near_the_top_with_room_to_spare(
    params: BubbleParams, square: SquareFactory
) -> None:
    p = dataclasses.replace(params, hole_mm=3.0, hole_wall_mm=2.0)
    sd, raster = sdf_of_square(square, p, 20.0)

    centre = find_hole_center(sd, raster, p)

    assert centre is not None
    cx, cy = centre
    assert 8.0 < cx < 12.0
    assert 14.5 < cy < 18.0


def test_no_hole_when_the_glyph_is_too_thin(params: BubbleParams, square: SquareFactory) -> None:
    p = dataclasses.replace(params, hole_mm=3.0, hole_wall_mm=2.0)
    sd, raster = sdf_of_square(square, p, 4.0)

    assert find_hole_center(sd, raster, p) is None


def test_bottom_placement(params: BubbleParams, square: SquareFactory) -> None:
    p = dataclasses.replace(params, hole_mm=3.0, hole_wall_mm=2.0)
    sd, raster = sdf_of_square(square, p, 20.0)

    centre = find_hole_center(sd, raster, p, where="bottom")

    assert centre is not None
    assert 2.0 < centre[1] < 5.5


def test_drilling_removes_material(params: BubbleParams) -> None:
    p = dataclasses.replace(params, hole_mm=2.0)
    box = trimesh.creation.box(extents=(10.0, 10.0, 4.0))

    drilled = drill_hole(box, (0.0, 0.0), p)

    assert drilled.is_watertight
    assert drilled.volume < box.volume - 10.0
