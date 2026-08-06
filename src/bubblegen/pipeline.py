"""End-to-end: character in, printable mesh out."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import trimesh

from bubblegen.errors import BubbleGenError
from bubblegen.inflate import height_field
from bubblegen.mesh import build_mesh
from bubblegen.raster import Field, Raster, rasterize, round_silhouette, signed_distance

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from bubblegen.config import BubbleParams
    from bubblegen.fonts import Font

logger = logging.getLogger(__name__)

_PLAIN_NAME = re.compile(r"[A-Za-z0-9]")


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


def _rounded(raster: Raster, char: str, params: BubbleParams) -> Raster:
    """Round the silhouette as far as this particular glyph allows.

    `--round` is an upper bound, not a promise: a radius that fits a fat O fills the
    counter of an R, so it is backed off per letter and the choice is logged.
    """
    mask, used = round_silhouette(raster.mask, params.resolution, params.round_radius)
    if used < params.round_radius:
        logger.warning(
            "%r: --round %.1f mm would deform the glyph, using %.1f mm",
            char,
            params.round_radius,
            used,
        )
    return raster.with_mask(mask)


def _report_puff_cap(sd: Field, char: str, params: BubbleParams) -> None:
    """Say so when the stroke, not `--puff`, is what sets the thickness."""
    deepest = float(sd.max())
    if deepest < params.puff_mm:
        logger.warning(
            "%r: the widest stroke is %.1f mm, so --puff %.1f mm is capped at %.1f mm; "
            "use a heavier font or a larger --size for a fatter bubble",
            char,
            2 * deepest,
            params.puff_mm,
            deepest,
        )


def build_letter(font: Font, char: str, params: BubbleParams) -> LetterMesh:
    """Run the whole pipeline for one character."""
    contours = font.contours_mm(char, params.size_mm, params.bezier_steps)

    raster = _rounded(rasterize(contours, params), char, params)
    sd = signed_distance(raster.mask, params.resolution)
    _report_puff_cap(sd, char, params)
    mesh = build_mesh(height_field(sd, params), sd, raster, params)

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
