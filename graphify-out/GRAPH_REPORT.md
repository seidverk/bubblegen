# Graph Report - bubblegen  (2026-08-13)

## Corpus Check
- 32 files · ~57,283 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 555 nodes · 1145 edges · 28 communities (14 shown, 14 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 198 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5de90b04`
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
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]

## God Nodes (most connected - your core abstractions)
1. `BubbleParams` - 78 edges
2. `Font` - 39 edges
3. `StandParams` - 34 edges
4. `rasterize()` - 30 edges
5. `build_letter()` - 28 edges
6. `build_mesh()` - 23 edges
7. `inflated()` - 21 edges
8. `apply_tweaks()` - 20 edges
9. `rect()` - 18 edges
10. `height_field()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `test_base_radius_defaults_to_a_fraction_of_puff()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_defaults_are_the_reference_balloon()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_explicit_base_round_wins()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_invalid_values_rejected()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py
- `test_margin_covers_inflation_without_puff()` --calls--> `BubbleParams`  [INFERRED]
  tests/test_config.py → src/bubblegen/config.py

## Import Cycles
- None detected.

## Communities (28 total, 14 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (60): LogCaptureFixture, BubbleParams, All tunables in one immutable, validated object., Blank border around the glyph so inflation and rounding never clip., Geometry and sampling parameters for one batch of letters.      Distances are mi, Parametric inflated 3D bubble letters from any TTF/OTF font., build_alphabet(), build_letter() (+52 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (38): SquareFactory, Axis-aligned square contour in mm, counter-clockwise., square(), dilate(), enclosed_gaps(), erode(), rasterize(), Contours to a pixel mask, and the mask to a signed distance field. (+30 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (43): RectFactory, Axis-aligned rectangle contour in mm: a stroke of a given width., rect(), inflated(), float64, NDArray, RectFactory, The ring of an O is narrower at top and bottom. The tube must not be pinched (+35 more)

### Community 3 - "Community 3"
Cohesion: 0.13
Nodes (16): build_parser(), _configure_logging(), main(), params_from_args(), ArgumentParser, Namespace, Command line entry point., CaptureFixture (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (18): dumbbell(), elbow(), fat_elbow(), font(), font_path(), notched(), params(), float64 (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (51): Prepared, _base_inset(), build_mesh(), _decimate(), _drop_degenerate_faces(), float64, NDArray, Trimesh (+43 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (70): Op, The per-letter tweaks file is missing, malformed, or invalid., TweaksError, apply_tweaks(), _band_weight(), _BandOp, _cut(), DeepenOp (+62 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (59): build_stand(), _cell(), cell_centres(), build_parser(), _configure_logging(), main(), params_from_args(), ArgumentParser (+51 more)

### Community 8 - "Community 8"
Cohesion: 0.13
Nodes (14): bubblegen, Development, Fonts, How it works, Install, Layout, Library use, License (+6 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (38): [0.10.0] - 2026-08-07, [0.11.0] - 2026-08-07, [0.1.0] - 2026-08-06, [0.2.0] - 2026-08-06, [0.3.0] - 2026-08-06, [0.4.0] - 2026-08-06, [0.5.0] - 2026-08-06, [0.6.0] - 2026-08-06 (+30 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (23): _cone_floor(), _crest_line(), _half_width(), height_field(), _largest_piece(), _membrane(), Field, Mask (+15 more)

### Community 16 - "Community 16"
Cohesion: 0.06
Nodes (21): BasePen, Exception, BubbleGenError, EmptyGlyphError, FontError, GlyphNotFoundError, Exception hierarchy: every expected failure is a `BubbleGenError`., Font file missing, unreadable, or not a font. (+13 more)

### Community 21 - "Community 21"
Cohesion: 0.31
Nodes (6): CaptureFixture, Path, test_help_exits_cleanly(), test_impossible_geometry_fails_without_a_traceback(), test_run_creates_missing_directories(), test_run_writes_an_stl()

### Community 22 - "Community 22"
Cohesion: 0.40
Nodes (4): Geometry, Implementation, Parameters, Resin painting stand

## Knowledge Gaps
- **43 isolated node(s):** `bubblegen`, `Added`, `Fixed`, `Changed`, `Fixed` (+38 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Font` connect `Community 0` to `Community 1`, `Community 3`, `Community 4`, `Community 6`, `Community 16`?**
  _High betweenness centrality (0.177) - this node is a cross-community bridge._
- **Why does `BubbleParams` connect `Community 0` to `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 12`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `BubbleParams` (e.g. with `LetterMesh` and `test_base_radius_defaults_to_a_fraction_of_puff()`) actually correct?**
  _`BubbleParams` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Font` (e.g. with `LetterMesh` and `EmptyGlyphError`) actually correct?**
  _`Font` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `rasterize()` (e.g. with `build_letter()` and `inflated()`) actually correct?**
  _`rasterize()` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `build_letter()` (e.g. with `height_field()` and `build_mesh()`) actually correct?**
  _`build_letter()` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `bubblegen`, `Parametric inflated 3D bubble letters from any TTF/OTF font.`, `Enables `python -m bubblegen`.` to the rest of the system?**
  _182 weakly-connected nodes found - possible documentation gaps or missing edges._