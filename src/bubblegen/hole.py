"""Keyring hole: where to put it, and how to drill it."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal

import numpy as np
import trimesh

from bubblegen.errors import MeshError

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from bubblegen.config import BubbleParams
    from bubblegen.raster import Raster

logger = logging.getLogger(__name__)

BAND_MM = 0.5
"""Height of the band searched for a centred hole position."""

CYLINDER_SECTIONS = 64


def find_hole_center(
    sd: NDArray[np.float64],
    raster: Raster,
    params: BubbleParams,
    where: Literal["top", "bottom"] = "top",
) -> tuple[float, float] | None:
    """Hole centre in mm that still leaves `hole_wall_mm` of material, or None."""
    needed = params.hole_radius + params.hole_wall_mm
    candidates = sd >= needed
    if not candidates.any():
        return None

    ys, xs = np.nonzero(candidates)
    band_px = max(1, int(BAND_MM * raster.px_per_mm))
    band = ys >= ys.max() - band_px if where == "top" else ys <= ys.min() + band_px

    band_xs, band_ys = xs[band], ys[band]
    # within the band, pick the pixel closest to its horizontal centre
    pick = int(np.argmin(np.abs(band_xs - band_xs.mean())))
    return raster.to_mm((int(band_xs[pick]), int(band_ys[pick])))


def drill_hole(
    mesh: trimesh.Trimesh, center: tuple[float, float], params: BubbleParams
) -> trimesh.Trimesh:
    """Subtract a through-cylinder as a real boolean.

    A boolean rather than a notch in the scalar field: a min() crease in the field
    makes marching cubes emit non-manifold edges.
    """
    cylinder = trimesh.creation.cylinder(
        radius=params.hole_radius,
        height=params.puff_mm * 8,
        sections=CYLINDER_SECTIONS,
    )
    cylinder.apply_translation([center[0], center[1], 0.0])

    try:
        drilled: trimesh.Trimesh = trimesh.boolean.difference([mesh, cylinder])
    except Exception as exc:  # boolean backend errors are engine-specific
        raise MeshError(f"hole boolean failed: {exc}") from exc

    if drilled is None or len(drilled.faces) == 0:
        raise MeshError("hole boolean produced an empty mesh")
    return drilled
