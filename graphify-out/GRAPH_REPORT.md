# Graph Report - bubble-alphabet-is  (2026-08-07)

## Corpus Check
- 25 files · ~14,416 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 365 nodes · 783 edges · 18 communities (15 shown, 3 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 132 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8a6e4c04`
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

## God Nodes (most connected - your core abstractions)
1. `BubbleParams` - 84 edges
2. `Font` - 36 edges
3. `rasterize()` - 28 edges
4. `build_letter()` - 24 edges
5. `build_mesh()` - 21 edges
6. `inflated()` - 19 edges
7. `FlattenPen` - 15 edges
8. `square()` - 15 edges
9. `rect()` - 15 edges
10. `puffed_square()` - 15 edges

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

## Communities (18 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (37): LogCaptureFixture, BubbleParams, All tunables in one immutable, validated object., Blank border around the glyph so inflation and rounding never clip., Geometry and sampling parameters for one batch of letters.      Distances are mi, build_letter(), Field, Round the silhouette as far as this particular glyph allows.      `--round` is a (+29 more)

### Community 1 - "Community 1"
Cohesion: 0.16
Nodes (18): dumbbell(), elbow(), fat_elbow(), font(), font_path(), notched(), params(), float64 (+10 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (35): Field, Signed distance in mm: positive inside the glyph, negative outside., signed_distance(), RectFactory, Axis-aligned rectangle contour in mm: a stroke of a given width., rect(), inflated(), float64 (+27 more)

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (16): ArgumentParser, CaptureFixture, Namespace, build_parser(), _configure_logging(), main(), params_from_args(), Command line entry point. (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.19
Nodes (6): BasePen, FlattenPen, Contour, Font units to mm, such that a capital letter is `size_mm` tall., Flattened contours of `char`, in mm., Collects glyph contours as flat polylines, sampling beziers into lines.

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (45): Prepared, _base_inset(), build_mesh(), _decimate(), _drop_degenerate_faces(), float64, NDArray, Trimesh (+37 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (44): dilate(), enclosed_gaps(), erode(), Contour, Mask, rasterize(), Contours to a pixel mask, and the mask to a signed distance field., Round the sharp outer tips of the silhouette (A apex, W, Ж, Æ).      Opening onl (+36 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (12): build_alphabet(), export_stl(), LetterMesh, Path, End-to-end: character in, printable mesh out., Build every character, skipping whitespace and glyphs the font cannot supply., Write the letter as `bubble_<name>.stl` and return the path., One finished letter, resting on z = 0. (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (12): bubblegen, Development, Fonts, How it works, Install, Layout, Library use, License (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (34): [0.10.0] - 2026-08-07, [0.1.0] - 2026-08-06, [0.2.0] - 2026-08-06, [0.3.0] - 2026-08-06, [0.4.0] - 2026-08-06, [0.5.0] - 2026-08-06, [0.6.0] - 2026-08-06, [0.7.0] - 2026-08-06 (+26 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (23): _cone_floor(), _crest_line(), _half_width(), height_field(), _largest_piece(), _membrane(), Field, Mask (+15 more)

### Community 13 - "Community 13"
Cohesion: 0.80
Nodes (4): download(), main(), pin_instance(), Path

### Community 14 - "Community 14"
Cohesion: 0.20
Nodes (10): Font, Font units a capital letter occupies, so all letters share one scale.          O, A loaded font, queried per character., test_bezier_steps_control_point_density(), test_cap_letter_is_scaled_to_requested_size(), test_counter_produces_two_contours(), test_missing_glyph(), test_reference_height_is_cap_height() (+2 more)

### Community 15 - "Community 15"
Cohesion: 0.24
Nodes (10): Exception, BubbleGenError, EmptyGlyphError, FontError, GlyphNotFoundError, Exception hierarchy: every expected failure is a `BubbleGenError`., Font file missing, unreadable, or not a font., The font has no glyph for the requested character. (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.29
Nodes (5): Any, Path, Path, test_load_reports_missing_file(), TTFont

## Knowledge Gaps
- **35 isolated node(s):** `bubblegen`, `Fixed`, `Fixed`, `Changed`, `Fixed` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BubbleParams` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 7`, `Community 12`?**
  _High betweenness centrality (0.311) - this node is a cross-community bridge._
- **Why does `Font` connect `Community 14` to `Community 0`, `Community 4`, `Community 7`, `Community 15`, `Community 16`, `Community 17`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Why does `FlattenPen` connect `Community 4` to `Community 16`, `Community 17`, `Community 15`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `BubbleParams` (e.g. with `LetterMesh` and `Raster`) actually correct?**
  _`BubbleParams` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Font` (e.g. with `EmptyGlyphError` and `FontError`) actually correct?**
  _`Font` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `rasterize()` (e.g. with `build_letter()` and `inflated()`) actually correct?**
  _`rasterize()` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `build_letter()` (e.g. with `height_field()` and `build_mesh()`) actually correct?**
  _`build_letter()` has 16 INFERRED edges - model-reasoned connections that need verification._