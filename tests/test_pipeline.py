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


def test_bottom_is_a_flat_plate(font: Font, params: BubbleParams) -> None:
    letter = build_letter(font, "I", params)
    bottom = letter.mesh.vertices[letter.mesh.vertices[:, 2] < 0.01]

    assert len(bottom) > 0
    assert bottom[:, 2].max() == pytest.approx(0.0, abs=0.01)
    assert 0.0 < letter.extents[2] <= params.puff_mm * (1 + params.dome) + 0.05


def test_thickness_reaches_the_requested_puff_on_fat_strokes(font: Font) -> None:
    p = BubbleParams(
        size_mm=60.0, puff_mm=3.0, dome=0.2, resolution=4.0, z_steps=32, target_faces=0
    )

    letter = build_letter(font, "I", p)

    assert letter.extents[2] == pytest.approx(p.puff_mm * (1 + p.dome), abs=0.3)


def test_capped_thickness_is_reported(
    font: Font, params: BubbleParams, caplog: pytest.LogCaptureFixture
) -> None:
    p = dataclasses.replace(params, puff_mm=6.0)

    with caplog.at_level("WARNING"):
        build_letter(font, "I", p)

    assert "is capped at" in caplog.text


def test_decimation_meets_the_face_budget(font: Font) -> None:
    """Quadric decimation emits a few zero-area faces. Unless they are dropped the
    candidate reads as non-manifold and the dense mesh gets exported instead."""
    budget = 40_000
    params = BubbleParams(
        size_mm=45.0,
        puff_mm=6.0,
        dome=0.4,
        resolution=5.0,
        smooth_iterations=0,
        target_faces=budget,
    )

    letter = build_letter(font, "A", params)

    assert letter.face_count <= budget
    assert letter.is_watertight


def test_decimation_never_flattens_the_dome(font: Font) -> None:
    """Quadric decimation collapses whole strips of a straight stroke into plates,
    which prints as a low-poly letter. Fidelity has to win over the face budget."""
    p = BubbleParams(
        size_mm=40.0, puff_mm=4.0, resolution=4.0, smooth_iterations=0, target_faces=3_000
    )

    mesh = build_letter(font, "H", p).mesh
    dome = mesh.area_faces[mesh.face_normals[:, 2] > 0.7]

    assert dome.max() < 1.0  # mm2; dense faces are ~0.04, plates are tens


def test_oversized_rounding_is_backed_off_and_reported(
    font: Font, params: BubbleParams, caplog: pytest.LogCaptureFixture
) -> None:
    """A radius wider than half a stroke would erase it, so it must be reduced."""
    p = dataclasses.replace(params, round_mm=4.0)

    with caplog.at_level("WARNING"):
        letter = build_letter(font, "I", p)

    assert letter.is_watertight
    assert "would deform the glyph" in caplog.text


def test_rounding_keeps_the_counter_of_a_letter(font: Font, params: BubbleParams) -> None:
    """An 'O' with its counter filled would print as a blob."""
    p = dataclasses.replace(params, size_mm=40.0, puff_mm=6.0)

    letter = build_letter(font, "O", p)

    assert letter.mesh.euler_number == 0  # a torus, not a disc


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
