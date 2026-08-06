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

ROUND_BACKOFF = 0.7
"""Factor the rounding radius shrinks by when the glyph cannot take it."""

MIN_ROUND_MM = 0.2
"""Below this the rounding is invisible; give up instead of iterating."""

MIN_AREA_RATIO = 0.75
"""Rounding trims tips; taking off more than this is damage, not rounding."""


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
    # a distance transform needs something to measure against: with no foreground
    # (or, below, no background) scipy returns garbage rather than an empty result
    if radius <= 0 or not mask.any():
        return mask
    outside: Field = ndimage.distance_transform_edt(~mask) / px_per_mm
    return mask | (outside <= radius)


def erode(mask: Mask, px_per_mm: float, radius: float) -> Mask:
    if radius <= 0 or mask.all():
        return mask
    inside: Field = ndimage.distance_transform_edt(mask) / px_per_mm
    return inside > radius


def soften(mask: Mask, px_per_mm: float, radius: float) -> Mask:
    """Round the sharp outer tips of the silhouette (A apex, W, Ж, Æ).

    Opening only: erode, then dilate back. The matching closing would round inner
    corners too, but it bridges every gap narrower than its radius, which fills the
    apertures of S, C and G and leaves a blob. Inner corners are left to the inflation,
    which rounds them in 3D anyway.
    """
    if radius <= 0:
        return mask
    return dilate(erode(mask, px_per_mm, radius), px_per_mm, radius)


def enclosed_gaps(mask: Mask) -> int:
    """Count background regions fully enclosed by the glyph: its counters."""
    labels, count = ndimage.label(~mask)
    if count == 0:
        return 0
    border = np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]])
    reaches_outside = set(np.unique(border).tolist())
    return sum(1 for label in range(1, count + 1) if label not in reaches_outside)


def round_silhouette(mask: Mask, px_per_mm: float, radius: float) -> tuple[Mask, float]:
    """Round the outline by as much as the glyph tolerates.

    Every piece of the glyph is rounded on its own. Erosion deletes anything thinner
    than twice the radius, so a radius the body of an Ö takes would wipe out the dots
    of its umlaut, and backing the whole glyph off to what the dots can take would
    leave the body barely rounded.

    Returns the rounded mask and the radius the body of the glyph ended up with.
    """
    labels, count = ndimage.label(mask)
    if count <= 1:
        return _round_piece(mask, px_per_mm, radius)

    rounded = np.zeros_like(mask)
    body = int(np.argmax(np.bincount(labels.ravel())[1:])) + 1
    body_radius = 0.0
    for piece in range(1, count + 1):
        piece_rounded, used = _round_piece(labels == piece, px_per_mm, radius)
        rounded |= piece_rounded
        if piece == body:
            body_radius = used
    return rounded, body_radius


def _round_piece(piece: Mask, px_per_mm: float, radius: float) -> tuple[Mask, float]:
    """Round one connected piece, backing the radius off until the piece survives it."""
    counters = enclosed_gaps(piece)
    area = piece.sum()

    attempt = radius
    while attempt >= MIN_ROUND_MM:
        rounded = soften(piece, px_per_mm, attempt)
        if (
            rounded.any()
            and enclosed_gaps(rounded) == counters
            and rounded.sum() / area >= MIN_AREA_RATIO
        ):
            return rounded, attempt
        attempt *= ROUND_BACKOFF

    return piece, 0.0


def signed_distance(mask: Mask, px_per_mm: float) -> Field:
    """Signed distance in mm: positive inside the glyph, negative outside."""
    inside = ndimage.distance_transform_edt(mask) / px_per_mm
    outside = ndimage.distance_transform_edt(~mask) / px_per_mm
    return np.asarray(inside - outside, dtype=np.float64)
