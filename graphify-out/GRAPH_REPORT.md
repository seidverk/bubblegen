# Graph Report - bubble-alphabet-is  (2026-08-06)

## Corpus Check
- 25 files · ~9,638 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 288 nodes · 593 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 98 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9efaae6f`
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
1. `BubbleParams` - 66 edges
2. `Font` - 36 edges
3. `build_letter()` - 23 edges
4. `rasterize()` - 20 edges
5. `build_mesh()` - 17 edges
6. `FlattenPen` - 15 edges
7. `square()` - 15 edges
8. `puffed_square()` - 14 edges
9. `Raster` - 13 edges
10. `inflated()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_font_and_chars_are_required()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/bubblegen/cli.py
- `test_base_radius_defaults_to_a_fraction_of_puff()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_explicit_base_round_wins()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_invalid_values_rejected()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_margin_covers_puff_and_rounding()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py

## Import Cycles
- None detected.

## Communities (14 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (34): Any, BasePen, Exception, BubbleGenError, EmptyGlyphError, FontError, GlyphNotFoundError, Exception hierarchy: every expected failure is a `BubbleGenError`. (+26 more)

### Community 1 - "Community 1"
Cohesion: 0.17
Nodes (11): All tunables in one immutable, validated object., elbow(), font(), font_path(), params(), float64, NDArray, Path (+3 more)

### Community 2 - "Community 2"
Cohesion: 0.18
Nodes (8): export_stl(), LetterMesh, Path, Write the letter as `bubble_<name>.stl` and return the path., One finished letter, resting on z = 0., Filename-safe name for a character., slug(), test_slug()

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (16): ArgumentParser, CaptureFixture, Namespace, build_parser(), _configure_logging(), main(), params_from_args(), Command line entry point. (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (36): LogCaptureFixture, BubbleParams, Geometry and sampling parameters for one batch of letters.      Distances are mi, Blank border around the glyph so inflation and rounding never clip., build_alphabet(), build_letter(), Field, Build every character, skipping whitespace and glyphs the font cannot supply. (+28 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (32): Prepared, _base_inset(), build_mesh(), _decimate(), _drop_degenerate_faces(), float64, NDArray, Trimesh (+24 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (35): dilate(), enclosed_gaps(), erode(), Contour, Field, Mask, rasterize(), Contours to a pixel mask, and the mask to a signed distance field. (+27 more)

### Community 7 - "Community 7"
Cohesion: 0.18
Nodes (20): bool_, RectFactory, Axis-aligned rectangle contour in mm: a stroke of a given width., rect(), inflated(), float64, NDArray, RectFactory (+12 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (12): bubblegen, Development, Fonts, How it works, Install, Layout, Library use, License (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (19): [0.1.0] - 2026-08-06, [0.2.0] - 2026-08-06, [0.3.0] - 2026-08-06, [0.4.0] - 2026-08-06, [0.5.0] - 2026-08-06, Added, Added, Added (+11 more)

### Community 12 - "Community 12"
Cohesion: 0.31
Nodes (9): _deflection(), height_field(), Field, Mask, The inflation itself: silhouette in, thickness out.  The letter is treated as a, Thickness h(x, y) in mm, from the membrane deflection over the silhouette., Membrane deflection under unit pressure, in mm squared., Five-point Laplacian on the masked pixels, zero on everything outside. (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.80
Nodes (4): download(), main(), pin_instance(), Path

## Knowledge Gaps
- **25 isolated node(s):** `bubblegen`, `Changed`, `Removed`, `Fixed`, `Changed` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BubbleParams` connect `Community 4` to `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 7`, `Community 12`?**
  _High betweenness centrality (0.299) - this node is a cross-community bridge._
- **Why does `Font` connect `Community 0` to `Community 2`, `Community 4`, `Community 7`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `BubbleParams` (e.g. with `LetterMesh` and `Raster`) actually correct?**
  _`BubbleParams` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Font` (e.g. with `EmptyGlyphError` and `FontError`) actually correct?**
  _`Font` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `build_letter()` (e.g. with `height_field()` and `build_mesh()`) actually correct?**
  _`build_letter()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `rasterize()` (e.g. with `build_letter()` and `inflated()`) actually correct?**
  _`rasterize()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `build_mesh()` (e.g. with `build_letter()` and `test_decimation_reduces_faces_and_keeps_it_closed()`) actually correct?**
  _`build_mesh()` has 7 INFERRED edges - model-reasoned connections that need verification._