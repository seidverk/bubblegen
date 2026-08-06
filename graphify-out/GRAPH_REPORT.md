# Graph Report - bubble-alphabet-is  (2026-08-06)

## Corpus Check
- 25 files · ~12,688 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 340 nodes · 716 edges · 13 communities (11 shown, 2 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 118 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `00bc340d`
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
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]

## God Nodes (most connected - your core abstractions)
1. `BubbleParams` - 79 edges
2. `Font` - 36 edges
3. `rasterize()` - 25 edges
4. `build_letter()` - 24 edges
5. `inflated()` - 19 edges
6. `build_mesh()` - 17 edges
7. `FlattenPen` - 15 edges
8. `square()` - 15 edges
9. `Raster` - 14 edges
10. `rect()` - 14 edges

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

## Communities (13 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (37): LogCaptureFixture, BubbleParams, All tunables in one immutable, validated object., Blank border around the glyph so inflation and rounding never clip., Geometry and sampling parameters for one batch of letters.      Distances are mi, build_letter(), Field, Round the silhouette as far as this particular glyph allows.      `--round` is a (+29 more)

### Community 1 - "Community 1"
Cohesion: 0.17
Nodes (16): elbow(), fat_elbow(), font(), font_path(), notched(), params(), float64, NDArray (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (33): Field, Signed distance in mm: positive inside the glyph, negative outside., signed_distance(), RectFactory, Axis-aligned rectangle contour in mm: a stroke of a given width., rect(), inflated(), float64 (+25 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (22): ArgumentParser, CaptureFixture, Namespace, build_parser(), _configure_logging(), main(), params_from_args(), Command line entry point. (+14 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (39): Any, BasePen, Exception, BubbleGenError, EmptyGlyphError, FontError, GlyphNotFoundError, Exception hierarchy: every expected failure is a `BubbleGenError`. (+31 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (32): Prepared, _base_inset(), build_mesh(), _decimate(), _drop_degenerate_faces(), float64, NDArray, Trimesh (+24 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (44): dilate(), enclosed_gaps(), erode(), Contour, Mask, rasterize(), Contours to a pixel mask, and the mask to a signed distance field., Round the sharp outer tips of the silhouette (A apex, W, Ж, Æ).      Opening onl (+36 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (12): bubblegen, Development, Fonts, How it works, Install, Layout, Library use, License (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (32): [0.1.0] - 2026-08-06, [0.2.0] - 2026-08-06, [0.3.0] - 2026-08-06, [0.4.0] - 2026-08-06, [0.5.0] - 2026-08-06, [0.6.0] - 2026-08-06, [0.7.0] - 2026-08-06, [0.8.0] - 2026-08-06 (+24 more)

### Community 12 - "Community 12"
Cohesion: 0.21
Nodes (17): _crest_line(), height_field(), _largest_piece(), _membrane(), Field, Mask, The inflation itself: silhouette in, thickness out.  The letter is treated as a, The glyph's centre line, minus the branches that run into concave corners. (+9 more)

### Community 13 - "Community 13"
Cohesion: 0.80
Nodes (4): download(), main(), pin_instance(), Path

## Knowledge Gaps
- **34 isolated node(s):** `bubblegen`, `Fixed`, `Changed`, `Fixed`, `Added` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BubbleParams` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 12`?**
  _High betweenness centrality (0.311) - this node is a cross-community bridge._
- **Why does `Font` connect `Community 4` to `Community 0`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `BubbleParams` (e.g. with `LetterMesh` and `Raster`) actually correct?**
  _`BubbleParams` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Font` (e.g. with `EmptyGlyphError` and `FontError`) actually correct?**
  _`Font` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `rasterize()` (e.g. with `build_letter()` and `inflated()`) actually correct?**
  _`rasterize()` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `build_letter()` (e.g. with `height_field()` and `build_mesh()`) actually correct?**
  _`build_letter()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `inflated()` (e.g. with `height_field()` and `rasterize()`) actually correct?**
  _`inflated()` has 3 INFERRED edges - model-reasoned connections that need verification._