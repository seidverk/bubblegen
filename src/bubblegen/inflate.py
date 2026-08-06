"""The inflation itself: signed distance in, half-thickness out."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from bubblegen.config import Profile

if TYPE_CHECKING:
    from bubblegen.config import BubbleParams

Field = NDArray[np.float64]

SUPER_EXPONENT = 3.0

_EDGE_PROFILES: dict[Profile, Callable[[Field], Field]] = {
    # t runs 0 at the silhouette to 1 where full thickness is reached
    Profile.SPHERE: lambda t: np.sqrt(np.clip(1.0 - (1.0 - t) ** 2, 0.0, None)),
    Profile.SMOOTH: lambda t: t * t * (3.0 - 2.0 * t),
    Profile.SUPER: lambda t: (1.0 - (1.0 - t) ** SUPER_EXPONENT) ** (1.0 / SUPER_EXPONENT),
}


def height_field(sd: Field, params: BubbleParams) -> Field:
    """Half-thickness h(x, y) in mm from the signed distance field.

    Outside the glyph the field keeps the (negative) distance, so the isosurface
    at 0 closes exactly on the silhouette.
    """
    deep = np.clip(sd, 0.0, None)
    deepest = float(deep.max())
    puff = params.puff_for(deepest)

    t = np.clip(sd / params.roll_for(deepest), 0.0, 1.0)
    edge = _EDGE_PROFILES[params.profile](t)
    h = puff * edge

    if params.dome > 0.0:
        # gentle global bulge: proportional to how deep inside the stroke we are
        h = h + puff * params.dome * edge * (deep / (deepest or 1.0))

    return np.asarray(np.where(sd > 0, h, sd), dtype=np.float64)
