from __future__ import annotations

from pathlib import Path

import pytest

from bubblegen.cli import build_parser, main, params_from_args
from bubblegen.config import Profile


def test_font_and_chars_are_required() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([])


def test_help_exits_cleanly(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(["--help"])
    assert exc.value.code == 0
    assert "bubble" in capsys.readouterr().out.lower()


def test_flags_map_onto_params() -> None:
    args = build_parser().parse_args(
        [
            "--font",
            "f.ttf",
            "--chars",
            "AB",
            "--puff",
            "3",
            "--profile",
            "smooth",
            "--base-round",
            "0.5",
        ]
    )
    params = params_from_args(args)

    assert params.puff_mm == 3.0
    assert params.profile is Profile.SMOOTH
    assert params.base_radius == 0.5
    assert params.roll_mm is None


def test_run_writes_an_stl(font_path: Path, tmp_path: Path) -> None:
    code = main(
        [
            "--font",
            str(font_path),
            "--chars",
            "I",
            "--out",
            str(tmp_path),
            "--size",
            "12",
            "--puff",
            "1.5",
            "--res",
            "3",
            "--zsteps",
            "16",
            "--smooth",
            "0",
            "--faces",
            "0",
        ]
    )

    assert code == 0
    assert (tmp_path / "bubble_I.stl").exists()


def test_missing_font_is_reported_not_raised(tmp_path: Path) -> None:
    code = main(["--font", str(tmp_path / "nope.ttf"), "--chars", "A", "--out", str(tmp_path)])
    assert code == 1


def test_invalid_parameter_is_reported_not_raised(font_path: Path, tmp_path: Path) -> None:
    code = main(["--font", str(font_path), "--chars", "A", "--out", str(tmp_path), "--puff", "-1"])
    assert code == 1
