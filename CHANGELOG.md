# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-08-06

### Fixed

- `S`, `C` and `G` came out as blobs. Silhouette rounding did a morphological closing
  before the opening, and closing bridges every gap narrower than its radius: at
  `--puff 14` that is 6.3 mm, which swallowed both apertures of a fat `S` and grew its area
  by 10 percent. Rounding is now opening only, so it can never add material. Inner corners
  are left to the inflation, which rounds them in 3D anyway.

### Added

- `--fullness` (default `4`): shapes the cross-section from a plain semicircle towards a
  balloon by steepening the flanks and broadening the top, without moving any ridge. The
  reference for the power is the local ridge height, not the letter's peak, so thin strokes
  are not stretched up towards the tallest one.

## [0.5.0] - 2026-08-06

The shape is now solved, not sculpted.

### Changed

- Thickness comes from a membrane clamped to the outline under uniform pressure
  (`laplace(u) = -1`, `h = sqrt(2u)`) instead of a profile built from the distance to the
  outline. A straight stroke still comes out as a semicircle of its own half-width, but the
  surface is smooth everywhere, so the ridge along the centre line, the creases radiating
  from corners and the dents at junctions are all gone: a junction now bulges, because a
  wider patch of membrane deflects further. Measured as pixels where the surface curves the
  wrong way: 54 on a DejaVu `K`, now zero.
- `--puff` is a ceiling. Letters are never stretched taller than the membrane naturally
  sits, which is what keeps a thin stroke from becoming a sausage.

### Removed

- `--roll` and `--profile`. Both existed to hand-shape a profile that the membrane now
  derives, and neither had a meaning left.
- `local_thickness`, the granulometry the previous profile was normalised by.

### Fixed

- Decimation fidelity was measured on a band selected by distance from the outline, which on
  a thin stroke left almost nothing to check. It now follows height above the base fillet, so
  plates on the dome are caught: a DejaVu `H` at a 3000-face budget went from 2.0 mm to
  0.7 mm of dome facet inradius.

## [0.4.0] - 2026-08-06

Letters shaped like inflated bubbles, front and back.

### Changed

- The inflation profile is normalised by the local stroke thickness (a granulometry of the
  glyph) instead of one distance per letter. Every stroke becomes a tube of its own width and
  the surface levels off at the centre line, so letters no longer come out with a tent ridge
  and creases fanning out of every corner.
- `--puff` is capped per stroke rather than per letter, so a thin stroke next to a fat
  junction stays proportional instead of inflating into a sausage.

### Added

- `--base-round`: a fillet under the letter, default `0.25 * puff`. The bottom stays flat and
  support-free, but the outline curves down into a slightly smaller contact patch instead of
  meeting the plate at a right angle.

### Removed

- `--dome`. It added its bulge at the medial axis, which sharpened the very ridge it was
  meant to soften, and with per-stroke normalisation it only scaled `--puff`.

## [0.3.0] - 2026-08-06

Letters that actually read as bubbles. Three shaping defects, all visible in print.

### Fixed

- Silhouette rounding filled counters and bridged apertures: `R` printed as a blob with a
  notch and `G` lost its aperture, because closing with `0.45 * puff` (5.4 mm at
  `--puff 12`) bridges every gap narrower than its radius. The radius is now backed off per
  letter until the glyph keeps its counters, its strokes and roughly its area, and the value
  used is logged.
- Straight letters printed as extrusions with a chamfer: `--roll` defaulted to `--puff`, so
  any stroke wider than `2 * puff` got a flat plateau across its middle (18-23% of the area
  for TitanOne at 80 mm). The roll now follows each glyph's own half-width, putting the peak
  at the centre of the stroke.
- Light fonts inflated into tubes: thickness is now capped per letter at the stroke
  half-width, so a peak can never exceed half the width it sits on. DejaVu Sans at
  `--size 60 --puff 8` was 2.2 times taller than wide. The cap is logged.
- Letters with straight strokes printed low-poly: quadric decimation treats the
  developable surface of a straight stroke as free to flatten and collapsed whole strips
  into plates (single dome facets of 69 mm2 on `I` and 264 mm2 on `R`, up to 1.4 mm off the
  intended surface). Every candidate is now checked against the height field it should
  follow and rejected if it adds more than 0.15 mm of error, so `I` and `R` keep 160k
  triangles instead of shipping as polyhedra.
- A face budget at or above the dense triangle count crashed `fast-simplification`, which
  surfaced as a misleading "decimation unavailable" warning.

### Removed

- `MeshError`, which nothing raises now that rounding backs off instead of failing.

## [0.2.0] - 2026-08-06

Wall letters, not keyrings: one shape mode, flat bottom always.

### Removed

- The keyring hole (`--hole`, `--hole-wall`, `bubblegen.hole`).
- The two-sided pillow mode (`--flat-back`). A flat bottom at `z = 0` is now the only
  output, since that is what hangs on a wall and prints without supports.

### Added

- `make fonts` and `scripts/fetch_fonts.py`: downloads four heavy OFL display fonts into
  `fonts/`, pinning variable fonts to their heaviest instance.
- A warning when silhouette rounding removes more than half the glyph, and a `MeshError`
  when it erases the glyph completely, instead of exporting a near-empty mesh.

### Fixed

- Taubin smoothing ran after decimation and diverged on the irregular triangles decimation
  leaves behind: letters collapsed instead of rounding. Nunito Black at `--puff 8` lost half
  its volume (8598 -> 4359 mm3) and 13 mm of height. Smoothing now runs while the mesh is
  still dense.
- `dilate` on an empty mask returned a filled mask (scipy's EDT has no background to measure
  against), so a rounding radius that erased the glyph produced a solid slab.

## [0.1.0] - 2026-08-06

First packaged release. The single `bubble_letters.py` script became the `bubblegen`
package, with the pipeline split into modules and covered by tests.

### Added

- `bubblegen` CLI (`bubblegen`, `python -m bubblegen`) with grouped options and log levels.
- Library API: `Font`, `BubbleParams`, `Profile`, `build_letter`, `build_alphabet`,
  `export_stl`, `LetterMesh`.
- `BubbleParams`: frozen, validated on construction, so bad values fail before meshing.
- Exception hierarchy under `BubbleGenError` instead of printed messages.
- Test suite covering fonts, rasterisation, inflation, hole placement, meshing, pipeline
  and CLI.

### Fixed

- Domes above `0.25` were clipped flat: the marching-cubes grid stopped at `1.25 * puff`
  while the dome pushes the peak to `puff * (1 + dome)`.
- Cap height for fonts with an OS/2 version 1 table (no `sCapHeight`) is now measured from
  a flat-topped capital instead of guessed as `0.72 * ascender`, which was off by 9 percent
  on DejaVu Sans.
- `--faces` was quietly ignored on most letters: quadric decimation leaves a few zero-area
  faces, which made the candidate read as non-manifold, so the dense mesh was exported
  (130k triangles instead of 40k). Degenerate faces are now dropped before the check.
- A failed keyring-hole boolean now raises `MeshError` instead of silently exporting an
  undrilled letter.
