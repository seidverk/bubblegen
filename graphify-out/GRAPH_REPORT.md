# Graph Report - bubblegen  (2026-08-07)

## Corpus Check
- 25 files · ~50,020 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 383 nodes · 772 edges · 24 communities (10 shown, 14 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 149 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f306795b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]

## God Nodes (most connected - your core abstractions)
1. `BubbleParams` - 75 edges
2. `Font` - 30 edges
3. `rasterize()` - 29 edges
4. `build_letter()` - 25 edges
5. `build_mesh()` - 22 edges
6. `inflated()` - 20 edges
7. `rect()` - 17 edges
8. `height_field()` - 16 edges
9. `puffed_square()` - 16 edges
10. `FlattenPen` - 15 edges

## Surprising Connections (you probably didn't know these)
- `test_font_and_chars_are_required()` --calls--> `build_parser()`  [INFERRED]
  tests/test_cli.py → src/bubblegen/cli.py
- `test_base_radius_defaults_to_a_fraction_of_puff()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_defaults_are_full_inflation()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_explicit_base_round_wins()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_invalid_values_rejected()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py

## Import Cycles
- None detected.

## Communities (24 total, 14 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (59): LogCaptureFixture, BubbleParams, All tunables in one immutable, validated object., Blank border around the glyph so inflation and rounding never clip., Geometry and sampling parameters for one batch of letters.      Distances are mi, build_alphabet(), build_letter(), export_stl() (+51 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (38): SquareFactory, Axis-aligned square contour in mm, counter-clockwise., square(), dilate(), enclosed_gaps(), erode(), rasterize(), Contours to a pixel mask, and the mask to a signed distance field. (+30 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (43): height_field(), Thickness h(x, y) and the geometric half-width map, both in mm.      `puff` is h, RectFactory, Axis-aligned rectangle contour in mm: a stroke of a given width., rect(), inflated(), float64, NDArray (+35 more)

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (12): ArgumentParser, CaptureFixture, Namespace, build_parser(), _configure_logging(), main(), params_from_args(), Command line entry point. (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (18): dumbbell(), elbow(), fat_elbow(), font(), font_path(), notched(), params(), float64 (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (47): Prepared, _base_inset(), build_mesh(), _decimate(), _drop_degenerate_faces(), float64, NDArray, Trimesh (+39 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (12): bubblegen, Development, Fonts, How it works, Install, Layout, Library use, License (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (38): [0.10.0] - 2026-08-07, [0.11.0] - 2026-08-07, [0.1.0] - 2026-08-06, [0.2.0] - 2026-08-06, [0.3.0] - 2026-08-06, [0.4.0] - 2026-08-06, [0.5.0] - 2026-08-06, [0.6.0] - 2026-08-06 (+30 more)

### Community 12 - "Community 12"
Cohesion: 0.18
Nodes (21): _cone_floor(), _crest_line(), _half_width(), _largest_piece(), _membrane(), Field, Mask, The inflation itself: silhouette in, thickness out.  The letter is treated as a (+13 more)

### Community 16 - "Community 16"
Cohesion: 0.06
Nodes (21): Any, BasePen, Exception, TTFont, download(), main(), pin_instance(), BubbleGenError (+13 more)

## Knowledge Gaps
- **38 isolated node(s):** `bubblegen`, `Added`, `Fixed`, `Changed`, `Fixed` (+33 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BubbleParams` connect `Community 0` to `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 12`?**
  _High betweenness centrality (0.244) - this node is a cross-community bridge._
- **Why does `Font` connect `Community 0` to `Community 16`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `rasterize()` connect `Community 1` to `Community 0`, `Community 2`, `Community 5`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `BubbleParams` (e.g. with `LetterMesh` and `test_base_radius_defaults_to_a_fraction_of_puff()`) actually correct?**
  _`BubbleParams` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Font` (e.g. with `LetterMesh` and `EmptyGlyphError`) actually correct?**
  _`Font` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `rasterize()` (e.g. with `build_letter()` and `inflated()`) actually correct?**
  _`rasterize()` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `build_letter()` (e.g. with `height_field()` and `build_mesh()`) actually correct?**
  _`build_letter()` has 17 INFERRED edges - model-reasoned connections that need verification._