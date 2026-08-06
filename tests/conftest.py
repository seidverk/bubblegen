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


@pytest.fixture(scope="session")
def font_path() -> Path:
    return Path(font_manager.findfont("DejaVu Sans"))


@pytest.fixture(scope="session")
def font(font_path: Path) -> Font:
    return Font.load(font_path)


@pytest.fixture
def params() -> BubbleParams:
    """Small and coarse: keeps meshing tests in the millisecond range."""
    return BubbleParams(
        size_mm=15.0,
        puff_mm=2.0,
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
