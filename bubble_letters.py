#!/usr/bin/env python3
"""
bubble_letters.py — parametric "inflated / puffy" 3D letters from any TTF/OTF font.

Pipeline:
    glyph outline (fontTools)
      -> flattened contours
      -> raster mask (matplotlib Path, non-zero winding => holes work)
      -> signed distance field in mm (scipy EDT)
      -> height profile h(d)  (the "inflation")
      -> 3D scalar field  f = h(x,y) - |z|
      -> marching cubes (scikit-image)
      -> Taubin smoothing (trimesh)
      -> watertight STL

Everything is procedural: no manual sculpting, whole alphabet in one run.
"""

import argparse
import math
import os
import re
import sys

import numpy as np
from scipy import ndimage
from skimage import measure
from matplotlib.path import Path as MplPath

import trimesh
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen


# --------------------------------------------------------------------------
# 1. Font outline extraction
# --------------------------------------------------------------------------

class FlattenPen(BasePen):
    """Collects glyph contours as flat polylines (beziers sampled into lines)."""

    def __init__(self, glyphSet, steps=24):
        super().__init__(glyphSet)
        self.steps = steps
        self.contours = []
        self._current = []

    def _moveTo(self, pt):
        self._flushContour()
        self._current = [pt]

    def _lineTo(self, pt):
        self._current.append(pt)

    def _curveToOne(self, p1, p2, p3):
        # cubic bezier sampling; BasePen converts quadratics to cubics for us
        p0 = self._current[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1.0 - t
            x = (mt**3 * p0[0] + 3 * mt**2 * t * p1[0]
                 + 3 * mt * t**2 * p2[0] + t**3 * p3[0])
            y = (mt**3 * p0[1] + 3 * mt**2 * t * p1[1]
                 + 3 * mt * t**2 * p2[1] + t**3 * p3[1])
            self._current.append((x, y))

    def _closePath(self):
        self._flushContour()

    def _endPath(self):
        self._flushContour()

    def _flushContour(self):
        if len(self._current) >= 3:
            self.contours.append(np.asarray(self._current, dtype=np.float64))
        self._current = []

    def result(self):
        self._flushContour()
        return self.contours


def glyph_contours(font, glyph_set, char, steps=24):
    """Return list of contours (Nx2 arrays) in font units for one character."""
    cmap = font.getBestCmap()
    code = ord(char)
    if code not in cmap:
        raise KeyError(f"glyph for {char!r} (U+{code:04X}) not found in font")
    name = cmap[code]
    pen = FlattenPen(glyph_set, steps=steps)
    glyph_set[name].draw(pen)
    contours = pen.result()
    if not contours:
        raise ValueError(f"{char!r} produced an empty outline (whitespace?)")
    return contours


def font_reference_height(font):
    """Units that a capital letter occupies — used so all letters share one scale."""
    if "OS/2" in font and getattr(font["OS/2"], "sCapHeight", 0):
        return float(font["OS/2"].sCapHeight)
    return float(font["hhea"].ascender) * 0.72


# --------------------------------------------------------------------------
# 2. Rasterisation + signed distance
# --------------------------------------------------------------------------

def rasterize(contours, px_mm, margin_mm):
    """Rasterize contours (already in mm) to a boolean mask.

    Returns (mask, origin_xy) where origin maps pixel (0,0) to mm coordinates.
    """
    allpts = np.vstack(contours)
    lo = allpts.min(axis=0) - margin_mm
    hi = allpts.max(axis=0) + margin_mm

    w = int(math.ceil((hi[0] - lo[0]) * px_mm))
    h = int(math.ceil((hi[1] - lo[1]) * px_mm))

    xs = lo[0] + (np.arange(w) + 0.5) / px_mm
    ys = lo[1] + (np.arange(h) + 0.5) / px_mm
    gx, gy = np.meshgrid(xs, ys)
    pts = np.column_stack([gx.ravel(), gy.ravel()])

    # Test each contour separately and XOR them (even-odd rule).
    # matplotlib's containment test is unreliable on compound paths, and even-odd
    # is correct for font outlines: counters simply flip the state.
    mask = np.zeros(h * w, dtype=bool)
    for c in contours:
        poly = MplPath(np.vstack([c, c[:1]]), closed=True)
        mask ^= poly.contains_points(pts)

    return mask.reshape(h, w), lo


def _dilate(mask, px_mm, r):
    if r <= 0:
        return mask
    d = ndimage.distance_transform_edt(~mask) / px_mm
    return mask | (d <= r)


def _erode(mask, px_mm, r):
    if r <= 0:
        return mask
    d = ndimage.distance_transform_edt(mask) / px_mm
    return d > r


def soften(mask, px_mm, r):
    """Round the silhouette itself — this is what makes letters read as 'bubble'.

    closing (dilate+erode) rounds inner corners and fuses strokes that nearly touch,
    opening (erode+dilate) rounds the sharp outer tips (A apex, W, Ж, Æ).
    """
    if r <= 0:
        return mask
    m = _erode(_dilate(mask, px_mm, r), px_mm, r)
    m = _dilate(_erode(m, px_mm, r), px_mm, r)
    return m


def signed_distance(mask, px_mm):
    """Signed distance in mm: positive inside the glyph, negative outside."""
    inside = ndimage.distance_transform_edt(mask) / px_mm
    outside = ndimage.distance_transform_edt(~mask) / px_mm
    return inside - outside


# --------------------------------------------------------------------------
# 3. Inflation profile
# --------------------------------------------------------------------------

def height_field(sd, puff, roll, dome, profile):
    """Half-thickness h(x,y) in mm from the signed distance field.

    puff    : max half-thickness (total part thickness = 2*puff, or puff if flat back)
    roll    : distance over which the edge rounds up to full thickness
    dome    : extra bulge in the middle, as a fraction of puff (0 = flat top)
    profile : shape of that edge roll
    """
    t = np.clip(sd / max(roll, 1e-6), 0.0, 1.0)

    if profile == "sphere":          # quarter-circle roll — classic pillow edge
        edge = np.sqrt(np.clip(1.0 - (1.0 - t) ** 2, 0.0, None))
    elif profile == "smooth":        # smoothstep — softer, more "balloon"
        edge = t * t * (3.0 - 2.0 * t)
    elif profile == "super":         # superellipse — fuller, squarer shoulder
        n = 3.0
        edge = (1.0 - (1.0 - t) ** n) ** (1.0 / n)
    else:
        raise ValueError(f"unknown profile {profile!r}")

    h = puff * edge

    if dome > 0.0:
        # gentle global bulge: proportional to how deep inside the stroke we are
        deep = np.clip(sd, 0.0, None)
        dmax = deep.max() if deep.max() > 0 else 1.0
        h = h + puff * dome * edge * (deep / dmax)

    # outside the glyph the field must go negative so the isosurface closes
    h = np.where(sd > 0, h, sd)
    return h


def find_hole_center(sd, mask, hole_r, wall, lo, px_mm, where="top"):
    """Pick a keyring-hole centre that still leaves `wall` mm of material."""
    need = hole_r + wall
    ok = sd >= need
    if not ok.any():
        return None
    ys, xs = np.nonzero(ok)
    if where == "top":
        best_y = ys.max()
        band = ys >= best_y - max(1, int(0.5 * px_mm))
    else:
        best_y = ys.min()
        band = ys <= best_y + max(1, int(0.5 * px_mm))
    cx = xs[band].mean()
    # among the band pick the pixel closest to its horizontal centre
    cand = np.argmin(np.abs(xs[band] - cx))
    px, py = xs[band][cand], ys[band][cand]
    return (lo[0] + (px + 0.5) / px_mm, lo[1] + (py + 0.5) / px_mm)


# --------------------------------------------------------------------------
# 4. Meshing
# --------------------------------------------------------------------------

def cut_hole(mesh, center, radius, puff):
    """Drill the keyring hole as a real boolean (needs `pip install manifold3d`).

    Doing it as a boolean rather than carving the scalar field keeps the mesh
    manifold — a min() crease in the field makes marching cubes emit bad edges.
    """
    cyl = trimesh.creation.cylinder(radius=radius, height=puff * 8, sections=64)
    cyl.apply_translation([center[0], center[1], 0.0])
    try:
        out = trimesh.boolean.difference([mesh, cyl])
        if out is not None and len(out.faces) > 0:
            return out
    except Exception as e:
        print(f"    (hole boolean failed, install manifold3d: {e})")
    return mesh


def build_mesh(h, lo, px_mm, puff, flat_back, z_steps, smooth=12,
               target_faces=40000):
    """Marching-cubes a height field into a watertight mesh."""
    if flat_back:
        z0, z1 = -0.6 * puff, puff * 1.25
    else:
        z0, z1 = -puff * 1.25, puff * 1.25

    zs = np.linspace(z0, z1, z_steps)
    dz = zs[1] - zs[0]

    H = h[:, :, None]
    Z = zs[None, None, :]

    if flat_back:
        # solid between z = 0 and z = h  -> flat printable back
        field = np.minimum(H - Z, Z)
    else:
        # symmetric pillow, inflated on both sides
        field = H - np.abs(Z)

    # pad with negative values so the isosurface is always closed
    field = np.pad(field, 1, mode="constant", constant_values=-1e3)

    verts, faces, normals, _ = measure.marching_cubes(
        field, level=0.0, spacing=(1.0 / px_mm, 1.0 / px_mm, dz)
    )

    # marching cubes returns (row, col, z) = (y, x, z) -> reorder to x, y, z
    v = np.column_stack([
        verts[:, 1] + lo[0] - 1.0 / px_mm,
        verts[:, 0] + lo[1] - 1.0 / px_mm,
        verts[:, 2] + z0 - dz,
    ])

    mesh = trimesh.Trimesh(vertices=v, faces=faces, process=True)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    mesh.fix_normals()

    # Marching cubes is very dense; decimate to keep STL files sane.
    # Decimation can occasionally punch a non-manifold edge, so verify and retry
    # with a looser budget before giving up and keeping the (valid) dense mesh.
    if target_faces and len(mesh.faces) > target_faces:
        dense = mesh
        for budget in (target_faces, int(target_faces * 1.5), target_faces * 2):
            try:
                cand = dense.simplify_quadric_decimation(face_count=budget)
            except Exception as e:  # optional dependency missing
                print(f"    (decimation unavailable: {e})")
                break
            if cand.is_watertight:
                mesh = cand
                break
        else:
            print("    (decimation kept breaking the mesh, exporting dense version)")

    if smooth > 0:
        # Taubin keeps volume (unlike plain Laplacian) — no shrinking
        trimesh.smoothing.filter_taubin(mesh, lamb=0.5, nu=-0.53, iterations=smooth)

    return mesh


# --------------------------------------------------------------------------
# 5. Driver
# --------------------------------------------------------------------------

def safe_name(ch):
    if re.match(r"[A-Za-z0-9]", ch):
        return ch
    return f"U{ord(ch):04X}"


def main():
    ap = argparse.ArgumentParser(description="Generate inflated 'bubble' letter STLs.")
    ap.add_argument("--font", required=True, help="path to .ttf / .otf")
    ap.add_argument("--chars", required=True, help='characters, e.g. "ABCÞÐÆ" or "АБВ"')
    ap.add_argument("--out", default="out", help="output directory")

    ap.add_argument("--size", type=float, default=60.0,
                    help="cap height in mm (all letters share this scale)")
    ap.add_argument("--puff", type=float, default=7.0,
                    help="max half-thickness in mm")
    ap.add_argument("--roll", type=float, default=None,
                    help="edge rounding distance in mm (default = puff)")
    ap.add_argument("--round", dest="round_r", type=float, default=None,
                    help="silhouette rounding radius in mm (default = 0.45*puff)")
    ap.add_argument("--dome", type=float, default=0.15,
                    help="extra centre bulge, 0..0.5")
    ap.add_argument("--profile", default="sphere",
                    choices=["sphere", "smooth", "super"])
    ap.add_argument("--flat-back", action="store_true",
                    help="flat bottom, prints with zero supports")

    ap.add_argument("--hole", type=float, default=0.0,
                    help="keyring hole diameter in mm (0 = none)")
    ap.add_argument("--hole-wall", type=float, default=2.0,
                    help="min material around the hole in mm")

    ap.add_argument("--res", type=float, default=5.0, help="pixels per mm")
    ap.add_argument("--zsteps", type=int, default=64, help="vertical samples")
    ap.add_argument("--smooth", type=int, default=12, help="Taubin iterations")
    ap.add_argument("--faces", type=int, default=40000,
                    help="target triangle count (0 = keep raw marching-cubes mesh)")
    ap.add_argument("--bezier-steps", type=int, default=24)
    args = ap.parse_args()

    roll = args.roll if args.roll is not None else args.puff
    round_r = args.round_r if args.round_r is not None else 0.45 * args.puff

    os.makedirs(args.out, exist_ok=True)
    font = TTFont(args.font, fontNumber=0)
    glyph_set = font.getGlyphSet()
    upem = font["head"].unitsPerEm
    scale = args.size / font_reference_height(font)  # font units -> mm

    print(f"font: {os.path.basename(args.font)}  upem={upem}  scale={scale:.5f} mm/unit")

    for ch in args.chars:
        if ch.isspace():
            continue
        try:
            contours = glyph_contours(font, glyph_set, ch, steps=args.bezier_steps)
        except (KeyError, ValueError) as e:
            print(f"  skip {ch!r}: {e}")
            continue

        contours = [c * scale for c in contours]
        margin = args.puff * 1.5 + round_r * 2.5 + 1.0

        mask, lo = rasterize(contours, args.res, margin)
        mask = soften(mask, args.res, round_r)
        sd = signed_distance(mask, args.res)

        hole = None
        if args.hole > 0:
            c = find_hole_center(sd, mask, args.hole / 2, args.hole_wall,
                                 lo, args.res)
            if c is None:
                print(f"  {ch!r}: no room for a {args.hole} mm hole, skipping hole")
            else:
                hole = (c, args.hole / 2)

        h = height_field(sd, args.puff, roll, args.dome, args.profile)
        mesh = build_mesh(h, lo, args.res, args.puff, args.flat_back,
                          args.zsteps, smooth=args.smooth,
                          target_faces=args.faces)

        if hole is not None:
            mesh = cut_hole(mesh, hole[0], hole[1], args.puff)

        # drop to z = 0 so it lands on the build plate
        mesh.apply_translation([0, 0, -mesh.bounds[0][2]])

        path = os.path.join(args.out, f"bubble_{safe_name(ch)}.stl")
        mesh.export(path)
        bb = mesh.bounds[1] - mesh.bounds[0]
        print(f"  {ch}  ->  {os.path.basename(path)}  "
              f"{bb[0]:.1f} x {bb[1]:.1f} x {bb[2]:.1f} mm  "
              f"{len(mesh.faces)} tris  watertight={mesh.is_watertight}")

    print("done ->", os.path.abspath(args.out))


if __name__ == "__main__":
    sys.exit(main())
