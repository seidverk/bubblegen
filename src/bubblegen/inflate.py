"""The inflation itself: silhouette in, thickness out.

The letter is treated as a membrane clamped to its outline and pushed up by uniform
pressure, which is what a balloon actually is. The deflection `u` of such a membrane
solves Laplace's equation with a constant load, and `sqrt(2u)` is the thickness:

    laplace(u) = -1 inside the glyph, u = 0 on the outline

That is smooth everywhere, so there is no ridge along the centre line and no crease
radiating from a corner, the way a profile built from the distance to the outline has.

The membrane on its own is only half the answer: its height follows the local stroke
width, so every narrow section of an O or a G is pinched into a groove. A doughnut has
one tube thickness however its outline wanders, so the height is measured relative to
the crest the membrane reaches over the nearest centre line, and then set to `puff`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage, sparse
from scipy.sparse.linalg import spsolve
from skimage.morphology import medial_axis

from bubblegen.config import PUFF_SLACK

if TYPE_CHECKING:
    from bubblegen.config import BubbleParams
    from bubblegen.raster import Mask

Field = NDArray[np.float64]

NECK_PERCENTILE = 10.0
"""Which centre-line height counts as "the narrowest section" of a glyph."""

CREST_BLUR_MM = 2.0
"""Smoothing of the crest reference, in mm."""

CREST_FLOOR_MM = 1e-6
"""Keeps the division by the crest height defined on a hairline glyph."""

SOLVE_PX_PER_MM = 2.0
"""Resolution of both solves. The fields are smooth, so a coarse grid is plenty and it
keeps the linear systems small; they are interpolated back up afterwards."""


def uniform_limit(sd: Field, params: BubbleParams) -> float:
    """Thickest even tube this glyph can hold, in mm.

    A section can stand as tall as it is wide and no taller, so the narrowest section
    sets the limit. Ask for more and the narrow sections keep their own height while the
    rest goes higher, which shows up as a notch across the thin part of an O or a G.
    """
    _thickness, _crest, limit = _membrane(sd > 0, params.resolution)
    return limit


def height_field(sd: Field, params: BubbleParams) -> Field:
    """Thickness h(x, y) in mm, from the membrane deflection over the silhouette.

    `puff` is honoured up to the width of the stroke it sits on, so a thin stroke can
    become a round tube but never a sausage. `fullness` then shapes the cross-section
    from a plain semicircle towards a balloon.

    Outside the glyph the field keeps the (negative) distance, so the isosurface at 0
    closes exactly on the silhouette.
    """
    mask = sd > 0
    natural, crest, _limit = _membrane(mask, params.resolution)
    if natural.max() <= 0:
        return np.asarray(np.where(mask, 0.0, sd), dtype=np.float64)

    # the membrane alone stops at half the stroke width, so reaching a full round tube
    # means stretching it - never further, or the letter stands taller than it is wide
    amplitude = np.minimum(params.puff_mm, PUFF_SLACK * crest)
    h = amplitude * (natural / crest) ** (2.0 / params.fullness)

    return np.asarray(np.where(mask, h, sd), dtype=np.float64)


def _membrane(mask: Mask, px_per_mm: float) -> tuple[Field, Field, float]:
    """Membrane thickness and the crest height it is measured against, both in mm.

    The crest is the thickness the membrane reaches over the glyph's centre line, carried
    across the whole glyph so that every pixel knows how tall its own stroke stands.
    """
    step = max(1, round(px_per_mm / SOLVE_PX_PER_MM))
    coarse = mask[::step, ::step]
    spacing = step / px_per_mm

    thickness = np.zeros(coarse.shape, dtype=np.float64)
    crest = np.zeros(coarse.shape, dtype=np.float64)
    limit = 0.0
    if coarse.any():
        deflection = _solve(coarse, spacing, load=-1.0)
        thickness[coarse] = np.sqrt(2.0 * np.clip(deflection, 0.0, None))

        axis = coarse & medial_axis(coarse)
        crest = _spread(thickness, axis, 1.0 / spacing) if axis.any() else thickness.copy()
        if axis.any():
            # the tenth percentile, not the minimum: the centre line runs out to the tip
            # of every stroke, where the tube is meant to round off anyway
            limit = PUFF_SLACK * float(np.percentile(thickness[axis], NECK_PERCENTILE))

    full_thickness = _upsample(thickness, mask.shape)
    # the two fields are interpolated apart, and a crest below the surface it measures
    # would push the letter past the thickness that was asked for
    full_crest = np.maximum(_upsample(crest, mask.shape), full_thickness)
    return full_thickness, np.maximum(full_crest, CREST_FLOOR_MM), limit


def _spread(thickness: Field, axis: Mask, px_per_mm: float) -> Field:
    """Carry the centre-line thickness across the glyph, then smooth the seams.

    Every pixel takes the thickness of the centre line nearest to it. Where two centre
    lines compete that lookup jumps, and the mesh turns the jump into a crease, so the
    result is blurred; the value only sets how tall the tube is, and stroke widths vary
    slowly, so a generous blur costs nothing.
    """
    nearest = ndimage.distance_transform_edt(~axis, return_distances=False, return_indices=True)
    lifted = thickness[tuple(nearest)]
    return np.asarray(
        ndimage.gaussian_filter(lifted, sigma=CREST_BLUR_MM * px_per_mm), dtype=np.float64
    )


def _upsample(coarse: Field, shape: tuple[int, ...]) -> Field:
    """Back to raster resolution, cubically: bilinear leaves a kink on every cell edge,
    which the mesh faithfully reproduces as faceting."""
    zoom = (shape[0] / coarse.shape[0], shape[1] / coarse.shape[1])
    upsampled = ndimage.zoom(coarse, zoom, order=3)
    # cubic overshoots into negative values next to the clamped outline
    trimmed = np.clip(upsampled[: shape[0], : shape[1]], 0.0, None)
    return np.asarray(trimmed, dtype=np.float64)


def _solve(free: Mask, spacing_mm: float, load: float) -> Field:
    """Five-point Laplacian over `free`, returning the solution on those pixels.

    Everything beyond `free` is held at zero: the membrane pinned to the outline.
    """
    index = np.full(free.shape, -1, dtype=np.int64)
    count = int(free.sum())
    index[free] = np.arange(count)
    own = index[free]

    neighbour_rows: list[NDArray[np.int64]] = []
    neighbour_cols: list[NDArray[np.int64]] = []
    diagonal = np.zeros(count)
    rhs = np.full(count, load * spacing_mm**2)

    for axis, shift in ((0, 1), (0, -1), (1, 1), (1, -1)):
        shifted = np.roll(index, shift, axis=axis)
        border: list[slice | int] = [slice(None), slice(None)]
        border[axis] = 0 if shift == 1 else -1
        shifted[tuple(border)] = -1  # rolled around: not a neighbour at all

        found = shifted[free]
        solved_here = found >= 0
        neighbour_rows.append(own[solved_here])
        neighbour_cols.append(found[solved_here])

    # a pinned outline contributes its zero with full weight, so the stencil stays at
    # four however many neighbours are actually inside
    diagonal[:] = -4.0

    rows = np.concatenate([own, *neighbour_rows])
    cols = np.concatenate([own, *neighbour_cols])
    data = np.concatenate([diagonal, np.ones(len(rows) - count)])
    laplacian = sparse.coo_matrix((data, (rows, cols)), shape=(count, count)).tocsr()

    return np.asarray(spsolve(laplacian, rhs), dtype=np.float64)
