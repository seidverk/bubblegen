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

RIDGE_SHARE = 0.99
RIDGE_REACH_MM = 2.0
"""How close to the tallest point nearby a centre-line pixel has to stand to count as a
crest. The medial axis also runs into every concave corner, where the letter is not at
its thickest at all, and taking those pixels for crests raises a pimple there."""

CREST_FLOOR_MM = 1e-6
"""Keeps the division by the crest height defined on a hairline glyph."""


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

    Both are solved on the raster grid itself. A coarser grid is tempting, since these
    fields are smooth, but a steep flank shows every wrinkle the interpolation back up
    leaves behind, as ribbing along the walls.
    """
    thickness = np.zeros(mask.shape, dtype=np.float64)
    crest = np.zeros(mask.shape, dtype=np.float64)
    limit = 0.0
    if mask.any():
        deflection = _solve(mask, 1.0 / px_per_mm, load=-1.0)
        thickness[mask] = np.sqrt(2.0 * np.clip(deflection, 0.0, None))

        axis = _crest_line(thickness, mask, px_per_mm)
        crest = _spread(thickness, axis, px_per_mm) if axis.any() else thickness.copy()
        crest = np.maximum(crest, thickness)

        body = axis & _largest_piece(mask)
        if body.any():
            # the tenth percentile, not the minimum: the centre line runs out to the tip
            # of every stroke, where the tube is meant to round off anyway
            limit = PUFF_SLACK * float(np.percentile(thickness[body], NECK_PERCENTILE))

    return thickness, np.maximum(crest, CREST_FLOOR_MM), limit


def _crest_line(thickness: Field, mask: Mask, px_per_mm: float) -> Mask:
    """The glyph's centre line, minus the branches that run into concave corners.

    The medial axis passes close to every reflex corner, and the membrane is nowhere
    near its local peak there. Treating those pixels as crests puts a pimple on the
    inside of every junction, so a pixel only counts if it stands within `RIDGE_SHARE`
    of the tallest point around it.
    """
    axis: Mask = mask & medial_axis(mask)
    if not axis.any():
        return axis
    nearby = ndimage.maximum_filter(thickness, size=int(RIDGE_REACH_MM * px_per_mm) | 1)
    crest: Mask = axis & (thickness >= RIDGE_SHARE * nearby)
    return crest if crest.any() else axis


def _largest_piece(mask: Mask) -> Mask:
    """The glyph's body, without its accents.

    An acute or a dot is a small piece of its own: it is meant to stay thin, and letting
    it speak for the letter would report a thickness far below what the body can hold.
    """
    labels, count = ndimage.label(mask)
    if count <= 1:
        return mask
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    return np.asarray(labels == int(np.argmax(sizes)))


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
