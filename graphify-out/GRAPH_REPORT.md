# Graph Report - bubble-alphabet-is  (2026-08-06)

## Corpus Check
- 25 files · ~9,573 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 283 nodes · 600 edges · 11 communities (9 shown, 2 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 109 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0b406e00`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
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
1. `BubbleParams` - 73 edges
2. `Font` - 35 edges
3. `build_letter()` - 23 edges
4. `square()` - 23 edges
5. `rasterize()` - 21 edges
6. `build_mesh()` - 17 edges
7. `FlattenPen` - 15 edges
8. `inflated()` - 14 edges
9. `puffed_square()` - 14 edges
10. `Raster` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_font_and_chars_are_required()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/bubblegen/cli.py
- `test_base_radius_defaults_to_a_fraction_of_puff()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_explicit_base_round_wins()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_explicit_roll_and_round_win()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_invalid_values_rejected()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py

## Import Cycles
- None detected.

## Communities (11 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (34): BasePen, Exception, BubbleGenError, EmptyGlyphError, FontError, GlyphNotFoundError, Exception hierarchy: every expected failure is a `BubbleGenError`., Font file missing, unreadable, or not a font. (+26 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (15): Any, download(), main(), pin_instance(), Path, Path, font(), font_path() (+7 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (22): ArgumentParser, CaptureFixture, Namespace, build_parser(), _configure_logging(), main(), params_from_args(), Command line entry point. (+14 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (38): LogCaptureFixture, BubbleParams, Blank border around the glyph so inflation and rounding never clip., Geometry and sampling parameters for one batch of letters.      Distances are mi, build_letter(), Field, Round the silhouette as far as this particular glyph allows.      `--round` is a, Say so when the stroke, not `--puff`, is what sets the thickness. (+30 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (32): Prepared, _base_inset(), build_mesh(), _decimate(), _drop_degenerate_faces(), float64, NDArray, Trimesh (+24 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (40): Mask, dilate(), enclosed_gaps(), erode(), local_thickness(), Contour, Field, rasterize() (+32 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (23): Profile, All tunables in one immutable, validated object., Shape of the edge roll — how the surface climbs from 0 to full thickness., height_field(), Field, The inflation itself: signed distance in, thickness out., Thickness h(x, y) in mm from the signed distance field.      Each stroke is infl, Local stroke half-width, smoothed just enough to leave no visible steps.      Th (+15 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (12): bubblegen, Development, Fonts, How it works, Install, Layout, Library use, License (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (15): [0.1.0] - 2026-08-06, [0.2.0] - 2026-08-06, [0.3.0] - 2026-08-06, [0.4.0] - 2026-08-06, Added, Added, Added, Changed (+7 more)

## Knowledge Gaps
- **22 isolated node(s):** `bubblegen`, `Changed`, `Added`, `Removed`, `Fixed` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BubbleParams` connect `Community 4` to `Community 0`, `Community 1`, `Community 3`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.344) - this node is a cross-community bridge._
- **Why does `Font` connect `Community 0` to `Community 1`, `Community 4`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Why does `FlattenPen` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `BubbleParams` (e.g. with `LetterMesh` and `Raster`) actually correct?**
  _`BubbleParams` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Font` (e.g. with `EmptyGlyphError` and `FontError`) actually correct?**
  _`Font` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `build_letter()` (e.g. with `height_field()` and `build_mesh()`) actually correct?**
  _`build_letter()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `square()` (e.g. with `test_each_stroke_inflates_to_its_own_width()` and `test_explicit_roll_saturates_early()`) actually correct?**
  _`square()` has 20 INFERRED edges - model-reasoned connections that need verification._