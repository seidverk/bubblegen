"""Height field to a watertight triangle mesh."""

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

DECIMATION_RETRIES = (1.0, 1.5, 2.0)
"""Face budget multipliers tried in order when decimation breaks watertightness."""

Z_HEADROOM = 1.15
"""Slack above the tallest point, so the isosurface closes instead of being clipped."""

FLAT_BACK_DEPTH = 0.6
"""How far below z = 0 the grid extends when the back is flat."""


def build_mesh(
    height: NDArray[np.float64], raster: Raster, params: BubbleParams
) -> trimesh.Trimesh:
    """Marching-cubes the height field, then clean, decimate and smooth it."""
    px_mm = raster.px_per_mm
    puff = params.puff_mm
    # the dome pushes the peak above puff, so the grid has to follow it
    z1 = puff * (1.0 + params.dome) * Z_HEADROOM
    z0 = -FLAT_BACK_DEPTH * puff if params.flat_back else -z1

    zs = np.linspace(z0, z1, params.z_steps)
    dz = float(zs[1] - zs[0])

    h = height[:, :, None]
    z = zs[None, None, :]
    # flat back: solid between z = 0 and z = h, support-free. otherwise: symmetric pillow.
    field = np.minimum(h - z, z) if params.flat_back else h - np.abs(z)

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

    mesh = _decimate(mesh, params.target_faces)
    if params.smooth_iterations > 0:
        trimesh.smoothing.filter_taubin(
            mesh, lamb=TAUBIN_LAMB, nu=TAUBIN_NU, iterations=params.smooth_iterations
        )
    return mesh


def _drop_degenerate_faces(mesh: trimesh.Trimesh) -> None:
    """Remove zero-area faces in place.

    Both marching cubes and quadric decimation emit a handful of them, and a single
    zero-area face is enough to make the surrounding edges look non-manifold.
    """
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()


def _decimate(mesh: trimesh.Trimesh, target_faces: int) -> trimesh.Trimesh:
    """Marching cubes is very dense; trim it to keep STL files sane.

    Decimation can still break manifoldness on tight geometry, so each cleaned
    candidate is verified and retried with a looser budget before giving up on the
    (valid) dense mesh.
    """
    if not target_faces or len(mesh.faces) <= target_faces:
        return mesh

    for multiplier in DECIMATION_RETRIES:
        budget = int(target_faces * multiplier)
        try:
            candidate = mesh.simplify_quadric_decimation(face_count=budget)
        except Exception as exc:  # optional decimation backend missing
            logger.warning("decimation unavailable, keeping dense mesh: %s", exc)
            return mesh
        _drop_degenerate_faces(candidate)
        if candidate.is_watertight:
            return candidate
        logger.debug("decimation to %d faces was not watertight, retrying", budget)

    logger.warning("decimation kept breaking the mesh, keeping the dense version")
    return mesh
