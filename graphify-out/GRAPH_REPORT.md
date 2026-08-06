# Graph Report - bubble-alphabet-is  (2026-08-06)

## Corpus Check
- 26 files · ~6,827 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 237 nodes · 488 edges · 12 communities (10 shown, 2 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 91 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8ad7da4a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]

## God Nodes (most connected - your core abstractions)
1. `BubbleParams` - 60 edges
2. `Font` - 30 edges
3. `build_letter()` - 19 edges
4. `FlattenPen` - 15 edges
5. `build_mesh()` - 15 edges
6. `rasterize()` - 15 edges
7. `puffed_square()` - 15 edges
8. `square()` - 12 edges
9. `sdf_of_square()` - 12 edges
10. `height_field()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `test_font_and_chars_are_required()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/bubblegen/cli.py
- `test_explicit_roll_and_round_win()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_hole_radius_is_half_the_diameter()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_invalid_values_rejected()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_margin_covers_puff_and_rounding()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py

## Import Cycles
- None detected.

## Communities (12 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (35): Any, BasePen, Exception, BubbleGenError, EmptyGlyphError, FontError, GlyphNotFoundError, MeshError (+27 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (27): Mask, drill_hole(), find_hole_center(), float64, NDArray, Trimesh, Keyring hole: where to put it, and how to drill it., Hole centre in mm that still leaves `hole_wall_mm` of material, or None. (+19 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (22): build_alphabet(), build_letter(), export_stl(), LetterMesh, Path, End-to-end: character in, printable mesh out., One finished letter, resting on z = 0., Filename-safe name for a character. (+14 more)

### Community 3 - "Community 3"
Cohesion: 0.13
Nodes (20): ArgumentParser, CaptureFixture, Namespace, build_parser(), _configure_logging(), main(), params_from_args(), Command line entry point. (+12 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (14): BubbleParams, Blank border around the glyph so inflation and rounding never clip., Geometry and sampling parameters for one batch of letters.      Distances are mi, params(), Small and coarse: keeps meshing tests in the millisecond range., test_explicit_roll_and_round_win(), test_hole_radius_is_half_the_diameter(), test_invalid_values_rejected() (+6 more)

### Community 5 - "Community 5"
Cohesion: 0.20
Nodes (19): build_mesh(), _decimate(), _drop_degenerate_faces(), float64, NDArray, Trimesh, Height field to a watertight triangle mesh., Marching-cubes the height field, then clean, decimate and smooth it. (+11 more)

### Community 6 - "Community 6"
Cohesion: 0.21
Nodes (18): Contour, rasterize(), Rasterize contours (in mm) to a boolean mask with a blank margin., font(), font_path(), Path, SquareFactory, Shared fixtures. DejaVu Sans ships with matplotlib, so tests need no font assets (+10 more)

### Community 7 - "Community 7"
Cohesion: 0.28
Nodes (13): height_field(), Field, The inflation itself: signed distance in, half-thickness out., Half-thickness h(x, y) in mm from the signed distance field.      Outside the gl, float64, NDArray, One-dimensional signed distance ramp: outside, edge roll, deep interior., sd() (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.17
Nodes (11): bubblegen, Development, How it works, Install, Layout, Library use, License, Options (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.40
Nodes (4): [0.1.0] - 2026-08-06, Added, Changelog, Fixed

## Knowledge Gaps
- **13 isolated node(s):** `bubblegen`, `Added`, `Fixed`, `graphify`, `How it works` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BubbleParams` connect `Community 4` to `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.348) - this node is a cross-community bridge._
- **Why does `Font` connect `Community 0` to `Community 2`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **Why does `build_letter()` connect `Community 2` to `Community 0`, `Community 1`, `Community 4`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `BubbleParams` (e.g. with `LetterMesh` and `Raster`) actually correct?**
  _`BubbleParams` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Font` (e.g. with `EmptyGlyphError` and `FontError`) actually correct?**
  _`Font` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `build_letter()` (e.g. with `drill_hole()` and `find_hole_center()`) actually correct?**
  _`build_letter()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `FlattenPen` (e.g. with `EmptyGlyphError` and `FontError`) actually correct?**
  _`FlattenPen` has 3 INFERRED edges - model-reasoned connections that need verification._