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

BALLOON_ROUND_FACTOR = 0.175
BALLOON_BASE_FACTOR = 0.12
BALLOON_MARGIN_FACTOR = 0.75
"""Size-relative stand-ins for the puff-derived radii and margin when `--puff` is not
given: without a cap there is no single thickness to derive them from."""


@dataclass(frozen=True, slots=True)
class BubbleParams:
    """Geometry and sampling parameters for one batch of letters.

    Distances are millimetres; the mesh is built at 1 unit = 1 mm so exported
    STLs drop straight into a slicer.
    """

    size_mm: float = 100.0
    """Cap height. Every letter shares this scale, so an alphabet stays consistent."""

    puff_mm: float | None = None
    """Even-tube thickness cap at the centre of a stroke.

    None inflates every stroke to a full round tube: the height follows the local
    stroke width, as on a real balloon, and no plateau is clipped into the top. A
    number caps the whole letter at one thickness; each stroke still stops at its
    own width, past which the letter would stand taller than it is wide. See
    PUFF_SLACK.
    """

    round_mm: float | None = None
    """Silhouette rounding radius. Defaults to ROUND_FACTOR * puff, or
    BALLOON_ROUND_FACTOR * size without a puff."""

    fullness: float = 2.0
    """Cross-section exponent. 2 is a plain semicircle; higher steepens the flanks
    and flattens the crown into a plateau."""

    evenness: float = 0.0
    """How far the hills are pressed towards one even tube, 0..1.

    Inflation follows the local stroke width, so a swelling-and-tapering face rolls
    hills along the letter. 0 keeps the free balloon, smooth by construction; 1
    presses everything down to the letter's own even-tube thickness. The pressing
    only ever lowers, and its boundary can read as a crease, so prefer a lower
    `inflate` when the letter merely looks too fat."""

    inflate: float = 1.5
    """How hard the membrane is blown up when `--puff` is not given.

    The share of a full round tube: 2 stands as tall as the stroke is wide (a
    doughnut), 1 is the bare membrane at half that. 1.5 is the reference balloon:
    clearly inflated, never bulbous. Scales the whole letter smoothly, so hills
    shrink with it."""

    base_round_mm: float | None = None
    """Fillet radius under the letter. Defaults to BASE_ROUND_FACTOR * puff, or
    BALLOON_BASE_FACTOR * size without a puff.

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
        if self.puff_mm is not None:
            self._require_positive("puff_mm", self.puff_mm)
        self._require_positive("resolution", self.resolution)
        self._require_positive("bezier_steps", self.bezier_steps)
        if not MIN_FULLNESS <= self.fullness <= MAX_FULLNESS:
            raise ValueError(
                f"fullness must be within {MIN_FULLNESS}..{MAX_FULLNESS}, got {self.fullness}"
            )
        if not 0.0 <= self.evenness <= 1.0:
            raise ValueError(f"evenness must be within 0..1, got {self.evenness}")
        if not 0.0 < self.inflate <= PUFF_SLACK:
            raise ValueError(f"inflate must be within 0..{PUFF_SLACK}, got {self.inflate}")
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
        if self.round_mm is not None:
            return self.round_mm
        if self.puff_mm is not None:
            return ROUND_FACTOR * self.puff_mm
        return BALLOON_ROUND_FACTOR * self.size_mm

    @property
    def base_radius(self) -> float:
        if self.base_round_mm is not None:
            return self.base_round_mm
        if self.puff_mm is not None:
            return BASE_ROUND_FACTOR * self.puff_mm
        return BALLOON_BASE_FACTOR * self.size_mm

    @property
    def margin(self) -> float:
        """Blank border around the glyph so inflation and rounding never clip."""
        if self.puff_mm is not None:
            return self.puff_mm * 1.5 + self.round_radius * 2.5 + 1.0
        return BALLOON_MARGIN_FACTOR * self.size_mm + self.round_radius * 2.5 + 1.0
