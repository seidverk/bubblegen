"""All tunables in one immutable, validated object."""

from __future__ import annotations

from dataclasses import dataclass

ROUND_FACTOR = 0.45
"""Silhouette rounding radius as a fraction of puff, when not given explicitly."""

BASE_ROUND_FACTOR = 0.5
"""Underside fillet radius as a fraction of puff, when not given explicitly.

Half the thickness rounds the underside as much as the tube allows, which is what makes
the cross-section read as a doughnut rather than a pillow. The contact patch stays wide
enough to glue and to print: it comes out around two thirds of the letter's width.
"""

PUFF_SLACK = 2.0
"""How far past the membrane's own peak `--puff` may push, as a multiple of it.

The membrane on its own reaches half the stroke width, which reads as flattened. Twice
that is a full round tube: as tall as the stroke is wide, which is what a doughnut is.
Beyond it the letter would be taller than wide, which is a sausage.
"""

MIN_FULLNESS = 2.0
MAX_FULLNESS = 8.0
"""Below 2 the cross-section would dip below a semicircle and read as deflated."""


@dataclass(frozen=True, slots=True)
class BubbleParams:
    """Geometry and sampling parameters for one batch of letters.

    Distances are millimetres; the mesh is built at 1 unit = 1 mm so exported
    STLs drop straight into a slicer.
    """

    size_mm: float = 60.0
    """Cap height. Every letter shares this scale, so an alphabet stays consistent."""

    puff_mm: float = 7.0
    """Thickness at the centre of a stroke.

    An upper bound: each stroke is capped at its own width, past which the letter
    would stand taller than it is wide. See PUFF_SLACK.
    """

    round_mm: float | None = None
    """Silhouette rounding radius. Defaults to ROUND_FACTOR * puff."""

    fullness: float = 4.0
    """How inflated the cross-section looks. 2 is a plain semicircle; higher steepens
    the flanks and broadens the top, which is what reads as a balloon."""

    base_round_mm: float | None = None
    """Fillet radius under the letter. Defaults to BASE_ROUND_FACTOR * puff.

    The bottom stays flat and printable, but the outline curves down into it instead of
    meeting the plate at a right angle.
    """

    resolution: float = 5.0
    """Raster pixels per mm. Drives both quality and cost quadratically."""

    z_steps: int = 64
    """Vertical samples for marching cubes."""

    smooth_iterations: int = 40
    """Taubin smoothing passes. 0 disables smoothing.

    Marching cubes leaves fine corrugation on a steep flank, which reads as ribbing
    along the walls; this is what irons it out. Taubin preserves volume, so more passes
    cost shape rather than size: 40 passes take about half a percent off.
    """

    target_faces: int = 40_000
    """Triangle budget after decimation. 0 keeps the raw marching-cubes mesh."""

    bezier_steps: int = 24
    """Line segments per bezier when flattening the outline."""

    def __post_init__(self) -> None:
        self._require_positive("size_mm", self.size_mm)
        self._require_positive("puff_mm", self.puff_mm)
        self._require_positive("resolution", self.resolution)
        self._require_positive("bezier_steps", self.bezier_steps)
        if not MIN_FULLNESS <= self.fullness <= MAX_FULLNESS:
            raise ValueError(
                f"fullness must be within {MIN_FULLNESS}..{MAX_FULLNESS}, got {self.fullness}"
            )
        if self.round_mm is not None:
            self._require_non_negative("round_mm", self.round_mm)
        if self.base_round_mm is not None:
            self._require_non_negative("base_round_mm", self.base_round_mm)
        self._require_non_negative("smooth_iterations", self.smooth_iterations)
        self._require_non_negative("target_faces", self.target_faces)
        if self.z_steps < 2:
            raise ValueError(f"z_steps must be at least 2, got {self.z_steps}")

    @staticmethod
    def _require_positive(name: str, value: float) -> None:
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")

    @staticmethod
    def _require_non_negative(name: str, value: float) -> None:
        if value < 0:
            raise ValueError(f"{name} must not be negative, got {value}")

    @property
    def round_radius(self) -> float:
        return ROUND_FACTOR * self.puff_mm if self.round_mm is None else self.round_mm

    @property
    def base_radius(self) -> float:
        if self.base_round_mm is not None:
            return self.base_round_mm
        return BASE_ROUND_FACTOR * self.puff_mm

    @property
    def margin(self) -> float:
        """Blank border around the glyph so inflation and rounding never clip."""
        return self.puff_mm * 1.5 + self.round_radius * 2.5 + 1.0
