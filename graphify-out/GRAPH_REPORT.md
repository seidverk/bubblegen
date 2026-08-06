# Graph Report - bubble-alphabet-is  (2026-08-06)

## Corpus Check
- 25 files · ~8,664 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 268 nodes · 560 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 109 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1e34cdb6`
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
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]

## God Nodes (most connected - your core abstractions)
1. `BubbleParams` - 71 edges
2. `Font` - 35 edges
3. `build_letter()` - 23 edges
4. `rasterize()` - 18 edges
5. `height_field()` - 16 edges
6. `FlattenPen` - 15 edges
7. `build_mesh()` - 15 edges
8. `square()` - 15 edges
9. `puffed_square()` - 15 edges
10. `Raster` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_font_and_chars_are_required()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/bubblegen/cli.py
- `test_automatic_roll_has_a_floor()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_explicit_roll_and_round_win()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_invalid_values_rejected()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_margin_covers_puff_and_rounding()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py

## Import Cycles
- None detected.

## Communities (14 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (16): BasePen, Exception, BubbleGenError, EmptyGlyphError, FontError, GlyphNotFoundError, Exception hierarchy: every expected failure is a `BubbleGenError`., Font file missing, unreadable, or not a font. (+8 more)

### Community 1 - "Community 1"
Cohesion: 0.22
Nodes (9): Any, download(), main(), pin_instance(), Path, Path, Path, test_load_reports_missing_file() (+1 more)

### Community 2 - "Community 2"
Cohesion: 0.18
Nodes (8): export_stl(), LetterMesh, Path, Write the letter as `bubble_<name>.stl` and return the path., One finished letter, resting on z = 0., Filename-safe name for a character., slug(), test_slug()

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (16): ArgumentParser, CaptureFixture, Namespace, build_parser(), _configure_logging(), main(), params_from_args(), Command line entry point. (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (17): BubbleParams, Thickness for a glyph whose deepest point is `deepest_mm` in.          Capped so, Edge roll distance for a glyph whose deepest point is `deepest_mm` in., Blank border around the glyph so inflation and rounding never clip., Geometry and sampling parameters for one batch of letters.      Distances are mi, Field, Say so when the stroke, not `--puff`, is what sets the thickness., _report_puff_cap() (+9 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (27): build_mesh(), _decimate(), _drop_degenerate_faces(), float64, NDArray, Height field to a watertight triangle mesh with a flat, printable bottom., Worst gap between the inflated top of `mesh` and the height field it follows., Marching cubes is very dense; trim it to keep STL files sane.      Quadric decim (+19 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (35): Mask, dilate(), enclosed_gaps(), erode(), Contour, Field, rasterize(), Contours to a pixel mask, and the mask to a signed distance field. (+27 more)

### Community 7 - "Community 7"
Cohesion: 0.19
Nodes (20): height_field(), Field, The inflation itself: signed distance in, half-thickness out., Half-thickness h(x, y) in mm from the signed distance field.      Outside the gl, float64, NDArray, One-dimensional signed distance ramp: outside, edge roll, deep interior., Without an explicit roll the peak must sit at the deepest point only: a fixed (+12 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (12): bubblegen, Development, Fonts, How it works, Install, Layout, Library use, License (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.17
Nodes (11): [0.1.0] - 2026-08-06, [0.2.0] - 2026-08-06, [0.3.0] - 2026-08-06, Added, Added, Changelog, Fixed, Fixed (+3 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (33): LogCaptureFixture, Font, Glyph outlines from a TTF/OTF, flattened to polylines and scaled to mm., Font units a capital letter occupies, so all letters share one scale.          O, A loaded font, queried per character., build_alphabet(), build_letter(), Build every character, skipping whitespace and glyphs the font cannot supply. (+25 more)

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (11): Profile, All tunables in one immutable, validated object., Shape of the edge roll — how the surface climbs from 0 to full thickness., Parametric inflated 3D bubble letters from any TTF/OTF font., StrEnum, font(), font_path(), params() (+3 more)

## Knowledge Gaps
- **19 isolated node(s):** `bubblegen`, `Fixed`, `Removed`, `Removed`, `Added` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BubbleParams` connect `Community 4` to `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 7`, `Community 12`, `Community 13`?**
  _High betweenness centrality (0.358) - this node is a cross-community bridge._
- **Why does `Font` connect `Community 12` to `Community 0`, `Community 1`, `Community 2`?**
  _High betweenness centrality (0.196) - this node is a cross-community bridge._
- **Why does `build_letter()` connect `Community 12` to `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `BubbleParams` (e.g. with `LetterMesh` and `Raster`) actually correct?**
  _`BubbleParams` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Font` (e.g. with `EmptyGlyphError` and `FontError`) actually correct?**
  _`Font` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `build_letter()` (e.g. with `height_field()` and `build_mesh()`) actually correct?**
  _`build_letter()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `rasterize()` (e.g. with `build_letter()` and `puffed_square()`) actually correct?**
  _`rasterize()` has 13 INFERRED edges - model-reasoned connections that need verification._