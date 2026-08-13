from __future__ import annotations

import numpy as np
import pytest
import trimesh

from bubblegen.stand import FOOT_HEIGHT_MM, StandParams, build_stand, cell_centres

SLAB_MM = 0.2
"""Thickness of the probe slab. Thin enough that a tapered wall barely changes across it."""


@pytest.fixture
def stand_params() -> StandParams:
    """Small deck: three hexagons a row keeps the booleans in the millisecond range."""
    return StandParams(
        size_mm=30.0,
        height_mm=12.0,
        deck_mm=4.0,
        cell_mm=6.0,
        leg_mm=5.0,
    )


@pytest.fixture
def stand(stand_params: StandParams) -> trimesh.Trimesh:
    return build_stand(stand_params)


def material_area(mesh: trimesh.Trimesh, z: float) -> float:
    """Solid cross-section area at height z, measured as the volume of a thin slab."""
    probe = trimesh.creation.box(extents=[1e3, 1e3, SLAB_MM])
    probe.apply_translation([0.0, 0.0, z])
    slab = mesh.intersection(probe)
    return float(slab.volume) / SLAB_MM


def test_stand_is_watertight(stand: trimesh.Trimesh) -> None:
    assert stand.is_watertight
    assert stand.volume > 0


def test_stand_fills_the_given_footprint(stand: trimesh.Trimesh, stand_params: StandParams) -> None:
    low, high = stand.bounds
    size, height = stand_params.size_mm, stand_params.height_mm

    assert np.allclose(low, [0.0, 0.0, 0.0], atol=1e-6)
    assert np.allclose(high, [size, size, height], atol=1e-6)


def test_deck_is_mostly_open() -> None:
    """At the shipped defaults the deck is more hole than wall, so resin drips through."""
    params = StandParams()
    deck = build_stand(params)

    assert material_area(deck, params.deck_z0 + 0.5) < 0.5 * params.size_mm**2


def test_walls_taper_towards_the_crest(stand: trimesh.Trimesh, stand_params: StandParams) -> None:
    """The holes widen upwards, so the letter meets a crest instead of a face."""
    at_bottom = material_area(stand, stand_params.deck_z0 + 0.5)
    at_crest = material_area(stand, stand_params.height_mm - 0.5)

    assert at_crest < at_bottom


def test_equal_crest_and_wall_leaves_the_walls_straight(stand_params: StandParams) -> None:
    straight = build_stand(
        StandParams(
            size_mm=stand_params.size_mm,
            height_mm=stand_params.height_mm,
            deck_mm=stand_params.deck_mm,
            cell_mm=stand_params.cell_mm,
            leg_mm=stand_params.leg_mm,
            crest_mm=stand_params.wall_mm,
        )
    )
    at_bottom = material_area(straight, stand_params.deck_z0 + 0.5)
    at_crest = material_area(straight, stand_params.height_mm - 0.5)

    assert at_crest == pytest.approx(at_bottom, rel=0.02)


def test_only_the_legs_carry_below_the_deck(
    stand: trimesh.Trimesh, stand_params: StandParams
) -> None:
    legs = 4 * stand_params.leg_mm**2

    assert material_area(stand, FOOT_HEIGHT_MM + 1.0) == pytest.approx(legs, rel=0.02)


def test_the_foot_is_wider_than_the_leg(stand: trimesh.Trimesh, stand_params: StandParams) -> None:
    """A flared foot adds first-layer area and tipping resistance, without an overhang."""
    at_floor = material_area(stand, SLAB_MM)
    at_leg = material_area(stand, FOOT_HEIGHT_MM + 1.0)

    assert at_floor > at_leg


def test_rim_stays_solid(stand: trimesh.Trimesh, stand_params: StandParams) -> None:
    """No hexagon is cut into the border, so the deck never ends in a sliver."""
    size, rim = stand_params.size_mm, stand_params.rim_mm
    band = trimesh.creation.box(extents=[size, size, SLAB_MM])
    band.apply_translation([size / 2, size / 2, stand_params.deck_z0 + 0.5])
    inner = trimesh.creation.box(extents=[size - 2 * rim, size - 2 * rim, 1e3])
    inner.apply_translation([size / 2, size / 2, 0.0])
    band = band.difference(inner)

    solid = stand.intersection(band).volume / SLAB_MM

    assert solid == pytest.approx(size**2 - (size - 2 * rim) ** 2, rel=1e-3)


def test_the_cell_field_is_centred() -> None:
    """Leftover span is split between the two borders, so the deck reads as intentional."""
    centres = np.array(cell_centres(StandParams()))
    low, high = centres.min(axis=0), centres.max(axis=0)

    assert np.allclose((low + high) / 2, StandParams().size_mm / 2, atol=1e-6)


def test_finer_cells_add_walls(stand_params: StandParams) -> None:
    fine = build_stand(
        StandParams(
            size_mm=stand_params.size_mm,
            height_mm=stand_params.height_mm,
            deck_mm=stand_params.deck_mm,
            cell_mm=stand_params.cell_mm / 2,
            leg_mm=stand_params.leg_mm,
        )
    )
    coarse = build_stand(stand_params)
    z = stand_params.deck_z0 + 0.5

    assert material_area(fine, z) > material_area(coarse, z)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("size_mm", -1.0),
        ("height_mm", 0.0),
        ("deck_mm", 0.0),
        ("cell_mm", 0.0),
        ("wall_mm", 0.0),
        ("crest_mm", 0.0),
        ("leg_mm", 0.0),
        ("rim_mm", -0.5),
    ],
)
def test_sizes_must_be_positive(field: str, value: float) -> None:
    with pytest.raises(ValueError, match=field):
        StandParams(**{field: value})


def test_crest_may_not_exceed_the_wall() -> None:
    with pytest.raises(ValueError, match="crest_mm"):
        StandParams(wall_mm=1.0, crest_mm=1.5)


def test_deck_must_leave_room_for_legs() -> None:
    with pytest.raises(ValueError, match="deck_mm"):
        StandParams(height_mm=10.0, deck_mm=10.0)


def test_rim_must_leave_an_opening() -> None:
    with pytest.raises(ValueError, match="rim_mm"):
        StandParams(size_mm=20.0, rim_mm=10.0)


def test_legs_must_fit_the_footprint() -> None:
    with pytest.raises(ValueError, match="leg_mm"):
        StandParams(size_mm=20.0, leg_mm=12.0)


def test_cell_must_fit_inside_the_rim() -> None:
    with pytest.raises(ValueError, match="cell_mm"):
        StandParams(size_mm=30.0, rim_mm=5.0, cell_mm=40.0)
