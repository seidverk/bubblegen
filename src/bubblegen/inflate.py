"""The inflation itself: silhouette in, thickness out.

The letter is treated as a membrane clamped to its outline and pushed up by uniform
pressure, which is what a balloon actually is. The deflection `u` of such a membrane
solves Laplace's equation with a constant load, and `sqrt(2u)` is the thickness:

    laplace(u) = -1 inside the glyph, u = 0 on the outline

For a straight stroke that yields exactly a semicircular cross-section of the stroke's
own half-width, so each stroke inflates to its own size. Unlike a profile built from
the distance to the outline, it is smooth everywhere: no ridge along the centre line,
no crease radiating from a corner, and junctions bulge rather than dent, because a
wider patch of membrane deflects further.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage, sparse
from scipy.sparse.linalg import spsolve

if TYPE_CHECKING:
    from bubblegen.config import BubbleParams
    from bubblegen.raster import Mask

Field = NDArray[np.float64]

SOLVE_PX_PER_MM = 2.0
"""Resolution of the membrane solve. The result is smooth, so a coarse grid is plenty
and it keeps the linear system small; the height field is interpolated back up."""


def height_field(sd: Field, params: BubbleParams) -> Field:
    """Thickness h(x, y) in mm, from the membrane deflection over the silhouette.

    `puff` is a ceiling, not a target: the membrane is never stretched taller than it
    would naturally sit, so a thin stroke stays a thin bubble instead of a sausage.

    Outside the glyph the field keeps the (negative) distance, so the isosurface at 0
    closes exactly on the silhouette.
    """
    mask = sd > 0
    natural = np.sqrt(2.0 * _deflection(mask, params.resolution))
    peak = float(natural.max())
    scale = min(1.0, params.puff_mm / peak) if peak > 0 else 0.0

    return np.asarray(np.where(mask, scale * natural, sd), dtype=np.float64)


def _deflection(mask: Mask, px_per_mm: float) -> Field:
    """Membrane deflection under unit pressure, in mm squared."""
    step = max(1, round(px_per_mm / SOLVE_PX_PER_MM))
    coarse = mask[::step, ::step]
    if not coarse.any():
        return np.zeros_like(mask, dtype=np.float64)

    solved = np.zeros(coarse.shape, dtype=np.float64)
    solved[coarse] = np.clip(_solve_laplace(coarse, step / px_per_mm), 0.0, None)

    zoom = (mask.shape[0] / coarse.shape[0], mask.shape[1] / coarse.shape[1])
    # cubic keeps the interpolated field smooth: bilinear leaves a kink on every
    # coarse cell edge, which the mesh faithfully reproduces as faceting
    upsampled = ndimage.zoom(solved, zoom, order=3)
    # cubic overshoots into negative values next to the clamped outline
    trimmed = np.clip(upsampled[: mask.shape[0], : mask.shape[1]], 0.0, None)
    return np.asarray(trimmed, dtype=np.float64)


def _solve_laplace(mask: Mask, spacing_mm: float) -> Field:
    """Five-point Laplacian on the masked pixels, zero on everything outside."""
    index = np.full(mask.shape, -1, dtype=np.int64)
    count = int(mask.sum())
    index[mask] = np.arange(count)
    own = index[mask]

    rows = [own]
    cols = [own]
    values = [np.full(count, -4.0)]
    for axis, shift in ((0, 1), (0, -1), (1, 1), (1, -1)):
        neighbour = np.roll(index, shift, axis=axis)
        edge: list[slice | int] = [slice(None), slice(None)]
        edge[axis] = 0 if shift == 1 else -1
        neighbour[tuple(edge)] = -1  # rolled around: not a neighbour at all

        found = neighbour[mask]
        inside = found >= 0
        rows.append(own[inside])
        cols.append(found[inside])
        values.append(np.ones(int(inside.sum())))

    laplacian = (
        sparse.coo_matrix(
            (np.concatenate(values), (np.concatenate(rows), np.concatenate(cols))),
            shape=(count, count),
        ).tocsr()
        / spacing_mm**2
    )

    return np.asarray(spsolve(laplacian, np.full(count, -1.0)), dtype=np.float64)
