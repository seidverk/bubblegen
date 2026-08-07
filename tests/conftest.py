"""Shared fixtures. DejaVu Sans ships with matplotlib, so tests need no font assets."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest
from matplotlib import font_manager
from numpy.typing import NDArray

from bubblegen.config import BubbleParams
from bubblegen.fonts import Font

SquareFactory = Callable[..., NDArray[np.float64]]
RectFactory = Callable[..., NDArray[np.float64]]


@pytest.fixture(scope="session")
def font_path() -> Path:
    return Path(font_manager.findfont("DejaVu Sans"))


@pytest.fixture(scope="session")
def font(font_path: Path) -> Font:
    return Font.load(font_path)


@pytest.fixture
def params() -> BubbleParams:
    """Small and coarse: keeps meshing tests in the millisecond range.

    evenness is pinned to 0 so tests describe the raw inflation; the ones about
    evenness itself set it explicitly."""
    return BubbleParams(
        size_mm=15.0,
        puff_mm=2.0,
        evenness=0.0,
        inflate=2.0,
        resolution=4.0,
        z_steps=20,
        smooth_iterations=0,
        target_faces=0,
    )


@pytest.fixture
def square() -> SquareFactory:
    """Axis-aligned square contour in mm, counter-clockwise."""

    def make(size: float = 10.0, offset: float = 0.0) -> NDArray[np.float64]:
        s, o = size, offset
        return np.array([(o, o), (o + s, o), (o + s, o + s), (o, o + s)], dtype=np.float64)

    return make


@pytest.fixture
def rect() -> RectFactory:
    """Axis-aligned rectangle contour in mm: a stroke of a given width."""

    def make(width: float, height: float, x: float = 0.0, y: float = 0.0) -> NDArray[np.float64]:
        return np.array(
            [(x, y), (x + width, y), (x + width, y + height), (x, y + height)],
            dtype=np.float64,
        )

    return make


@pytest.fixture
def uneven_ring() -> list[NDArray[np.float64]]:
    """An O whose ring is narrower at top and bottom, as in most typefaces."""
    angle = np.linspace(0.0, 2.0 * np.pi, 240, endpoint=False)
    outer = np.column_stack([40 + 30 * np.cos(angle), 40 + 30 * np.sin(angle)])
    inner = np.column_stack([40 + 14 * np.cos(angle), 40 + 18 * np.sin(angle)])
    return [outer, inner]


@pytest.fixture
def dumbbell() -> NDArray[np.float64]:
    """Two fat pads joined by a short 8 mm neck: a waist the crest line skips."""
    return np.array(
        [
            (0, 0),
            (18, 0),
            (18, 6),
            (22, 6),
            (22, 0),
            (40, 0),
            (40, 20),
            (22, 20),
            (22, 14),
            (18, 14),
            (18, 20),
            (0, 20),
        ],
        dtype=np.float64,
    )


@pytest.fixture
def notched() -> NDArray[np.float64]:
    """A fat C: 16 mm walls around an 8 mm aperture, like the apertures of S and G."""
    return np.array(
        [(0, 0), (40, 0), (40, 16), (15, 16), (15, 24), (40, 24), (40, 40), (0, 40)],
        dtype=np.float64,
    )


@pytest.fixture
def fat_elbow() -> NDArray[np.float64]:
    """An L with 30 mm arms: wide enough for its concave corner to matter."""
    return np.array([(0, 0), (70, 0), (70, 30), (30, 30), (30, 70), (0, 70)], dtype=np.float64)


@pytest.fixture
def elbow() -> NDArray[np.float64]:
    """An L: two 10 mm strokes meeting at a junction, as one contour."""
    return np.array([(0, 0), (40, 0), (40, 10), (10, 10), (10, 40), (0, 40)], dtype=np.float64)
