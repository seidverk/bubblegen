from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bubblegen.errors import EmptyGlyphError, FontError, GlyphNotFoundError
from bubblegen.fonts import Font

MISSING_CHAR = "\U0010fffe"  # noncharacter, no font maps it


def test_load_reports_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FontError):
        Font.load(tmp_path / "nope.ttf")


def test_units_per_em(font: Font) -> None:
    assert font.units_per_em == 2048


def test_reference_height_is_cap_height(font: Font) -> None:
    assert font.reference_height == pytest.approx(1493.0)


def test_cap_letter_is_scaled_to_requested_size(font: Font) -> None:
    contours = font.contours_mm("H", size_mm=20.0, bezier_steps=8)
    pts = np.vstack(contours)
    height = pts[:, 1].max() - pts[:, 1].min()
    assert height == pytest.approx(20.0, rel=0.02)


def test_counter_produces_two_contours(font: Font) -> None:
    assert len(font.contours_mm("O", size_mm=20.0, bezier_steps=8)) == 2


def test_bezier_steps_control_point_density(font: Font) -> None:
    coarse = np.vstack(font.contours_mm("O", size_mm=20.0, bezier_steps=4))
    fine = np.vstack(font.contours_mm("O", size_mm=20.0, bezier_steps=32))
    assert len(fine) > len(coarse)


def test_missing_glyph(font: Font) -> None:
    with pytest.raises(GlyphNotFoundError):
        font.contours_mm(MISSING_CHAR, size_mm=20.0, bezier_steps=8)


def test_whitespace_glyph_is_empty(font: Font) -> None:
    with pytest.raises(EmptyGlyphError):
        font.contours_mm(" ", size_mm=20.0, bezier_steps=8)
