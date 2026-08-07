from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import numpy as np
import pytest
import trimesh
from numpy.typing import NDArray

from bubblegen.config import BubbleParams
from bubblegen.inflate import height_field
from bubblegen.mesh import _base_inset, build_mesh
from bubblegen.raster import Raster, rasterize, signed_distance

if TYPE_CHECKING:
    from conftest import RectFactory, SquareFactory

Prepared = tuple[NDArray[np.float64], NDArray[np.float64], Raster, NDArray[np.float64]]


def puffed_square(square: SquareFactory, params: BubbleParams, size: float = 10.0) -> Prepared:
    raster = rasterize([square(size)], params)
    sd = signed_distance(raster.mask, params.resolution)
    height, crest = height_field(sd, params)
    return height, sd, raster, crest


def contact_patch(mesh: trimesh.Trimesh) -> NDArray[np.float64]:
    """Vertices sitting on the plate: the flat patch the letter actually rests on."""
    return np.asarray(mesh.vertices[mesh.vertices[:, 2] < 1e-4])


def outward_step(mesh: trimesh.Trimesh, z_lo: float, z_hi: float) -> float:
    """How far the outline at `z_hi` juts out past the one at `z_lo`, at the worst point.

    This is the unsupported width a printer meets going from one layer to the next."""

    def rings(z: float) -> list[NDArray[np.float64]]:
        section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        assert section is not None
        return [np.asarray(c)[:, :2] for c in section.discrete]

    def inside(pt: NDArray[np.float64], polys: list[NDArray[np.float64]]) -> bool:
        crossings = 0
        for poly in polys:
            px, py = poly[:, 0], poly[:, 1]
            qx, qy = np.roll(px, 1), np.roll(py, 1)
            spans = (py > pt[1]) != (qy > pt[1])
            with np.errstate(divide="ignore", invalid="ignore"):
                xin = px + (pt[1] - py) * (qx - px) / (qy - py)
            crossings += int(np.count_nonzero(spans & (pt[0] < xin)))
        return crossings % 2 == 1

    def distance(pt: NDArray[np.float64], polys: list[NDArray[np.float64]]) -> float:
        best = np.inf
        for poly in polys:
            a, b = poly, np.roll(poly, -1, axis=0)
            ab, ap = b - a, pt - a
            t = np.clip(
                np.einsum("ij,ij->i", ap, ab) / np.maximum(np.einsum("ij,ij->i", ab, ab), 1e-12),
                0.0,
                1.0,
            )
            best = min(best, float(np.linalg.norm(pt - (a + t[:, None] * ab), axis=1).min()))
        return best

    lo, hi = rings(z_lo), rings(z_hi)
    return max(
        (distance(pt, lo) for poly in hi for pt in poly if not inside(pt, lo)),
        default=0.0,
    )


def test_mesh_is_watertight_and_sits_on_the_plate(
    params: BubbleParams, square: SquareFactory
) -> None:
    height, sd, raster, crest = puffed_square(square, params)

    mesh = build_mesh(height, sd, raster, params, crest)
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
    height, sd, raster, crest = puffed_square(square, p)

    mesh = build_mesh(height, sd, raster, p, crest)
    patch = contact_patch(mesh)
    widest = mesh.bounds[1][0] - mesh.bounds[0][0]
    # measured across the middle of an edge: at the corners the half-width pinches
    # and the fillet honestly backs off, so the patch corners stay wider
    middle = patch[np.abs(patch[:, 1] - patch[:, 1].mean()) < 2.0]
    footprint = middle[:, 0].max() - middle[:, 0].min()

    assert mesh.is_watertight
    erosion = (2.0 - np.sqrt(2.0)) * p.base_radius
    assert footprint == pytest.approx(widest - 2 * erosion, abs=1.0)


def test_base_fillet_never_overhangs_past_45_degrees() -> None:
    """Each layer must land on the one below: the fillet's outward step per layer
    cannot exceed the layer height, so the profile slope stays within 45 degrees."""
    radius = 3.5
    zs = np.linspace(0.0, radius, 701)

    inset = _base_inset(zs, radius)

    assert inset is not None
    slopes = np.abs(np.diff(inset) / np.diff(zs))
    assert slopes.max() <= 1.0 + 1e-9


