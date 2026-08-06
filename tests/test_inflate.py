from __future__ import annotations

import dataclasses

import numpy as np
import pytest
from numpy.typing import NDArray

from bubblegen.config import BubbleParams, Profile
from bubblegen.inflate import height_field


@pytest.fixture
def sd() -> NDArray[np.float64]:
    """One-dimensional signed distance ramp: outside, edge roll, deep interior."""
    return np.linspace(-2.0, 6.0, 201)


def test_automatic_roll_spans_the_whole_stroke(sd: NDArray[np.float64]) -> None:
    """Without an explicit roll the peak must sit at the deepest point only: a fixed
    roll shorter than the stroke leaves a flat plateau, which reads as an extrusion."""
    p = BubbleParams(puff_mm=2.0, roll_mm=None, dome=0.0)

    h = height_field(sd, p)

    assert h.max() == pytest.approx(p.puff_mm)
    plateau = (h >= p.puff_mm - 1e-9).sum()
    assert plateau == 1
    assert h[sd >= sd.max() / 2].min() < p.puff_mm


def test_thickness_is_capped_by_the_stroke_width() -> None:
    """A peak taller than the stroke half-width is a tube, not a bubble."""
    thin = np.linspace(-2.0, 2.0, 101)
    p = BubbleParams(puff_mm=10.0, dome=0.0)

    assert height_field(thin, p).max() == pytest.approx(2.0, rel=0.02)


def test_thick_strokes_keep_the_requested_puff() -> None:
    fat = np.linspace(-2.0, 20.0, 201)
    p = BubbleParams(puff_mm=5.0, dome=0.0)

    assert height_field(fat, p).max() == pytest.approx(5.0)


def test_dome_counts_towards_the_cap() -> None:
    thin = np.linspace(-2.0, 3.0, 101)
    p = BubbleParams(puff_mm=10.0, dome=0.5)

    assert height_field(thin, p).max() == pytest.approx(3.0, rel=0.02)


def test_explicit_roll_saturates_early(sd: NDArray[np.float64]) -> None:
    p = BubbleParams(puff_mm=2.0, roll_mm=1.0, dome=0.0)

    h = height_field(sd, p)

    assert (h >= p.puff_mm - 1e-9).sum() > 1


def test_full_thickness_reached_beyond_the_roll(sd: NDArray[np.float64]) -> None:
    p = BubbleParams(puff_mm=2.0, roll_mm=1.0, dome=0.0)
    assert height_field(sd, p).max() == pytest.approx(p.puff_mm)


def test_dome_adds_a_central_bulge(sd: NDArray[np.float64]) -> None:
    p = BubbleParams(puff_mm=2.0, roll_mm=1.0, dome=0.5)
    assert height_field(sd, p).max() == pytest.approx(p.puff_mm * 1.5)


def test_field_sign_follows_the_silhouette(sd: NDArray[np.float64]) -> None:
    p = BubbleParams(puff_mm=2.0, roll_mm=1.0)
    h = height_field(sd, p)
    assert np.all(h[sd < 0] < 0)
    assert np.all(h[sd > 0] >= 0)


def test_height_is_monotonic_in_distance(sd: NDArray[np.float64]) -> None:
    p = BubbleParams(puff_mm=2.0, roll_mm=1.0, dome=0.2)
    assert np.all(np.diff(height_field(sd, p)) >= -1e-9)


def test_profiles_are_ordered_by_shoulder_fullness(sd: NDArray[np.float64]) -> None:
    base = BubbleParams(puff_mm=2.0, roll_mm=1.0, dome=0.0)
    heights = {
        profile: height_field(sd, dataclasses.replace(base, profile=profile)) for profile in Profile
    }
    inside = sd > 0
    assert np.all(heights[Profile.SUPER][inside] >= heights[Profile.SPHERE][inside] - 1e-9)
    assert np.all(heights[Profile.SPHERE][inside] >= heights[Profile.SMOOTH][inside] - 1e-9)
