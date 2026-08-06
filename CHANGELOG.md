# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
