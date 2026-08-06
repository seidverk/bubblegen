"""Contours to a pixel mask, and the mask to a signed distance field."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from matplotlib.path import Path as MplPath
from numpy.typing import NDArray
from scipy import ndimage

if TYPE_CHECKING:
    from collections.abc import Sequence

    from bubblegen.config import BubbleParams
    from bubblegen.fonts import Contour

Mask = NDArray[np.bool_]
Field = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class Raster:
    """A boolean glyph mask plus the mapping back to millimetres."""

    mask: Mask
    origin: tuple[float, float]
    """mm coordinates of the lower-left corner of pixel (0, 0)."""
    px_per_mm: float

    def to_mm(self, pixel: tuple[int, int]) -> tuple[float, float]:
        px, py = pixel
        return (
            self.origin[0] + (px + 0.5) / self.px_per_mm,
            self.origin[1] + (py + 0.5) / self.px_per_mm,
        )

    def to_pixel(self, point: tuple[float, float]) -> tuple[int, int]:
        x, y = point
        return (
            round((x - self.origin[0]) * self.px_per_mm - 0.5),
            round((y - self.origin[1]) * self.px_per_mm - 0.5),
        )

    def with_mask(self, mask: Mask) -> Raster:
        return Raster(mask=mask, origin=self.origin, px_per_mm=self.px_per_mm)


def rasterize(contours: Sequence[Contour], params: BubbleParams) -> Raster:
    """Rasterize contours (in mm) to a boolean mask with a blank margin."""
    points = np.vstack(contours)
    lo = points.min(axis=0) - params.margin
    hi = points.max(axis=0) + params.margin
    px_mm = params.resolution

    width = math.ceil((hi[0] - lo[0]) * px_mm)
    height = math.ceil((hi[1] - lo[1]) * px_mm)

    xs = lo[0] + (np.arange(width) + 0.5) / px_mm
    ys = lo[1] + (np.arange(height) + 0.5) / px_mm
    gx, gy = np.meshgrid(xs, ys)
    grid = np.column_stack([gx.ravel(), gy.ravel()])

    # Test each contour separately and XOR them (even-odd rule).
    # matplotlib's containment test is unreliable on compound paths, and even-odd
    # is correct for font outlines: counters simply flip the state.
    mask = np.zeros(height * width, dtype=bool)
    for contour in contours:
        poly = MplPath(np.vstack([contour, contour[:1]]), closed=True)
        mask ^= poly.contains_points(grid)

    return Raster(
        mask=mask.reshape(height, width),
        origin=(float(lo[0]), float(lo[1])),
        px_per_mm=px_mm,
    )


def dilate(mask: Mask, px_per_mm: float, radius: float) -> Mask:
    if radius <= 0:
        return mask
    outside: Field = ndimage.distance_transform_edt(~mask) / px_per_mm
    return mask | (outside <= radius)


def erode(mask: Mask, px_per_mm: float, radius: float) -> Mask:
    if radius <= 0:
        return mask
    inside: Field = ndimage.distance_transform_edt(mask) / px_per_mm
    return inside > radius


def soften(mask: Mask, px_per_mm: float, radius: float) -> Mask:
    """Round the silhouette itself — this is what makes letters read as 'bubble'.

    Closing (dilate+erode) rounds inner corners and fuses strokes that nearly touch;
    opening (erode+dilate) rounds the sharp outer tips (A apex, W, Ж, Æ).
    """
    if radius <= 0:
        return mask
    closed = erode(dilate(mask, px_per_mm, radius), px_per_mm, radius)
    return dilate(erode(closed, px_per_mm, radius), px_per_mm, radius)


def signed_distance(mask: Mask, px_per_mm: float) -> Field:
    """Signed distance in mm: positive inside the glyph, negative outside."""
    inside = ndimage.distance_transform_edt(mask) / px_per_mm
    outside = ndimage.distance_transform_edt(~mask) / px_per_mm
    return np.asarray(inside - outside, dtype=np.float64)
