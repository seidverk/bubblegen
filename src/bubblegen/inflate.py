"""The inflation itself: signed distance in, thickness out."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage

from bubblegen.config import Profile
from bubblegen.raster import local_thickness

if TYPE_CHECKING:
    from bubblegen.config import BubbleParams

Field = NDArray[np.float64]

SUPER_EXPONENT = 3.0

THICKNESS_BLUR_MM = 0.6
"""Local thickness steps between disk radii; blurring it keeps the surface C1."""

_EDGE_PROFILES: dict[Profile, Callable[[Field], Field]] = {
    # t runs 0 at the silhouette to 1 at the centre line of the stroke
    Profile.SPHERE: lambda t: np.sqrt(np.clip(1.0 - (1.0 - t) ** 2, 0.0, None)),
    Profile.SMOOTH: lambda t: t * t * (3.0 - 2.0 * t),
    Profile.SUPER: lambda t: (1.0 - (1.0 - t) ** SUPER_EXPONENT) ** (1.0 / SUPER_EXPONENT),
}


def height_field(sd: Field, params: BubbleParams) -> Field:
    """Thickness h(x, y) in mm from the signed distance field.

    Each stroke is inflated to its own width: the profile is normalised by the local
    stroke thickness, so it arrives at the centre line flat instead of building a tent
    ridge, and a thin stroke becomes a thin tube rather than a tall sausage.

    Outside the glyph the field keeps the (negative) distance, so the isosurface at 0
    closes exactly on the silhouette.
    """
    thickness = _stroke_thickness(sd, params)
    amplitude = np.minimum(params.puff_mm, thickness)
    reach = thickness if params.roll_mm is None else np.full_like(sd, params.roll_mm)

    t = np.clip(sd / np.maximum(reach, 1e-6), 0.0, 1.0)
    h = amplitude * _EDGE_PROFILES[params.profile](t)

    return np.asarray(np.where(sd > 0, h, sd), dtype=np.float64)


def _stroke_thickness(sd: Field, params: BubbleParams) -> Field:
    """Local stroke half-width, smoothed just enough to leave no visible steps.

    The blur is weighted by the glyph itself: an ordinary blur would drag the value
    towards the zeros outside, which shows up as a sharpened rim.
    """
    thickness = local_thickness(sd, params.resolution)
    sigma = THICKNESS_BLUR_MM * params.resolution
    inside = (sd > 0).astype(np.float64)
    weight = ndimage.gaussian_filter(inside, sigma=sigma)
    smoothed = ndimage.gaussian_filter(thickness * inside, sigma=sigma) / np.maximum(weight, 1e-6)
    return np.asarray(np.where(sd > 0, smoothed, 0.0), dtype=np.float64)
