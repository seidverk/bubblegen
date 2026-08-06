from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from bubblegen.config import BubbleParams
from bubblegen.fonts import Font
from bubblegen.pipeline import build_alphabet, build_letter, export_stl, slug


def test_letter_is_watertight_and_grounded(font: Font, params: BubbleParams) -> None:
    letter = build_letter(font, "I", params)

    assert letter.char == "I"
    assert letter.mesh.is_watertight
    assert letter.mesh.bounds[0][2] == pytest.approx(0.0, abs=1e-6)


def test_letter_height_matches_the_requested_size(font: Font, params: BubbleParams) -> None:
    letter = build_letter(font, "I", params)
    assert letter.extents[1] == pytest.approx(params.size_mm, abs=2.0)


def test_letter_reports_mesh_stats(font: Font, params: BubbleParams) -> None:
    letter = build_letter(font, "I", params)
    assert letter.face_count == len(letter.mesh.faces)
    assert letter.is_watertight is True


def test_hole_is_drilled_when_requested(font: Font, params: BubbleParams) -> None:
    p = dataclasses.replace(params, size_mm=40.0, hole_mm=2.0, hole_wall_mm=0.5)

    solid = build_letter(font, "I", dataclasses.replace(p, hole_mm=0.0))
    drilled = build_letter(font, "I", p)

    assert drilled.mesh.volume < solid.mesh.volume


def test_decimation_meets_the_face_budget(font: Font) -> None:
    """Quadric decimation emits a few zero-area faces. Unless they are dropped the
    candidate reads as non-manifold and the dense mesh gets exported instead."""
    budget = 40_000
    params = BubbleParams(
        size_mm=45.0,
        puff_mm=6.0,
        dome=0.4,
        flat_back=True,
        resolution=5.0,
        smooth_iterations=0,
        target_faces=budget,
    )

    letter = build_letter(font, "A", params)

    assert letter.face_count <= budget
    assert letter.is_watertight


def test_alphabet_skips_whitespace_and_unmapped_glyphs(font: Font, params: BubbleParams) -> None:
    letters = list(build_alphabet(font, "I \U0010fffe", params))
    assert [letter.char for letter in letters] == ["I"]


def test_export_writes_an_stl(font: Font, params: BubbleParams, tmp_path: Path) -> None:
    letter = build_letter(font, "I", params)

    path = export_stl(letter, tmp_path)

    assert path == tmp_path / "bubble_I.stl"
    assert path.stat().st_size > 0


@pytest.mark.parametrize(
    ("char", "expected"),
    [("A", "A"), ("7", "7"), ("Ж", "U0416"), ("-", "U002D"), ("Þ", "U00DE")],
)
def test_slug(char: str, expected: str) -> None:
    assert slug(char) == expected
