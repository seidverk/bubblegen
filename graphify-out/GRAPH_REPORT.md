# Graph Report - bubble-alphabet-is  (2026-08-06)

## Corpus Check
- 4 files · ~2,052 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 36 nodes · 52 edges · 12 communities (4 shown, 8 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a6dab77b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]

## God Nodes (most connected - your core abstractions)
1. `FlattenPen` - 12 edges
2. `main()` - 11 edges
3. `glyph_contours()` - 5 edges
4. `soften()` - 5 edges
5. `font_reference_height()` - 3 edges
6. `rasterize()` - 3 edges
7. `signed_distance()` - 3 edges
8. `height_field()` - 3 edges
9. `find_hole_center()` - 3 edges
10. `cut_hole()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `glyph_contours()` --calls--> `FlattenPen`  [EXTRACTED]
  bubble_letters.py → bubble_letters.py  _Bridges community 0 → community 4_
- `main()` --calls--> `glyph_contours()`  [EXTRACTED]
  bubble_letters.py → bubble_letters.py  _Bridges community 4 → community 2_
- `main()` --calls--> `font_reference_height()`  [EXTRACTED]
  bubble_letters.py → bubble_letters.py  _Bridges community 7 → community 2_
- `main()` --calls--> `rasterize()`  [EXTRACTED]
  bubble_letters.py → bubble_letters.py  _Bridges community 9 → community 2_
- `main()` --calls--> `soften()`  [EXTRACTED]
  bubble_letters.py → bubble_letters.py  _Bridges community 1 → community 2_

## Import Cycles
- None detected.

## Communities (12 total, 8 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.33
Nodes (3): BasePen, FlattenPen, Collects glyph contours as flat polylines (beziers sampled into lines).

### Community 1 - "Community 1"
Cohesion: 0.60
Nodes (4): _dilate(), _erode(), Round the silhouette itself — this is what makes letters read as 'bubble'., soften()

### Community 2 - "Community 2"
Cohesion: 0.50
Nodes (4): cut_hole(), main(), Drill the keyring hole as a real boolean (needs `pip install manifold3d`)., safe_name()

## Knowledge Gaps
- **1 isolated node(s):** `graphify`
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FlattenPen` connect `Community 0` to `Community 1`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.422) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 2` to `Community 1`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `glyph_contours()` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **What connects `Collects glyph contours as flat polylines (beziers sampled into lines).`, `Return list of contours (Nx2 arrays) in font units for one character.`, `Units that a capital letter occupies — used so all letters share one scale.` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._