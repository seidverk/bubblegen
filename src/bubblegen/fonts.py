"""Glyph outlines from a TTF/OTF, flattened to polylines and scaled to mm."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Any

import numpy as np
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont, TTLibError
from numpy.typing import NDArray

from bubblegen.errors import EmptyGlyphError, FontError, GlyphNotFoundError

Contour = NDArray[np.float64]

CAP_REFERENCE_CHARS = ("H", "Н", "I")
"""Flat-topped capitals measured to recover cap height when OS/2 omits it."""

CAP_HEIGHT_FALLBACK = 0.72
"""Share of the ascender treated as cap height when nothing better is available."""

MIN_CONTOUR_POINTS = 3


class FlattenPen(BasePen):  # type: ignore[misc]  # fontTools ships no annotations
    """Collects glyph contours as flat polylines, sampling beziers into lines."""

    def __init__(self, glyph_set: Any, steps: int = 24) -> None:
        super().__init__(glyph_set)
        self.steps = steps
        self.contours: list[Contour] = []
        self._current: list[tuple[float, float]] = []

    def _moveTo(self, pt: tuple[float, float]) -> None:  # noqa: N802 - fontTools API
        self._flush()
        self._current = [pt]

    def _lineTo(self, pt: tuple[float, float]) -> None:  # noqa: N802 - fontTools API
        self._current.append(pt)

    def _curveToOne(  # noqa: N802 - fontTools API
        self,
        p1: tuple[float, float],
        p2: tuple[float, float],
        p3: tuple[float, float],
    ) -> None:
        # cubic bezier sampling; BasePen converts quadratics to cubics for us
        p0 = self._current[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1.0 - t
            x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
            y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
            self._current.append((x, y))

    def _closePath(self) -> None:  # noqa: N802 - fontTools API
        self._flush()

    def _endPath(self) -> None:  # noqa: N802 - fontTools API
        self._flush()

    def _flush(self) -> None:
        if len(self._current) >= MIN_CONTOUR_POINTS:
            self.contours.append(np.asarray(self._current, dtype=np.float64))
        self._current = []

    def result(self) -> list[Contour]:
        self._flush()
        return self.contours


class Font:
    """A loaded font, queried per character."""

    def __init__(self, path: Path, tt: TTFont) -> None:
        self.path = path
        self._tt = tt
        self._glyph_set = tt.getGlyphSet()
        self._cmap = tt.getBestCmap()

    @classmethod
    def load(cls, path: Path | str) -> Font:
        path = Path(path)
        try:
            tt = TTFont(path, fontNumber=0)
        except (OSError, TTLibError) as exc:
            raise FontError(f"cannot read font {path}: {exc}") from exc
        return cls(path, tt)

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def units_per_em(self) -> int:
        return int(self._tt["head"].unitsPerEm)

    @cached_property
    def reference_height(self) -> float:
        """Font units a capital letter occupies, so all letters share one scale.

        OS/2 version 1 has no sCapHeight field, so measuring a flat-topped capital
        is used before falling back to a share of the ascender.
        """
        os2: Any = self._tt.get("OS/2")
        declared = float(getattr(os2, "sCapHeight", 0.0) or 0.0)
        if declared > 0:
            return declared

        measured = self._measured_cap_height()
        if measured is not None:
            return measured
        return float(self._tt["hhea"].ascender) * CAP_HEIGHT_FALLBACK

    def _measured_cap_height(self) -> float | None:
        for char in CAP_REFERENCE_CHARS:
            name = self._cmap.get(ord(char))
            if name is None:
                continue
            pen = BoundsPen(self._glyph_set)
            self._glyph_set[name].draw(pen)
            if pen.bounds is not None and pen.bounds[3] > 0:
                return float(pen.bounds[3])
        return None

    def scale_for(self, size_mm: float) -> float:
        """Font units to mm, such that a capital letter is `size_mm` tall."""
        return size_mm / self.reference_height

    def contours_mm(self, char: str, size_mm: float, bezier_steps: int) -> list[Contour]:
        """Flattened contours of `char`, in mm."""
        code = ord(char)
        name = self._cmap.get(code)
        if name is None:
            raise GlyphNotFoundError(f"no glyph for {char!r} (U+{code:04X}) in {self.name}")

        pen = FlattenPen(self._glyph_set, steps=bezier_steps)
        self._glyph_set[name].draw(pen)
        contours = pen.result()
        if not contours:
            raise EmptyGlyphError(f"{char!r} has an empty outline (whitespace?)")

        scale = self.scale_for(size_mm)
        return [contour * scale for contour in contours]
