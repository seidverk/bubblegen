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
DOME_CLEARANCE_MM = 0.3
"""Which faces count as the inflated top: upward facing, and clear of the base fillet,
which pulls the surface away from the height field near the plate."""

Z_HEADROOM = 1.15
"""Slack above the tallest point, so the isosurface closes instead of being clipped."""

PLATE_DEPTH = 0.6
"""How far below the plate the grid extends, as a share of the peak height, so the
flat bottom closes cleanly."""

MIN_PEAK_MM = 0.1
"""Keeps the z grid non-degenerate on a glyph that inflates to nothing."""


def build_mesh(
    height: NDArray[np.float64],
    sd: NDArray[np.float64],
    raster: Raster,
    params: BubbleParams,
    halfwidth: NDArray[np.float64],
) -> trimesh.Trimesh:
    """Marching-cubes the height field, then clean, smooth and decimate it.

    The result is solid between the plate and z = h(x, y), with the outline curving
    down into a flat contact patch: it prints without supports and hangs flush against
    a wall, without the hard right-angle edge of a plain extrusion. The fillet radius
    is capped at the local stroke half-width, so no stroke is eroded off the plate.
    """
    px_mm = raster.px_per_mm
    peak = max(float(height.max()), MIN_PEAK_MM)
    z1 = peak * Z_HEADROOM
    z0 = -PLATE_DEPTH * peak

    zs = np.linspace(z0, z1, params.z_steps)
    dz = float(zs[1] - zs[0])

    h = height[:, :, None]
    z = zs[None, None, :]
    field = np.minimum(h - z, z)

    inset = _base_inset(zs, np.minimum(params.base_radius, halfwidth))
    if inset is not None:
        field = np.minimum(field, sd[:, :, None] - inset)

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
        _smooth_keeping_base(mesh, params, dz)
    return _decimate(mesh, params.target_faces, height, raster, params)


def _base_inset(
    zs: NDArray[np.float64], radius: float | NDArray[np.float64]
) -> NDArray[np.float64] | None:
    """How far the outline is pulled in at each height: fillet arc into a 45° chamfer.

    The arc rolls out to the full silhouette at `radius` height, but a full quarter
    circle would leave the plate horizontally and layers near the plate would print
    on air. So below the 45° tangent point the profile continues as a straight
    chamfer: the contact patch is the silhouette eroded by (2 - sqrt(2)) * radius.

    `radius` may be a per-pixel map; the result then broadcasts to (y, x, z).
    """
    r = np.asarray(radius, dtype=np.float64)
    if np.all(r <= 0):
        return None
    if r.ndim:
        r = r[:, :, None]
    z = np.clip(zs, 0.0, r)
    rise = r - z
    arc = r - np.sqrt(np.clip(r**2 - rise**2, 0.0, None))
    z45 = r * (1.0 - np.sqrt(0.5))
    chamfer = 2.0 * z45 - z
    return np.asarray(np.where(z < z45, chamfer, arc))


def _smooth_keeping_base(mesh: trimesh.Trimesh, params: BubbleParams, dz: float) -> None:
    """Taubin smoothing, vertically pinned at the plate but free in its plane.

    Smoothing exists to iron ribbing out of the walls. Unweighted passes roll the
    contact edge over until the first layers overhang past 45° again, so the vertical
    component fades to nothing over the couple of grid cells the roll reaches. The
    in-plane component stays at full strength all the way down: it is what cleans the
    marching-cubes jitter off the bottom edge, and it cannot lift anything.
    """
    ramp = 2.0 * dz if params.base_radius > 0 else 0.0
    weight: NDArray[np.float64] | np.float64
    if ramp > 0:
        vertical = np.clip(mesh.vertices[:, 2] / ramp, 0.0, 1.0)
        ones = np.ones_like(vertical)
        weight = np.column_stack([ones, ones, vertical])
    else:
        weight = np.float64(1.0)
    laplacian = trimesh.smoothing.laplacian_calculation(mesh)
    vertices = mesh.vertices.copy().view(np.ndarray)
    for index in range(params.smooth_iterations):
        dot = laplacian.dot(vertices) - vertices
        if index % 2 == 0:
            vertices += TAUBIN_LAMB * weight * dot
        else:
            vertices -= TAUBIN_NU * weight * dot
    mesh.vertices = vertices


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
    raster: Raster,
    floor_mm: float,
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

    dome = (mesh.face_normals[:, 2] > DOME_NORMAL_Z) & (target > floor_mm)
    if not dome.any():
        return 0.0
    return float(np.abs(centers[dome, 2] - target[dome]).max())


def _decimate(
    mesh: trimesh.Trimesh,
    target_faces: int,
    height: NDArray[np.float64],
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

    floor = params.base_radius + DOME_CLEARANCE_MM
    budget_error = _surface_error(mesh, height, raster, floor) + FIDELITY_TOLERANCE_MM
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

        error = _surface_error(candidate, height, raster, floor)
        if error <= budget_error:
            return candidate
        logger.debug("decimation to %d faces was %.2f mm off the surface, retrying", budget, error)

    logger.warning("no face budget kept the surface, keeping %d triangles", len(mesh.faces))
    return mesh
