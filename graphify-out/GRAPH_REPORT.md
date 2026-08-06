# Graph Report - bubble-alphabet-is  (2026-08-06)

## Corpus Check
- 25 files · ~7,178 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 238 nodes · 480 edges · 13 communities (11 shown, 2 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 88 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ad959168`
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

## God Nodes (most connected - your core abstractions)
1. `BubbleParams` - 57 edges
2. `Font` - 32 edges
3. `build_letter()` - 19 edges
4. `FlattenPen` - 15 edges
5. `build_mesh()` - 15 edges
6. `rasterize()` - 15 edges
7. `puffed_square()` - 15 edges
8. `LetterMesh` - 13 edges
9. `square()` - 12 edges
10. `height_field()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `test_font_and_chars_are_required()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/bubblegen/cli.py
- `test_explicit_roll_and_round_win()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_invalid_values_rejected()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_margin_covers_puff_and_rounding()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_params_are_immutable()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py

## Import Cycles
- None detected.

## Communities (13 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (35): Any, BasePen, Exception, BubbleGenError, EmptyGlyphError, FontError, GlyphNotFoundError, MeshError (+27 more)

### Community 1 - "Community 1"
Cohesion: 0.33
Nodes (6): font(), font_path(), params(), Path, Shared fixtures. DejaVu Sans ships with matplotlib, so tests need no font assets, Small and coarse: keeps meshing tests in the millisecond range.

### Community 2 - "Community 2"
Cohesion: 0.18
Nodes (8): export_stl(), LetterMesh, Path, Write the letter as `bubble_<name>.stl` and return the path., One finished letter, resting on z = 0., Filename-safe name for a character., slug(), test_slug()

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (16): ArgumentParser, CaptureFixture, Namespace, build_parser(), _configure_logging(), main(), params_from_args(), Command line entry point. (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (28): LogCaptureFixture, BubbleParams, Blank border around the glyph so inflation and rounding never clip., Geometry and sampling parameters for one batch of letters.      Distances are mi, build_alphabet(), build_letter(), Run the whole pipeline for one character., Build every character, skipping whitespace and glyphs the font cannot supply. (+20 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (30): Profile, All tunables in one immutable, validated object., Shape of the edge roll — how the surface climbs from 0 to full thickness., build_mesh(), _decimate(), _drop_degenerate_faces(), float64, NDArray (+22 more)

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (26): Mask, dilate(), erode(), Contour, Field, rasterize(), Signed distance in mm: positive inside the glyph, negative outside., Rasterize contours (in mm) to a boolean mask with a blank margin. (+18 more)

### Community 7 - "Community 7"
Cohesion: 0.28
Nodes (13): height_field(), Field, The inflation itself: signed distance in, half-thickness out., Half-thickness h(x, y) in mm from the signed distance field.      Outside the gl, float64, NDArray, One-dimensional signed distance ramp: outside, edge roll, deep interior., sd() (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (12): bubblegen, Development, Fonts, How it works, Install, Layout, Library use, License (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.22
Nodes (8): [0.1.0] - 2026-08-06, [0.2.0] - 2026-08-06, Added, Added, Changelog, Fixed, Fixed, Removed

### Community 12 - "Community 12"
Cohesion: 0.80
Nodes (4): download(), main(), pin_instance(), Path

## Knowledge Gaps
- **17 isolated node(s):** `bubblegen`, `Removed`, `Added`, `Fixed`, `Added` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BubbleParams` connect `Community 4` to `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.313) - this node is a cross-community bridge._
- **Why does `Font` connect `Community 0` to `Community 2`, `Community 4`?**
  _High betweenness centrality (0.206) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `BubbleParams` (e.g. with `LetterMesh` and `Raster`) actually correct?**
  _`BubbleParams` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Font` (e.g. with `EmptyGlyphError` and `FontError`) actually correct?**
  _`Font` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `build_letter()` (e.g. with `height_field()` and `build_mesh()`) actually correct?**
  _`build_letter()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `FlattenPen` (e.g. with `EmptyGlyphError` and `FontError`) actually correct?**
  _`FlattenPen` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `build_mesh()` (e.g. with `build_letter()` and `test_decimation_reduces_faces_and_keeps_it_closed()`) actually correct?**
  _`build_mesh()` has 6 INFERRED edges - model-reasoned connections that need verification._