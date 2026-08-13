from __future__ import annotations

from pathlib import Path

import pytest
import trimesh

from bubblegen.stand_cli import build_parser, main, params_from_args

FAST = ["--size", "30", "--height", "12", "--deck", "4", "--cell", "6", "--leg", "5"]


def test_help_exits_cleanly(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(["--help"])
    assert exc.value.code == 0
    assert "stand" in capsys.readouterr().out.lower()


def test_defaults_need_no_arguments() -> None:
    params = params_from_args(build_parser().parse_args([]))

    assert params.size_mm == 80.0
    assert params.height_mm == 18.0


def test_flags_map_onto_params() -> None:
    args = build_parser().parse_args(["--size", "110", "--cell", "9", "--crest", "0.4"])
    params = params_from_args(args)

    assert params.size_mm == 110.0
    assert params.cell_mm == 9.0
    assert params.crest_mm == 0.4


def test_run_writes_an_stl(tmp_path: Path) -> None:
    out = tmp_path / "stand.stl"

    code = main([*FAST, "--out", str(out)])

    assert code == 0
    mesh = trimesh.load(out)
    assert isinstance(mesh, trimesh.Trimesh)
    assert mesh.is_watertight


def test_run_creates_missing_directories(tmp_path: Path) -> None:
    out = tmp_path / "nested" / "stand.stl"

    assert main([*FAST, "--out", str(out)]) == 0
    assert out.exists()


def test_impossible_geometry_fails_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "stand.stl"

    code = main(["--size", "20", "--rim", "10", "--out", str(out)])

    assert code == 1
    assert "rim_mm" in capsys.readouterr().err
    assert not out.exists()
