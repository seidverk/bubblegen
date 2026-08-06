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
    square: SquareFactory, params: BubbleParams, size: float = 10.0
) -> tuple[NDArray[np.float64], Raster]:
    raster = rasterize([square(size)], params)
    sd = signed_distance(raster.mask, params.resolution)
    return height_field(sd, params), raster


def test_mesh_is_watertight_and_sits_on_the_plate(
    params: BubbleParams, square: SquareFactory
) -> None:
    p = dataclasses.replace(params, dome=0.0)
    height, raster = puffed_square(square, p)

    mesh = build_mesh(height, raster, p)
    extents = mesh.bounds[1] - mesh.bounds[0]

    assert mesh.is_watertight
    assert mesh.bounds[0][2] == pytest.approx(0.0, abs=0.25)
    assert mesh.bounds[1][2] == pytest.approx(p.puff_mm, abs=0.25)
    assert extents[0] == pytest.approx(10.0, abs=0.8)
    assert extents[1] == pytest.approx(10.0, abs=0.8)


def test_dome_raises_the_top(params: BubbleParams, square: SquareFactory) -> None:
    flat = dataclasses.replace(params, dome=0.0)
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


def test_smoothing_and_decimation_together_keep_the_shape(
    params: BubbleParams, square: SquareFactory
) -> None:
    """Taubin diverges on the irregular triangles decimation leaves behind, so the
    smoothing pass has to run while the mesh is still dense."""
    p = dataclasses.replace(params, puff_mm=6.0, dome=0.3, resolution=5.0)
    height, raster = puffed_square(square, p, size=30.0)
    dense = build_mesh(height, raster, p)

    both = build_mesh(
        height, raster, dataclasses.replace(p, target_faces=5_000, smooth_iterations=12)
    )

    assert both.is_watertight
    assert both.volume == pytest.approx(dense.volume, rel=0.03)
    assert both.bounds[1][2] == pytest.approx(dense.bounds[1][2], abs=0.4)
