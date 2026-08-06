from __future__ import annotations

import pytest

from bubblegen.config import BubbleParams, Profile


def test_roll_defaults_to_the_glyph_half_width() -> None:
    assert BubbleParams(puff_mm=7.0).roll_for(15.8) == 15.8


def test_automatic_roll_has_a_floor() -> None:
    assert BubbleParams().roll_for(0.0) > 0.0


def test_round_radius_defaults_to_fraction_of_puff() -> None:
    assert BubbleParams(puff_mm=7.0).round_radius == pytest.approx(3.15)


def test_explicit_roll_and_round_win() -> None:
    p = BubbleParams(puff_mm=7.0, roll_mm=2.0, round_mm=0.5)
    assert (p.roll_for(15.8), p.round_radius) == (2.0, 0.5)


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
