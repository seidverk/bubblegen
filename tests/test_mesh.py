from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import numpy as np
import pytest
import trimesh
from numpy.typing import NDArray

from bubblegen.config import BubbleParams
from bubblegen.inflate import height_field
from bubblegen.mesh import build_mesh
from bubblegen.raster import Raster, rasterize, signed_distance

if TYPE_CHECKING:
    from conftest import SquareFactory

Prepared = tuple[NDArray[np.float64], NDArray[np.float64], Raster]


def puffed_square(square: SquareFactory, params: BubbleParams, size: float = 10.0) -> Prepared:
    raster = rasterize([square(size)], params)
    sd = signed_distance(raster.mask, params.resolution)
    return height_field(sd, params), sd, raster


def contact_patch(mesh: trimesh.Trimesh) -> NDArray[np.float64]:
    """Vertices sitting on the plate: the flat patch the letter actually rests on."""
    return np.asarray(mesh.vertices[mesh.vertices[:, 2] < 0.02])


def test_mesh_is_watertight_and_sits_on_the_plate(
    params: BubbleParams, square: SquareFactory
) -> None:
    height, sd, raster = puffed_square(square, params)

    mesh = build_mesh(height, sd, raster, params)
    extents = mesh.bounds[1] - mesh.bounds[0]

    assert mesh.is_watertight
    assert mesh.bounds[0][2] == pytest.approx(0.0, abs=0.25)
    assert extents[0] == pytest.approx(10.0, abs=0.8)
    assert extents[1] == pytest.approx(10.0, abs=0.8)


def test_the_underside_is_filleted_into_a_smaller_flat_patch(
    params: BubbleParams, square: SquareFactory
) -> None:
    """A wall meeting the plate at a right angle reads as an extrusion; the outline has
    to curve down into the contact patch."""
    p = dataclasses.replace(params, base_round_mm=1.5)
    height, sd, raster = puffed_square(square, p)

    mesh = build_mesh(height, sd, raster, p)
    patch = contact_patch(mesh)
    widest = mesh.bounds[1][0] - mesh.bounds[0][0]
    footprint = patch[:, 0].max() - patch[:, 0].min()

    assert mesh.is_watertight
    assert patch[:, 2].max() == pytest.approx(0.0, abs=0.01)
    assert footprint == pytest.approx(widest - 2 * p.base_radius, abs=1.0)


def test_zero_base_round_keeps_the_wall_square(params: BubbleParams, square: SquareFactory) -> None:
    p = dataclasses.replace(params, base_round_mm=0.0)
    height, sd, raster = puffed_square(square, p)

    mesh = build_mesh(height, sd, raster, p)
    patch = contact_patch(mesh)
    widest = mesh.bounds[1][0] - mesh.bounds[0][0]

    assert patch[:, 0].max() - patch[:, 0].min() == pytest.approx(widest, abs=0.3)


def test_decimation_reduces_faces_and_keeps_it_closed(
    params: BubbleParams, square: SquareFactory
) -> None:
    height, sd, raster = puffed_square(square, params)
    dense = build_mesh(height, sd, raster, params)

    budget = len(dense.faces) // 4
    decimated = build_mesh(height, sd, raster, dataclasses.replace(params, target_faces=budget))

    assert len(decimated.faces) < len(dense.faces)
    assert decimated.is_watertight


def test_smoothing_keeps_the_mesh_closed_and_the_volume(
    params: BubbleParams, square: SquareFactory
) -> None:
    height, sd, raster = puffed_square(square, params)
    raw = build_mesh(height, sd, raster, params)

    smoothed = build_mesh(height, sd, raster, dataclasses.replace(params, smooth_iterations=10))

    assert smoothed.is_watertight
    assert smoothed.volume == pytest.approx(raw.volume, rel=0.15)


def test_smoothing_and_decimation_together_keep_the_shape(
    params: BubbleParams, square: SquareFactory
) -> None:
    """Taubin diverges on the irregular triangles decimation leaves behind, so the
    smoothing pass has to run while the mesh is still dense."""
    p = dataclasses.replace(params, puff_mm=6.0, resolution=5.0)
    height, sd, raster = puffed_square(square, p, size=30.0)
    dense = build_mesh(height, sd, raster, p)

    both = build_mesh(
        height, sd, raster, dataclasses.replace(p, target_faces=5_000, smooth_iterations=12)
    )

    assert both.is_watertight
    assert both.volume == pytest.approx(dense.volume, rel=0.03)
    assert both.bounds[1][2] == pytest.approx(dense.bounds[1][2], abs=0.4)
