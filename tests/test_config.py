from __future__ import annotations

import pytest

from bubblegen.config import BubbleParams, Profile


def test_roll_defaults_to_puff() -> None:
    assert BubbleParams(puff_mm=7.0).roll == 7.0


def test_round_radius_defaults_to_fraction_of_puff() -> None:
    assert BubbleParams(puff_mm=7.0).round_radius == pytest.approx(3.15)


def test_explicit_roll_and_round_win() -> None:
    p = BubbleParams(puff_mm=7.0, roll_mm=2.0, round_mm=0.5)
    assert (p.roll, p.round_radius) == (2.0, 0.5)


def test_hole_radius_is_half_the_diameter() -> None:
    assert BubbleParams(hole_mm=4.0).hole_radius == 2.0


def test_margin_covers_puff_and_rounding() -> None:
    p = BubbleParams(puff_mm=2.0, roll_mm=2.0, round_mm=1.0)
    assert p.margin == pytest.approx(2.0 * 1.5 + 1.0 * 2.5 + 1.0)


def test_profile_accepts_string() -> None:
    assert BubbleParams(profile="smooth").profile is Profile.SMOOTH  # type: ignore[arg-type]


def test_unknown_profile_rejected() -> None:
    with pytest.raises(ValueError, match="unknown profile 'banana'"):
        BubbleParams(profile="banana")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"size_mm": 0.0},
        {"puff_mm": -1.0},
        {"roll_mm": 0.0},
        {"round_mm": -0.5},
        {"dome": -0.1},
        {"dome": 1.5},
        {"hole_mm": -1.0},
        {"hole_wall_mm": -1.0},
        {"resolution": 0.0},
        {"z_steps": 1},
        {"smooth_iterations": -1},
        {"target_faces": -1},
        {"bezier_steps": 0},
    ],
)
def test_invalid_values_rejected(kwargs: dict[str, float | int]) -> None:
    with pytest.raises(ValueError):
        BubbleParams(**kwargs)  # type: ignore[arg-type]


def test_params_are_immutable() -> None:
    p = BubbleParams()
    with pytest.raises(AttributeError):
        p.puff_mm = 1.0  # type: ignore[misc]
