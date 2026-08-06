"""All tunables in one immutable, validated object."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

ROUND_FACTOR = 0.45
"""Silhouette rounding radius as a fraction of puff, when not given explicitly."""


class Profile(StrEnum):
    """Shape of the edge roll — how the surface climbs from 0 to full thickness."""

    SPHERE = "sphere"  # quarter-circle: classic pillow edge
    SMOOTH = "smooth"  # smoothstep: softer, more balloon-like
    SUPER = "super"  # superellipse: fuller, squarer shoulder


@dataclass(frozen=True, slots=True)
class BubbleParams:
    """Geometry and sampling parameters for one batch of letters.

    Distances are millimetres; the mesh is built at 1 unit = 1 mm so exported
    STLs drop straight into a slicer.
    """

    size_mm: float = 60.0
    """Cap height. Every letter shares this scale, so an alphabet stays consistent."""

    puff_mm: float = 7.0
    """Thickness at the centre of a stroke; the dome adds to it."""

    roll_mm: float | None = None
    """Distance over which the edge rounds up to full thickness. Defaults to puff."""

    round_mm: float | None = None
    """Silhouette rounding radius. Defaults to ROUND_FACTOR * puff."""

    dome: float = 0.15
    """Extra centre bulge as a fraction of puff. 0 keeps the top flat."""

    profile: Profile = Profile.SPHERE

    resolution: float = 5.0
    """Raster pixels per mm. Drives both quality and cost quadratically."""

    z_steps: int = 64
    """Vertical samples for marching cubes."""

    smooth_iterations: int = 12
    """Taubin smoothing passes. 0 disables smoothing."""

    target_faces: int = 40_000
    """Triangle budget after decimation. 0 keeps the raw marching-cubes mesh."""

    bezier_steps: int = 24
    """Line segments per bezier when flattening the outline."""

    def __post_init__(self) -> None:
        # StrEnum coercion lets callers pass plain strings from CLIs and config files.
        try:
            object.__setattr__(self, "profile", Profile(self.profile))
        except ValueError as exc:
            known = ", ".join(p.value for p in Profile)
            raise ValueError(f"unknown profile {self.profile!r}, expected one of {known}") from exc

        self._require_positive("size_mm", self.size_mm)
        self._require_positive("puff_mm", self.puff_mm)
        self._require_positive("resolution", self.resolution)
        self._require_positive("bezier_steps", self.bezier_steps)
        if self.roll_mm is not None:
            self._require_positive("roll_mm", self.roll_mm)
        if self.round_mm is not None:
            self._require_non_negative("round_mm", self.round_mm)
        self._require_non_negative("smooth_iterations", self.smooth_iterations)
        self._require_non_negative("target_faces", self.target_faces)
        if not 0.0 <= self.dome <= 1.0:
            raise ValueError(f"dome must be within 0..1, got {self.dome}")
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
    def roll(self) -> float:
        return self.puff_mm if self.roll_mm is None else self.roll_mm

    @property
    def round_radius(self) -> float:
        return ROUND_FACTOR * self.puff_mm if self.round_mm is None else self.round_mm

    @property
    def margin(self) -> float:
        """Blank border around the glyph so inflation and rounding never clip."""
        return self.puff_mm * 1.5 + self.round_radius * 2.5 + 1.0
