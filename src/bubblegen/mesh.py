"""Height field to a watertight triangle mesh with a flat, printable bottom."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np
import trimesh
from skimage import measure

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from bubblegen.config import BubbleParams
    from bubblegen.raster import Raster

logger = logging.getLogger(__name__)

OUTSIDE_VALUE = -1e3
"""Padding value that guarantees a closed isosurface at the grid border."""

TAUBIN_LAMB = 0.5
TAUBIN_NU = -0.53
"""Taubin pair: shrink then unshrink, so smoothing keeps the volume."""

DECIMATION_RETRIES = (1.0, 2.0, 4.0)
"""Face budget multipliers tried in order when a tighter budget damages the surface."""

FIDELITY_TOLERANCE_MM = 0.15
"""Surface error decimation may add on top of the marching-cubes discretisation."""

DOME_NORMAL_Z = 0.7
DOME_RIM_MM = 1.0
"""Which faces count as the inflated top: upward facing, and clear of the rim, where
the surface follows the base fillet rather than the height field."""

Z_HEADROOM = 1.15
"""Slack above the tallest point, so the isosurface closes instead of being clipped."""

PLATE_DEPTH = 0.6
"""How far below the plate the grid extends, so the flat bottom closes cleanly."""


def build_mesh(
    height: NDArray[np.float64],
    sd: NDArray[np.float64],
    raster: Raster,
    params: BubbleParams,
) -> trimesh.Trimesh:
    """Marching-cubes the height field, then clean, smooth and decimate it.

    The result is solid between the plate and z = h(x, y), with the outline curving
    down into a flat contact patch: it prints without supports and hangs flush against
    a wall, without the hard right-angle edge of a plain extrusion.
    """
    px_mm = raster.px_per_mm
    z1 = params.puff_mm * Z_HEADROOM
    z0 = -PLATE_DEPTH * params.puff_mm

    zs = np.linspace(z0, z1, params.z_steps)
    dz = float(zs[1] - zs[0])

    h = height[:, :, None]
    z = zs[None, None, :]
    field = np.minimum(h - z, z)

    inset = _base_inset(zs, params.base_radius)
    if inset is not None:
        field = np.minimum(field, sd[:, :, None] - inset[None, None, :])

    field = np.pad(field, 1, mode="constant", constant_values=OUTSIDE_VALUE)
    verts, faces, _normals, _values = measure.marching_cubes(
        field, level=0.0, spacing=(1.0 / px_mm, 1.0 / px_mm, dz)
    )

    # marching cubes returns (row, col, z) = (y, x, z); reorder to x, y, z and undo the pad
    vertices = np.column_stack(
        [
            verts[:, 1] + raster.origin[0] - 1.0 / px_mm,
            verts[:, 0] + raster.origin[1] - 1.0 / px_mm,
            verts[:, 2] + z0 - dz,
        ]
    )

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    _drop_degenerate_faces(mesh)
    mesh.fix_normals()

    # smoothing runs before decimation: Taubin diverges on the irregular triangles
    # decimation leaves behind, which collapses the letter instead of rounding it
    if params.smooth_iterations > 0:
        trimesh.smoothing.filter_taubin(
            mesh, lamb=TAUBIN_LAMB, nu=TAUBIN_NU, iterations=params.smooth_iterations
        )
    return _decimate(mesh, params.target_faces, height, sd, raster, params)


def _base_inset(zs: NDArray[np.float64], radius: float) -> NDArray[np.float64] | None:
    """How far the outline is pulled in at each height, as a quarter-circle fillet.

    `radius` at the plate, nothing from `radius` upwards: the contact patch is the
    silhouette eroded by `radius`, and the wall rolls out to the full silhouette.
    """
    if radius <= 0:
        return None
    rise = np.clip(radius - zs, 0.0, radius)
    return np.asarray(radius - np.sqrt(np.clip(radius**2 - rise**2, 0.0, None)))


def _drop_degenerate_faces(mesh: trimesh.Trimesh) -> None:
    """Remove zero-area faces in place.

    Both marching cubes and quadric decimation emit a handful of them, and a single
    zero-area face is enough to make the surrounding edges look non-manifold.
    """
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()


def _surface_error(
    mesh: trimesh.Trimesh,
    height: NDArray[np.float64],
    sd: NDArray[np.float64],
    raster: Raster,
    rim_mm: float,
) -> float:
    """Worst gap between the inflated top of `mesh` and the height field it follows."""
    centers = mesh.triangles_center
    px = np.clip(
        ((centers[:, 0] - raster.origin[0]) * raster.px_per_mm - 0.5).round().astype(int),
        0,
        height.shape[1] - 1,
    )
    py = np.clip(
        ((centers[:, 1] - raster.origin[1]) * raster.px_per_mm - 0.5).round().astype(int),
        0,
        height.shape[0] - 1,
    )
    target = height[py, px]

    dome = (mesh.face_normals[:, 2] > DOME_NORMAL_Z) & (sd[py, px] > rim_mm)
    if not dome.any():
        return 0.0
    return float(np.abs(centers[dome, 2] - target[dome]).max())


def _decimate(
    mesh: trimesh.Trimesh,
    target_faces: int,
    height: NDArray[np.float64],
    sd: NDArray[np.float64],
    raster: Raster,
    params: BubbleParams,
) -> trimesh.Trimesh:
    """Marching cubes is very dense; trim it to keep STL files sane.

    Quadric decimation is happy to collapse a whole strip of a straight stroke into
    one plate: the error metric sees a developable surface as free to flatten, and the
    letter prints low-poly. So every candidate is checked against the height field it
    should follow, and against watertightness, before it is allowed to replace the
    dense mesh.
    """
    if not target_faces or len(mesh.faces) <= target_faces:
        return mesh

    rim = params.base_radius + DOME_RIM_MM
    budget_error = _surface_error(mesh, height, sd, raster, rim) + FIDELITY_TOLERANCE_MM
    for multiplier in DECIMATION_RETRIES:
        budget = int(target_faces * multiplier)
        if budget >= len(mesh.faces):
            break
        try:
            candidate = mesh.simplify_quadric_decimation(face_count=budget)
        except Exception as exc:  # optional decimation backend missing
            logger.warning("decimation unavailable, keeping dense mesh: %s", exc)
            return mesh

        _drop_degenerate_faces(candidate)
        if not candidate.is_watertight:
            logger.debug("decimation to %d faces was not watertight, retrying", budget)
            continue

        error = _surface_error(candidate, height, sd, raster, rim)
        if error <= budget_error:
            return candidate
        logger.debug("decimation to %d faces was %.2f mm off the surface, retrying", budget, error)

    logger.warning("no face budget kept the surface, keeping %d triangles", len(mesh.faces))
    return mesh
