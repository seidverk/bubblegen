# bubblegen

Parametric inflated "bubble" letters from any TTF/OTF font, exported as watertight STL.

Every letter is puffed on top and flat on the bottom: it prints face-up without supports
and hangs flush against a wall.

Everything is procedural. No manual sculpting, no per-letter fixes: point it at a font, give
it a string, get a printable mesh per character.

```
bubblegen --font fonts/Nunito-Black.ttf --chars "ABC" --size 60 --puff 8
```

## How it works

```
glyph outline (fontTools)
  -> flattened contours          bezier sampling
  -> raster mask                 even-odd winding, so counters stay open
  -> silhouette rounding         closing + opening, backed off to keep counters
  -> membrane solve              laplace(u) = -1, clamped to the outline
  -> thickness h = sqrt(2u)      capped by --puff
  -> 3D scalar field             solid between the plate and h, filleted at the base
  -> marching cubes              scikit-image
  -> Taubin smoothing            volume-preserving, unlike Laplacian
  -> decimation + watertight STL
```

The shape is not a profile drawn by hand, it is a balloon: a membrane clamped to the letter's
outline and pushed up by uniform pressure. That is what `laplace(u) = -1` with `u = 0` on the
outline says, and `sqrt(2u)` is the thickness.

For a straight stroke it works out to exactly a semicircular cross-section of that stroke's own
half-width, so every stroke inflates to its own size. Because the solution is smooth
everywhere, there is no ridge down the centre line, no crease radiating from a corner, and
junctions bulge rather than dent: a wider patch of membrane deflects further. Anything built
from the distance to the outline instead gets all three of those artefacts.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```fish
git clone https://github.com/ingvarch/bubble-alphabet-is
cd bubble-alphabet-is
uv sync
make fonts   # four heavy display fonts into fonts/
```

Run without installing anything globally:

```fish
uv run bubblegen --font fonts/Nunito-Black.ttf --chars "ABC"
```

Install as a standalone tool:

```fish
uv tool install .
bubblegen --font fonts/Nunito-Black.ttf --chars "ABC"
```

## Fonts

Bubble letters need heavy fonts: thickness is capped at the stroke half-width, so a Regular
weight at 60 mm gives you a 4 mm bubble no matter what `--puff` says. Every cap and every
reduced rounding radius is logged, so you always know when the font is the limit.

`make fonts` fetches four SIL Open Font License faces into `fonts/` (gitignored):

| File | Character coverage | Look |
| --- | --- | --- |
| `Nunito-Black.ttf` | Latin, Latin Ext, Cyrillic | rounded, the safest default |
| `TitanOne-Regular.ttf` | Latin, Latin Ext | very fat, cartoon |
| `LilitaOne-Regular.ttf` | Latin, Latin Ext | tall, condensed |
| `Fredoka-Bold.ttf` | Latin, Latin Ext | soft, playful |

Any other TTF/OTF works. Variable fonts are read at their default location, which is usually
a light weight — pin a heavy instance first (see `scripts/fetch_fonts.py`).

## Usage

```fish
# Icelandic alphabet, 60 mm tall
uv run bubblegen --font fonts/Nunito-Black.ttf --chars "AÁBDÐEÉFGHIÍJKLMNOÓPRSTUÚVXYÝÞÆÖ"

# a name for the wall, fat and balloon-like
uv run bubblegen --font fonts/TitanOne-Regular.ttf --chars "IGOR" --size 80 --puff 14

# fast preview, then final quality
uv run bubblegen --font fonts/Nunito-Black.ttf --chars "A" --res 3 --zsteps 32 --smooth 0
uv run bubblegen --font fonts/Nunito-Black.ttf --chars "A" --res 8 --zsteps 96 --faces 80000
```

Output lands in `--out` (default `out/`) as `bubble_A.stl`. Characters outside `[A-Za-z0-9]`
are named by code point: `Þ` becomes `bubble_U00DE.stl`.

### Options

