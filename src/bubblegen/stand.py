"""A honeycomb-topped stand that holds a letter while it is painted with UV resin.

The letter rests on wall crests rather than on a surface: resin drips through the deck,
and what cures cannot glue the letter down over an area.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import numpy as np
import trimesh

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import NDArray

SQRT3 = math.sqrt(3.0)

FOOT_FLARE_MM = 1.0
FOOT_HEIGHT_MM = 2.0
"""Each leg widens by the flare per side over the foot height. The flare leans inward
going up, so it buys first-layer area and tipping resistance without an overhang."""

LEG_OVERLAP_MM = 0.5
"""How far the legs reach into the deck, so the union meets a volume, not two coplanar
faces."""

HOLE_OVERSHOOT_MM = 1.0
"""How far the cells stick out of both deck faces, for the same reason."""

SQUARE = np.array([(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)])
"""Unit square, counter-clockwise: the leg cross-section before scaling."""


@dataclass(frozen=True, slots=True)
class StandParams:
    """Geometry of one stand. Distances are millimetres, as everywhere in bubblegen."""

    size_mm: float = 80.0
    """Deck side. A letter wider than this overhangs and rocks when painted."""

    height_mm: float = 18.0
    """Total height, legs plus deck. Low on purpose: a stool, not a table."""

    deck_mm: float = 6.0
    """Deck thickness. It is also the length of the wall taper."""

    cell_mm: float = 8.0
    """Hexagon across the flats, measured at the underside."""

    wall_mm: float = 1.2
    """Wall thickness at the underside, where the deck needs its stiffness."""

    crest_mm: float = 0.6
    """Wall thickness at the crest, where the letter touches.

    The difference against `wall_mm` is what drafts the cells: thinner means a finer
    contact line and a steeper hole, so resin bridges less and the deck stays stiff.
    """

    rim_mm: float = 2.5
    """Solid border. Only cells that clear it are cut, so no sliver is left at the edge."""

    leg_mm: float = 6.0
    """Corner post section, above the flared foot."""

    def __post_init__(self) -> None:
        self._require_positive("size_mm", self.size_mm)
        self._require_positive("height_mm", self.height_mm)
        self._require_positive("deck_mm", self.deck_mm)
        self._require_positive("cell_mm", self.cell_mm)
        self._require_positive("wall_mm", self.wall_mm)
        self._require_positive("crest_mm", self.crest_mm)
        self._require_positive("leg_mm", self.leg_mm)
        if self.rim_mm < 0:
            raise ValueError(f"rim_mm must not be negative, got {self.rim_mm}")
        if self.crest_mm > self.wall_mm:
            raise ValueError(
                f"crest_mm must not exceed wall_mm {self.wall_mm}, got {self.crest_mm}"
            )
        if self.deck_mm >= self.height_mm:
            raise ValueError(
                f"deck_mm must leave room for the legs below height_mm {self.height_mm}, "
                f"got {self.deck_mm}"
            )
        if self.inner_span <= 0:
            raise ValueError(
                f"rim_mm must leave an opening in a {self.size_mm} mm deck, got {self.rim_mm}"
            )
        if 2 * self.foot_mm > self.size_mm:
            raise ValueError(
                f"leg_mm plus its foot must fit twice across {self.size_mm} mm, got {self.leg_mm}"
            )
        if 2 * self.widest_cell_mm / SQRT3 > self.inner_span:
            raise ValueError(
                f"cell_mm must fit inside the {self.inner_span} mm opening, got {self.cell_mm}"
            )

    @staticmethod
    def _require_positive(name: str, value: float) -> None:
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")

    @property
    def deck_z0(self) -> float:
        """Underside of the deck: everything below it is legs."""
        return self.height_mm - self.deck_mm

    @property
    def pitch(self) -> float:
        """Centre distance between neighbouring cells, which is a cell plus a wall."""
        return self.cell_mm + self.wall_mm

    @property
    def inner_span(self) -> float:
        """Free span inside the rim."""
        return self.size_mm - 2 * self.rim_mm

    @property
    def crest_gain(self) -> float:
        """How much wider a cell is at the crest, across the flats."""
        return self.wall_mm - self.crest_mm

    @property
    def widest_cell_mm(self) -> float:
        return self.cell_mm + self.crest_gain

    @property
    def foot_mm(self) -> float:
        return self.leg_mm + 2 * FOOT_FLARE_MM


def build_stand(params: StandParams) -> trimesh.Trimesh:
    """Deck with the cells cut out, standing on four legs, sitting on z = 0."""
    return _deck(params).union(_legs(params))


def _hexagon(across_flats: float) -> NDArray[np.float64]:
    """Pointy-top hexagon centred on the origin, counter-clockwise.

    Pointy-top puts the flats left and right, so the horizontal pitch is one cell plus
    one wall and every wall in the lattice comes out the same thickness.
    """
    radius = across_flats / SQRT3
    angles = np.radians(np.arange(30.0, 360.0, 60.0))
    return np.column_stack([radius * np.cos(angles), radius * np.sin(angles)])


def _loft(rings: Sequence[NDArray[np.float64]], heights: Sequence[float]) -> trimesh.Trimesh:
    """Close a stack of equally sized rings into a solid, bottom ring first.

    Rings run counter-clockwise seen from above, which puts the side normals outward.
    """
    corners = len(rings[0])
    vertices = np.vstack(
        [
            np.column_stack([ring, np.full(corners, z)])
            for ring, z in zip(rings, heights, strict=True)
        ]
    )

    faces = []
    for level in range(len(rings) - 1):
        low, high = level * corners, (level + 1) * corners
        for corner in range(corners):
            nxt = (corner + 1) % corners
            faces.append([low + corner, low + nxt, high + nxt])
            faces.append([low + corner, high + nxt, high + corner])

    top = (len(rings) - 1) * corners
    faces += [[0, k + 1, k] for k in range(1, corners - 1)]
    faces += [[top, top + k, top + k + 1] for k in range(1, corners - 1)]

    return trimesh.Trimesh(vertices=vertices, faces=np.array(faces), process=False)


def cell_centres(params: StandParams) -> list[tuple[float, float]]:
    """Cell centres whose whole footprint clears the rim, centred on the deck.

    Cutting a partial hexagon into the border would leave a wall too thin to print, so a
    cell that does not fit entirely is simply not cut. What the dropped cells leave over
    is then split between the two borders, rather than piling up against one of them.
    """
    row_pitch = params.pitch * SQRT3 / 2
    half_x = params.widest_cell_mm / 2
    half_y = params.widest_cell_mm / SQRT3
    middle = params.size_mm / 2
    columns = int(params.size_mm / params.pitch) + 2
    rows = int(params.size_mm / row_pitch) + 2

    centres = []
    for row in range(-rows, rows + 1):
        y = middle + row * row_pitch
        stagger = params.pitch / 2 if row % 2 else 0.0
        for column in range(-columns, columns + 1):
            x = middle + column * params.pitch + stagger
            fits_x = params.rim_mm <= x - half_x and x + half_x <= params.size_mm - params.rim_mm
            fits_y = params.rim_mm <= y - half_y and y + half_y <= params.size_mm - params.rim_mm
            if fits_x and fits_y:
                centres.append((x, y))

    field = np.array(centres)
    shift = middle - (field.min(axis=0) + field.max(axis=0)) / 2
    return [(x + shift[0], y + shift[1]) for x, y in centres]


def _cell(params: StandParams, x: float, y: float) -> trimesh.Trimesh:
    """One drafted cell: `cell_mm` across the flats underneath, `crest_gain` wider on top.

    It overshoots both deck faces so the difference never has to resolve a coplanar pair.
    """
    slope = params.crest_gain / params.deck_mm
    low, high = -HOLE_OVERSHOOT_MM, params.deck_mm + HOLE_OVERSHOOT_MM
    centre = np.array([x, y])
    rings = [_hexagon(params.cell_mm + slope * z) + centre for z in (low, high)]
    return _loft(rings, [params.deck_z0 + low, params.deck_z0 + high])


def _deck(params: StandParams) -> trimesh.Trimesh:
    slab = trimesh.creation.box(
        extents=[params.size_mm, params.size_mm, params.deck_mm],
        transform=trimesh.transformations.translation_matrix(
            [params.size_mm / 2, params.size_mm / 2, params.deck_z0 + params.deck_mm / 2]
        ),
    )
    cells = [_cell(params, x, y) for x, y in cell_centres(params)]
    hollow: trimesh.Trimesh = slab.difference(_merge(cells))
    return hollow


def _legs(params: StandParams) -> trimesh.Trimesh:
    """Four corner posts, flared at the foot and reaching up into the deck.

    The posts sit a flare in from the deck outline, so the widest part of a foot is
    flush with the edge and nothing sticks out of the footprint.
    """
    rings = [SQUARE * params.foot_mm / 2, SQUARE * params.leg_mm / 2, SQUARE * params.leg_mm / 2]
    heights = [0.0, FOOT_HEIGHT_MM, params.deck_z0 + LEG_OVERLAP_MM]
    inset = params.foot_mm / 2

    corners = [
        np.array([x, y])
        for x in (inset, params.size_mm - inset)
        for y in (inset, params.size_mm - inset)
    ]
    posts = [_loft([ring + corner for ring in rings], heights) for corner in corners]
    return _merge(posts)


def _merge(parts: Sequence[trimesh.Trimesh]) -> trimesh.Trimesh:
    """Carry bodies that never touch as one mesh; the booleans take it as it is."""
    return cast("trimesh.Trimesh", trimesh.util.concatenate(parts))
