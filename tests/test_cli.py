from __future__ import annotations

from pathlib import Path

import pytest
import trimesh

from bubblegen.cli import build_parser, main, params_from_args


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
            "--base-round",
            "0.5",
        ]
    )
    params = params_from_args(args)

    assert params.puff_mm == 3.0
    assert params.base_radius == 0.5


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


def test_tweaks_file_is_applied(font_path: Path, tmp_path: Path) -> None:
    tweaks = tmp_path / "tweaks.toml"
    tweaks.write_text(
        "[I]\n[[I.stretch]]\nband = [0.0, 1.0]\nbeyond = 0.5\ndx = 3.0\nfeather = 1.0\n",
        encoding="utf-8",
    )
    fast = ["--size", "12", "--puff", "1.5", "--res", "3", "--zsteps", "16", "--smooth", "0"]

    plain_dir, tweaked_dir = tmp_path / "plain", tmp_path / "tweaked"
    base = ["--font", str(font_path), "--chars", "I", *fast]
    assert main([*base, "--out", str(plain_dir)]) == 0
    assert main([*base, "--out", str(tweaked_dir), "--tweaks", str(tweaks)]) == 0

    plain = trimesh.load(plain_dir / "bubble_I.stl")
    tweaked = trimesh.load(tweaked_dir / "bubble_I.stl")
    widths = [m.bounds[1][0] - m.bounds[0][0] for m in (tweaked, plain)]
    assert widths[0] - widths[1] == pytest.approx(3.0, abs=1.0)


def test_a_bad_tweaks_file_is_reported_not_raised(font_path: Path, tmp_path: Path) -> None:
    tweaks = tmp_path / "tweaks.toml"
    tweaks.write_text("[I]\n[[I.stretch]]\nband = [0, 1]\nbeyond = 0.5\ndz = 3\n", encoding="utf-8")
    code = main(
        ["--font", str(font_path), "--chars", "I", "--out", str(tmp_path), "--tweaks", str(tweaks)]
    )
    assert code == 1


def test_missing_font_is_reported_not_raised(tmp_path: Path) -> None:
    code = main(["--font", str(tmp_path / "nope.ttf"), "--chars", "A", "--out", str(tmp_path)])
    assert code == 1


def test_invalid_parameter_is_reported_not_raised(font_path: Path, tmp_path: Path) -> None:
    code = main(["--font", str(font_path), "--chars", "A", "--out", str(tmp_path), "--puff", "-1"])
    assert code == 1
