from __future__ import annotations

import pytest

from bubblegen.config import BubbleParams


def test_defaults_are_the_reference_balloon() -> None:
    p = BubbleParams()
    assert p.puff_mm is None
    assert p.fullness == 2.0
    assert p.size_mm == 100.0
    assert p.evenness == 0.0
    assert p.inflate == 1.5


def test_radii_derive_from_size_without_puff() -> None:
    p = BubbleParams(size_mm=80.0)
    assert p.round_radius == pytest.approx(14.0)
    assert p.base_radius == pytest.approx(9.6)


def test_margin_covers_inflation_without_puff() -> None:
    p = BubbleParams(size_mm=80.0)
    assert p.margin == pytest.approx(80.0 * 0.75 + 14.0 * 2.5 + 1.0)


def test_round_radius_defaults_to_fraction_of_puff() -> None:
    assert BubbleParams(puff_mm=7.0).round_radius == pytest.approx(3.15)


def test_base_radius_defaults_to_a_fraction_of_puff() -> None:
    assert BubbleParams(puff_mm=8.0).base_radius == pytest.approx(4.0)


def test_explicit_base_round_wins() -> None:
    assert BubbleParams(puff_mm=8.0, base_round_mm=0.0).base_radius == 0.0


def test_margin_covers_puff_and_rounding() -> None:
    p = BubbleParams(puff_mm=2.0, round_mm=1.0)
    assert p.margin == pytest.approx(2.0 * 1.5 + 1.0 * 2.5 + 1.0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"size_mm": 0.0},
        {"puff_mm": -1.0},
        {"evenness": -0.1},
        {"evenness": 1.1},
        {"inflate": 0.0},
        {"inflate": 2.1},
        {"round_mm": -0.5},
        {"base_round_mm": -1.0},
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
