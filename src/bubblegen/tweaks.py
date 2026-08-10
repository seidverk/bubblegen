"""Per-letter silhouette surgery: reshape one part of a glyph before inflation.

A font fixes every glyph's proportions, and a bubble letter sometimes wants one part
different: E's middle arm is half the width of its neighbours in most display faces, so
it inflates lower and reads as flattened however hard the letter is blown up.

Three operations, all on the outline points, so the pipeline downstream never sees a seam:
`stretch` pulls an extremity outward, `thicken` pushes a band's two edges apart, and
`deepen` cuts a notch further into the letter. Thickening is what fixes a flat arm -
inflation follows the local stroke width, so a wider arm stands taller on its own -
while deepening is what fixes a letter that reads as a blob with dents, by trading spine
for arm without moving the arm tips.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from bubblegen.errors import TweaksError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import NDArray

    from bubblegen.fonts import Contour

DEFAULT_FEATHER_MM = 3.0
"""Softening of the band edges when the file does not say."""

_STRETCH_KEYS = {"band", "beyond", "dx", "dy", "feather"}
_THICKEN_KEYS = {"band", "beyond", "dy", "feather"}
_DEEPEN_KEYS = {"band", "beyond", "dx", "feather"}


@dataclass(frozen=True, slots=True)
class _BandOp:
    """Shared geometry of both operations: a band across the glyph, softened at its edges."""

    band: tuple[float, float]
    """Which slice of the perpendicular extent is affected, as fractions of the bbox."""

    beyond: float
    """Fraction of the other axis, from the anchor side, where the effect begins."""

    feather: float = DEFAULT_FEATHER_MM
    """Ramp width outside the band edges, in mm, so the effect fades instead of tearing.

    It is in millimetres while `band` is in fractions, so a band that fits between two
    arms can still reach into a neighbour: keep it under the gap.
    """

    def _validate_band(self) -> None:
        lo, hi = self.band
        if not 0.0 <= lo < hi <= 1.0:
            raise ValueError(f"band must be an increasing pair within 0..1, got {self.band}")
        if not 0.0 <= self.beyond < 1.0:
            raise ValueError(f"beyond must be within 0..1, got {self.beyond}")
        if self.feather < 0.0:
            raise ValueError(f"feather must not be negative, got {self.feather}")


@dataclass(frozen=True, slots=True)
class StretchOp(_BandOp):
    """Pull one extremity of a glyph outward.

    The pulled side follows the delta's sign: positive dx pulls the right edge right,
    negative dy pulls the bottom edge down. Points between the anchor side and `beyond`
    stay put; the rest move proportionally, so the extremity travels the full delta and
    the outline never folds.
    """

    dx: float = 0.0
    dy: float = 0.0
    """Pull distance in mm; exactly one of the two."""

    def __post_init__(self) -> None:
        if (self.dx == 0.0) == (self.dy == 0.0):
            raise ValueError("exactly one of dx or dy must be non-zero")
        self._validate_band()


@dataclass(frozen=True, slots=True)
class ThickenOp(_BandOp):
    """Push a band's two edges apart, widening the stroke that lies in it.

    Symmetric about the band's centre, so the letter keeps its overall height: the edge
    above the centre rises by `dy`, the one below drops by it. Only the part beyond
    `beyond` moves, which keeps the spine of a letter where it was.
    """

    dy: float = 0.0
    """How far each edge moves outward, in mm."""

    def __post_init__(self) -> None:
        if self.dy <= 0.0:
            raise ValueError(f"dy must be positive, got {self.dy}")
        self._validate_band()


@dataclass(frozen=True, slots=True)
class DeepenOp(_BandOp):
    """Cut a notch further into the letter, trading spine for arm.

    The notch floor - the rightmost outline point inside the band - moves inward by `dx`,
    and so do the arm roots around it, but the arm tips do not: the effect is windowed to
    end at the floor, which is what stops the feather from dragging the tips back with it.
    """

    dx: float = 0.0
    """How far the notch floor moves toward the spine, in mm."""

    def __post_init__(self) -> None:
        if self.dx <= 0.0:
            raise ValueError(f"dx must be positive, got {self.dx}")
        self._validate_band()


Op = StretchOp | ThickenOp | DeepenOp
Tweaks = Mapping[str, tuple[Op, ...]]


def load_tweaks(path: Path | str) -> dict[str, tuple[Op, ...]]:
    """Read a TOML file mapping single characters to their ops.

    The order is always deepen, then thicken, then stretch, whatever order the file lists
    them in: each one works on the shape the previous one left, so a stretch lengthens the
    arm a deepen has already freed from the spine.
    """
    path = Path(path)
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise TweaksError(f"cannot read tweaks {path}: {exc}") from exc

    tweaks: dict[str, tuple[Op, ...]] = {}
    for char, table in data.items():
        if len(char) != 1:
            raise TweaksError(f"{path}: key {char!r} is not a single character")
        if not isinstance(table, dict) or not set(table) <= {"stretch", "thicken", "deepen"}:
            raise TweaksError(
                f"{path}: [{char}] may only hold 'deepen', 'thicken' and 'stretch' lists"
            )
        ops: list[Op] = [_parse(raw, DeepenOp, char, path) for raw in table.get("deepen", ())]
        ops += [_parse(raw, ThickenOp, char, path) for raw in table.get("thicken", ())]
        ops += [_parse(raw, StretchOp, char, path) for raw in table.get("stretch", ())]
        tweaks[char] = tuple(ops)
    return tweaks


def _parse(raw: dict[str, Any], kind: type[Op], char: str, path: Path) -> Op:
    allowed = {ThickenOp: _THICKEN_KEYS, DeepenOp: _DEEPEN_KEYS}.get(kind, _STRETCH_KEYS)
    unknown = set(raw) - allowed
    if unknown:
        raise TweaksError(f"{path}: [{char}] {kind.__name__} has unknown keys {sorted(unknown)}")
    try:
        kwargs = dict(raw)
        kwargs["band"] = tuple(float(v) for v in raw.get("band", ()))
        for key in ("beyond", "dx", "dy", "feather"):
            if key in kwargs:
                kwargs[key] = float(kwargs[key])
        return kind(**kwargs)
    except (TypeError, ValueError) as exc:
        raise TweaksError(f"{path}: [{char}]: {exc}") from exc


def apply_tweaks(contours: list[Contour], ops: Sequence[Op]) -> list[Contour]:
    """Apply each op in order; every op sees the glyph the previous one left."""
    out = [np.array(contour, dtype=np.float64) for contour in contours]
    for op in ops:
        stacked = np.vstack(out)
        lo, hi = stacked.min(axis=0), stacked.max(axis=0)
        if np.any(hi - lo <= 0.0):
            continue
        floor = _notch_floor(stacked, op, lo, hi) if isinstance(op, DeepenOp) else 0.0
        for contour in out:
            if isinstance(op, StretchOp):
                _pull(contour, op, lo, hi)
            elif isinstance(op, ThickenOp):
                _widen(contour, op, lo, hi)
            else:
                _cut(contour, op, lo, hi, floor)
    return out


def _notch_floor(
    stacked: Contour, op: DeepenOp, lo: NDArray[np.float64], hi: NDArray[np.float64]
) -> float:
    """How far the notch reaches in: the rightmost outline point inside the band."""
    extent = hi[1] - lo[1]
    inside = (stacked[:, 1] >= lo[1] + op.band[0] * extent) & (
        stacked[:, 1] <= lo[1] + op.band[1] * extent
    )
    return float(stacked[inside, 0].max()) if inside.any() else float(lo[0])


def _cut(
    contour: Contour,
    op: DeepenOp,
    lo: NDArray[np.float64],
    hi: NDArray[np.float64],
    floor: float,
) -> None:
    """Move the notch floor toward the spine, windowed in x so the arm tips stay."""
    weight = _band_weight(contour[:, 1], op, lo, hi, axis=1) * _gate(contour[:, 0], op, lo, hi, 0)
    if op.feather > 0.0:
        beyond_floor = _smoothstep(np.clip((contour[:, 0] - floor) / op.feather, 0.0, 1.0))
    else:
        beyond_floor = (contour[:, 0] > floor).astype(np.float64)
    contour[:, 0] -= op.dx * weight * (1.0 - beyond_floor)


def _pull(
    contour: Contour, op: StretchOp, lo: NDArray[np.float64], hi: NDArray[np.float64]
) -> None:
    axis = 0 if op.dx != 0.0 else 1
    delta = op.dx if axis == 0 else op.dy
    extent = hi[axis] - lo[axis]

    v = contour[:, axis]
    if delta > 0:  # anchor at the low side, pull the high side out
        origin = lo[axis] + op.beyond * extent
        share = np.clip((v - origin) / (hi[axis] - origin), 0.0, 1.0)
    else:  # anchor at the high side, pull the low side out
        origin = hi[axis] - op.beyond * extent
        share = np.clip((origin - v) / (origin - lo[axis]), 0.0, 1.0)

    contour[:, axis] = v + delta * share * _band_weight(contour[:, 1 - axis], op, lo, hi, 1 - axis)


def _widen(
    contour: Contour, op: ThickenOp, lo: NDArray[np.float64], hi: NDArray[np.float64]
) -> None:
    """Move each side of the band away from its centre, fading in past `beyond`."""
    extent = hi[1] - lo[1]
    centre = lo[1] + 0.5 * (op.band[0] + op.band[1]) * extent
    gate = _gate(contour[:, 0], op, lo, hi, axis=0)
    weight = _band_weight(contour[:, 1], op, lo, hi, axis=1)
    contour[:, 1] += op.dy * np.sign(contour[:, 1] - centre) * weight * gate


def _gate(
    v: NDArray[np.float64],
    op: _BandOp,
    lo: NDArray[np.float64],
    hi: NDArray[np.float64],
    axis: int,
) -> NDArray[np.float64]:
    """0 before `beyond`, 1 past it, with a `feather`-wide ramp so the root does not kink."""
    threshold = lo[axis] + op.beyond * (hi[axis] - lo[axis])
    if op.feather == 0.0:
        return np.asarray((v >= threshold).astype(np.float64))
    return _smoothstep(np.clip((v - threshold) / op.feather, 0.0, 1.0))


def _band_weight(
    v: NDArray[np.float64],
    op: _BandOp,
    lo: NDArray[np.float64],
    hi: NDArray[np.float64],
    axis: int,
) -> NDArray[np.float64]:
    """1 inside the band, a smoothstep fade over `feather` mm outside it."""
    extent = hi[axis] - lo[axis]
    band_lo = lo[axis] + op.band[0] * extent
    band_hi = lo[axis] + op.band[1] * extent
    outside = np.maximum(np.maximum(band_lo - v, v - band_hi), 0.0)
    if op.feather == 0.0:
        return np.asarray((outside == 0.0).astype(np.float64))
    return _smoothstep(np.clip(1.0 - outside / op.feather, 0.0, 1.0))


def _smoothstep(t: NDArray[np.float64]) -> NDArray[np.float64]:
    return np.asarray(t * t * (3.0 - 2.0 * t))
