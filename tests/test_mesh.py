from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import pytest

from bubblegen.config import BubbleParams
from bubblegen.inflate import height_field
from bubblegen.mesh import build_mesh
from bubblegen.raster import Raster, rasterize, signed_distance

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray

    from conftest import SquareFactory


def puffed_square(
    square: SquareFactory, params: BubbleParams
) -> tuple[NDArray[np.float64], Raster]:
    raster = rasterize([square(10.0)], params)
    sd = signed_distance(raster.mask, params.resolution)
    return height_field(sd, params), raster


def test_symmetric_mesh_is_watertight_and_twice_the_puff(
    params: BubbleParams, square: SquareFactory
) -> None:
    p = dataclasses.replace(params, dome=0.0)
    height, raster = puffed_square(square, p)

    mesh = build_mesh(height, raster, p)
    extents = mesh.bounds[1] - mesh.bounds[0]

    assert mesh.is_watertight
    assert extents[2] == pytest.approx(2 * p.puff_mm, abs=0.4)
    assert extents[0] == pytest.approx(10.0, abs=0.8)
    assert extents[1] == pytest.approx(10.0, abs=0.8)


def test_flat_back_mesh_sits_on_one_plane(params: BubbleParams, square: SquareFactory) -> None:
    p = dataclasses.replace(params, flat_back=True, dome=0.0)
    height, raster = puffed_square(square, p)

    mesh = build_mesh(height, raster, p)

    assert mesh.is_watertight
    assert mesh.bounds[0][2] == pytest.approx(0.0, abs=0.25)
    assert mesh.bounds[1][2] == pytest.approx(p.puff_mm, abs=0.25)


def test_dome_raises_the_top(params: BubbleParams, square: SquareFactory) -> None:
    flat = dataclasses.replace(params, flat_back=True, dome=0.0)
    domed = dataclasses.replace(flat, dome=0.4)

    flat_mesh = build_mesh(*puffed_square(square, flat), flat)
    domed_mesh = build_mesh(*puffed_square(square, domed), domed)

    assert domed_mesh.bounds[1][2] == pytest.approx(flat.puff_mm * 1.4, abs=0.25)
    assert domed_mesh.bounds[1][2] > flat_mesh.bounds[1][2]


def test_decimation_reduces_faces_and_keeps_it_closed(
    params: BubbleParams, square: SquareFactory
) -> None:
    height, raster = puffed_square(square, params)
    dense = build_mesh(height, raster, params)

    budget = len(dense.faces) // 4
    decimated = build_mesh(height, raster, dataclasses.replace(params, target_faces=budget))

    assert len(decimated.faces) < len(dense.faces)
    assert decimated.is_watertight


def test_smoothing_keeps_the_mesh_closed_and_the_volume(
    params: BubbleParams, square: SquareFactory
) -> None:
    height, raster = puffed_square(square, params)
    raw = build_mesh(height, raster, params)

    smoothed = build_mesh(height, raster, dataclasses.replace(params, smooth_iterations=10))

    assert smoothed.is_watertight
    assert smoothed.volume == pytest.approx(raw.volume, rel=0.15)
