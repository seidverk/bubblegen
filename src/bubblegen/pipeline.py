"""End-to-end: character in, printable mesh out."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import trimesh

from bubblegen.errors import BubbleGenError, MeshError
from bubblegen.inflate import height_field
from bubblegen.mesh import build_mesh
from bubblegen.raster import Raster, rasterize, signed_distance, soften

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from bubblegen.config import BubbleParams
    from bubblegen.fonts import Font

logger = logging.getLogger(__name__)

_PLAIN_NAME = re.compile(r"[A-Za-z0-9]")

MIN_MASK_RETENTION = 0.5
"""Below this share of surviving glyph area the rounding radius is clearly too large."""


@dataclass(frozen=True, slots=True)
class LetterMesh:
    """One finished letter, resting on z = 0."""

    char: str
    mesh: trimesh.Trimesh

    @property
    def extents(self) -> tuple[float, float, float]:
        x, y, z = self.mesh.bounds[1] - self.mesh.bounds[0]
        return (float(x), float(y), float(z))

    @property
    def face_count(self) -> int:
        return len(self.mesh.faces)

    @property
    def is_watertight(self) -> bool:
        return bool(self.mesh.is_watertight)


def slug(char: str) -> str:
    """Filename-safe name for a character."""
    if _PLAIN_NAME.match(char):
        return char
    return f"U{ord(char):04X}"


def _round_silhouette(raster: Raster, char: str, params: BubbleParams) -> Raster:
    """Round the outline, and complain when the radius eats the strokes themselves.

    Rounding erodes by `round_radius`, so a radius wider than half a stroke deletes
    that stroke. Light fonts at a large puff hit this easily.
    """
    mask = soften(raster.mask, params.resolution, params.round_radius)
    if not mask.any():
        raise MeshError(
            f"a {params.round_radius:.1f} mm rounding radius erased {char!r}; "
            f"lower --round or --puff, or raise --size"
        )

    kept = mask.sum() / raster.mask.sum()
    if kept < MIN_MASK_RETENTION:
        logger.warning(
            "%r: rounding removed %.0f%% of the glyph, lower --round or --puff",
            char,
            100 * (1 - kept),
        )
    return raster.with_mask(mask)


def build_letter(font: Font, char: str, params: BubbleParams) -> LetterMesh:
    """Run the whole pipeline for one character."""
    contours = font.contours_mm(char, params.size_mm, params.bezier_steps)

    raster = _round_silhouette(rasterize(contours, params), char, params)
    sd = signed_distance(raster.mask, params.resolution)
    mesh = build_mesh(height_field(sd, params), raster, params)

    # drop to z = 0 so it lands on the build plate
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
    return LetterMesh(char=char, mesh=mesh)


def build_alphabet(font: Font, chars: Iterable[str], params: BubbleParams) -> Iterator[LetterMesh]:
    """Build every character, skipping whitespace and glyphs the font cannot supply."""
    for char in chars:
        if char.isspace():
            continue
        try:
            yield build_letter(font, char, params)
        except BubbleGenError as exc:
            logger.warning("skip %r: %s", char, exc)


def export_stl(letter: LetterMesh, out_dir: Path) -> Path:
    """Write the letter as `bubble_<name>.stl` and return the path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"bubble_{slug(letter.char)}.stl"
    letter.mesh.export(path)
    return path
