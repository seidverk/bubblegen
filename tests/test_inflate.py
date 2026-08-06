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
