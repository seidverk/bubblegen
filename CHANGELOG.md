# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
