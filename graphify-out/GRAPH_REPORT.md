# Graph Report - bubblegen  (2026-08-07)

## Corpus Check
- 25 files · ~49,334 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 376 nodes · 731 edges · 31 communities (12 shown, 19 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 138 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8a523a26`
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
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]

## God Nodes (most connected - your core abstractions)
1. `BubbleParams` - 71 edges
2. `Font` - 30 edges
3. `rasterize()` - 26 edges
4. `build_letter()` - 25 edges
5. `build_mesh()` - 22 edges
6. `Raster` - 20 edges
7. `inflated()` - 20 edges
8. `puffed_square()` - 16 edges
9. `FlattenPen` - 15 edges
10. `rect()` - 15 edges

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

## Communities (31 total, 19 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (48): LogCaptureFixture, build_alphabet(), build_letter(), export_stl(), LetterMesh, Field, Path, End-to-end: character in, printable mesh out. (+40 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (37): dilate(), enclosed_gaps(), erode(), rasterize(), Contours to a pixel mask, and the mask to a signed distance field., Round the sharp outer tips of the silhouette (A apex, W, Ж, Æ).      Opening onl, Count background regions fully enclosed by the glyph: its counters., Round the outline by as much as the glyph tolerates.      Every piece of the gly (+29 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (35): inflated(), float64, NDArray, RectFactory, The ring of an O is narrower at top and bottom. The tube must not be pinched, An acute or a dot is a small piece of its own and has to stay thin. It must not, The medial axis runs into every concave corner, but the letter is not at its, No cap means a full round tube everywhere: the height follows the local stroke (+27 more)

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (12): ArgumentParser, CaptureFixture, Namespace, build_parser(), _configure_logging(), main(), params_from_args(), Command line entry point. (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (13): BubbleParams, All tunables in one immutable, validated object., Blank border around the glyph so inflation and rounding never clip., Geometry and sampling parameters for one batch of letters.      Distances are mi, test_base_radius_defaults_to_a_fraction_of_puff(), test_defaults_are_full_inflation(), test_explicit_base_round_wins(), test_invalid_values_rejected() (+5 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (47): Prepared, _base_inset(), build_mesh(), _decimate(), _drop_degenerate_faces(), float64, NDArray, Trimesh (+39 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (13): dumbbell(), elbow(), fat_elbow(), notched(), params(), Shared fixtures. DejaVu Sans ships with matplotlib, so tests need no font assets, A fat C: 16 mm walls around an 8 mm aperture, like the apertures of S and G., An L with 30 mm arms: wide enough for its concave corner to matter. (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (12): bubblegen, Development, Fonts, How it works, Install, Layout, Library use, License (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (36): [0.10.0] - 2026-08-07, [0.11.0] - 2026-08-07, [0.1.0] - 2026-08-06, [0.2.0] - 2026-08-06, [0.3.0] - 2026-08-06, [0.4.0] - 2026-08-06, [0.5.0] - 2026-08-06, [0.6.0] - 2026-08-06 (+28 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (23): _cone_floor(), _crest_line(), _half_width(), height_field(), _largest_piece(), _membrane(), Field, Mask (+15 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (20): Any, BasePen, Exception, TTFont, download(), main(), pin_instance(), BubbleGenError (+12 more)

## Knowledge Gaps
- **36 isolated node(s):** `bubblegen`, `Changed`, `Fixed`, `Fixed`, `Changed` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BubbleParams` connect `Community 4` to `Community 0`, `Community 2`, `Community 3`, `Community 5`, `Community 12`?**
  _High betweenness centrality (0.232) - this node is a cross-community bridge._
- **Why does `Font` connect `Community 0` to `Community 16`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `Raster` connect `Community 5` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 12`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `BubbleParams` (e.g. with `LetterMesh` and `test_base_radius_defaults_to_a_fraction_of_puff()`) actually correct?**
  _`BubbleParams` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Font` (e.g. with `LetterMesh` and `EmptyGlyphError`) actually correct?**
  _`Font` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `rasterize()` (e.g. with `build_letter()` and `inflated()`) actually correct?**
  _`rasterize()` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `build_letter()` (e.g. with `height_field()` and `build_mesh()`) actually correct?**
  _`build_letter()` has 17 INFERRED edges - model-reasoned connections that need verification._