def test_a_narrow_stroke_keeps_its_feet_on_the_plate(
    params: BubbleParams, rect: RectFactory
) -> None:
    """A fillet the stroke cannot afford must back off: eroding past the local
    half-width lifts whole sections off the plate, and they print in the air."""
    p = dataclasses.replace(params, base_round_mm=8.0)
    raster = rasterize([rect(6.0, 15.0)], p)
    sd = signed_distance(raster.mask, p.resolution)
    height, crest = height_field(sd, p)

    mesh = build_mesh(height, sd, raster, p, crest)
    patch = contact_patch(mesh)

    assert mesh.is_watertight
    assert mesh.bounds[0][2] == pytest.approx(0.0, abs=0.05)
    assert patch.size > 0
    assert patch[:, 0].max() - patch[:, 0].min() >= 1.5


def test_a_waist_narrower_than_its_neighbours_stays_grounded(
    params: BubbleParams, dumbbell: NDArray[np.float64]
) -> None:
    """The fillet cap must follow the geometric half-width, not the membrane crest:
    a waist between two fat sections pinches sd while the crest stays high, and an
    uncapped fillet lifts the waist off the plate."""
    p = dataclasses.replace(params, base_round_mm=11.0)
    raster = rasterize([dumbbell], p)
    sd = signed_distance(raster.mask, p.resolution)
    height, halfwidth = height_field(sd, p)

    mesh = build_mesh(height, sd, raster, p, halfwidth)
    patch = contact_patch(mesh)
    neck = patch[(patch[:, 0] > 19.0) & (patch[:, 0] < 21.0)]

    assert mesh.is_watertight
    assert neck.size > 0


def test_zero_base_round_keeps_the_wall_square(params: BubbleParams, square: SquareFactory) -> None:
    p = dataclasses.replace(params, base_round_mm=0.0)
    height, sd, raster, crest = puffed_square(square, p)

    mesh = build_mesh(height, sd, raster, p, crest)
    patch = contact_patch(mesh)
    widest = mesh.bounds[1][0] - mesh.bounds[0][0]

    assert patch[:, 0].max() - patch[:, 0].min() == pytest.approx(widest, abs=0.3)


def test_decimation_reduces_faces_and_keeps_it_closed(
    params: BubbleParams, square: SquareFactory
) -> None:
    height, sd, raster, crest = puffed_square(square, params)
    dense = build_mesh(height, sd, raster, params, crest)

    budget = len(dense.faces) // 4
    decimated = build_mesh(
        height, sd, raster, dataclasses.replace(params, target_faces=budget), crest
    )

    assert len(decimated.faces) < len(dense.faces)
    assert decimated.is_watertight


def test_smoothing_keeps_the_mesh_closed_and_the_volume(
    params: BubbleParams, square: SquareFactory
) -> None:
    height, sd, raster, crest = puffed_square(square, params)
    raw = build_mesh(height, sd, raster, params, crest)

    smoothed = build_mesh(
        height, sd, raster, dataclasses.replace(params, smooth_iterations=10), crest
    )

    assert smoothed.is_watertight
    assert smoothed.volume == pytest.approx(raw.volume, rel=0.15)


def test_smoothing_does_not_roll_the_base_over(params: BubbleParams, square: SquareFactory) -> None:
    """Taubin rounds the corner where the chamfer meets the plate, and the first
    layers overhang past 45 degrees again; smoothing has to fade out at the base."""
    p = dataclasses.replace(
        params, puff_mm=4.0, z_steps=40, base_round_mm=2.0, smooth_iterations=40
    )
    height, sd, raster, crest = puffed_square(square, p, size=20.0)

    mesh = build_mesh(height, sd, raster, p, crest)

    assert outward_step(mesh, 0.1, 0.3) < 0.5


def test_smoothing_and_decimation_together_keep_the_shape(
    params: BubbleParams, square: SquareFactory
) -> None:
    """Taubin diverges on the irregular triangles decimation leaves behind, so the
    smoothing pass has to run while the mesh is still dense."""
    p = dataclasses.replace(params, puff_mm=6.0, resolution=5.0)
    height, sd, raster, crest = puffed_square(square, p, size=30.0)
    dense = build_mesh(height, sd, raster, p, crest)

    both = build_mesh(
        height, sd, raster, dataclasses.replace(p, target_faces=5_000, smooth_iterations=12), crest
    )

    assert both.is_watertight
    assert both.volume == pytest.approx(dense.volume, rel=0.03)
    assert both.bounds[1][2] == pytest.approx(dense.bounds[1][2], abs=0.4)