| Flag | Default | Meaning |
| --- | --- | --- |
| `--font` | required | Path to a `.ttf` or `.otf` |
| `--chars` | required | Characters to generate, e.g. `"ABCÞÐÆ"` |
| `--out` | `out` | Output directory |
| `--size` | `60` | Cap height in mm; shared by every letter so an alphabet stays consistent |
| `--puff` | `7` | Thickness at the centre of a stroke in mm, dome included. An upper bound: capped per letter at the stroke half-width |
| `--round` | `0.45*puff` | Silhouette rounding radius, an upper bound. Backed off per letter so counters and thin strokes survive |
| `--base-round` | `0.25*puff` | Fillet radius under the letter. The contact patch is the outline pulled in by this much; the wall then rolls out to the full silhouette |
| `--res` | `5` | Raster pixels per mm. Cost grows quadratically |
| `--zsteps` | `64` | Vertical samples for marching cubes |
| `--smooth` | `12` | Taubin smoothing passes |
| `--faces` | `40000` | Triangle target after decimation. `0` keeps the dense mesh |
| `--bezier-steps` | `24` | Line segments per bezier when flattening the outline |
| `-v` / `-q` | | More or less logging |

### Tuning notes

- "strokes are 8.4 mm wide, so --puff 8.0 mm is capped at 3.7 mm": the font is too light for
  the thickness you asked for. Use a heavier font, raise `--size`, or accept the thinner
  bubble. A peak taller than half the stroke width would print as a tube.
- "--round 5.4 mm would deform the glyph, using 3.8 mm": the radius would have filled a
  counter or eaten a stroke, so it was reduced for that letter. Set `--round` explicitly to
  silence it.
- Letters look under-inflated: raise `--puff`, and use a font with fatter strokes so the
  ceiling does not bite. Thickness is bounded by the stroke, not by the flag.
- Letters rock on the plate or the fillet is too subtle: tune `--base-round`. `0` gives the
  old square wall, half the puff gives an almost fully rounded underside.
- Sharp tips still sharp (`A`, `W`, `Ж`): raise `--round`.
- Facets or steps visible on the surface: raise `--res` and `--zsteps` before raising
  `--smooth`; smoothing cannot add detail that was never sampled.
- `--faces` is a target, not a cap. Each candidate is measured against the surface it should
  follow and rejected if decimation adds more than 0.15 mm of error, so letters with straight
  strokes keep more triangles than you asked for. Lower `--res` if you need smaller files.

## Printing

The bottom is flat at `z = 0`, so letters print face-up with no supports and no brim fiddling.
The outline curves down into it, so the contact patch is smaller than the silhouette by
`--base-round`; that is the point, but it also means a slightly smaller first layer. Meshes are
watertight and in millimetres, so slicers need no scaling.

For hanging: the flat back takes double-sided foam tape or mounting strips directly. Letters
above roughly 80 mm are worth printing hollow (a few perimeters, low infill) to keep the
weight off the tape.

## Library use

```python
from pathlib import Path

from bubblegen import BubbleParams, Font, build_alphabet, export_stl

font = Font.load("fonts/Nunito-Black.ttf")
params = BubbleParams(size_mm=40, puff_mm=5, base_round_mm=1.5)

for letter in build_alphabet(font, "IGOR", params):
    print(letter.char, letter.extents, letter.is_watertight)
    export_stl(letter, Path("out"))
```

`BubbleParams` is frozen and validated on construction, so bad values fail fast rather than
producing a broken mesh. `build_letter` raises `BubbleGenError` subclasses
(`GlyphNotFoundError`, `EmptyGlyphError`); `build_alphabet` logs and skips them.

## Layout

```
src/bubblegen/
  config.py     BubbleParams, Profile: every tunable, validated
  fonts.py      outline extraction, bezier flattening, mm scaling
  raster.py     contours -> mask -> signed distance field
  inflate.py    the membrane solve: silhouette -> thickness
  mesh.py       marching cubes, cleanup, smoothing, decimation
  pipeline.py   character -> LetterMesh -> STL
  cli.py        argument parsing and logging
scripts/
  fetch_fonts.py  downloads and pins the fonts used by `make fonts`
tests/            one module per source module
```

## Development

```fish
make sync     # create .venv and install dev dependencies
make test     # pytest
make lint     # ruff check + ruff format --check + mypy
make fix      # ruff format + ruff check --fix
make check    # lint + test, run this before committing
make hooks    # install pre-commit hooks
```

Tests use DejaVu Sans, which ships with matplotlib, so no font assets are needed.

## License

MIT. See [LICENSE](LICENSE). Fonts downloaded by `make fonts` are under the SIL Open Font
License and are not part of this repository.
