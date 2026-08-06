# bubblegen

Parametric inflated "bubble" letters from any TTF/OTF font, exported as watertight STL.

Everything is procedural. No manual sculpting, no per-letter fixes: point it at a font, give it
a string, get a printable mesh per character.

```
bubblegen --font DejaVuSans.ttf --chars "ABC" --size 60 --puff 8 --flat-back
```

## How it works

```
glyph outline (fontTools)
  -> flattened contours          bezier sampling
  -> raster mask                 even-odd winding, so counters stay open
  -> silhouette rounding         morphological closing + opening
  -> signed distance field (mm)  scipy EDT
  -> height profile h(d)         the inflation
  -> 3D scalar field  f = h(x,y) - |z|
  -> marching cubes              scikit-image
  -> Taubin smoothing            volume-preserving, unlike Laplacian
  -> decimation + watertight STL
```

The signed distance field is what makes this work: thickness is a function of distance to the
letter's edge, so every stroke inflates evenly and holes in the glyph inflate inward.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```fish
git clone https://github.com/ingvarch/bubble-alphabet-is
cd bubble-alphabet-is
uv sync
```

Run without installing anything globally:

```fish
uv run bubblegen --font /path/to/font.ttf --chars "ABC"
```

Install as a standalone tool:

```fish
uv tool install .
bubblegen --font /path/to/font.ttf --chars "ABC"
```

## Usage

```fish
# Icelandic alphabet, 60 mm tall, printable without supports
uv run bubblegen --font Inter.ttf --chars "AÁBDÐEÉFGHIÍJKLMNOÓPRSTUÚVXYÝÞÆÖ" --flat-back

# keyring charms: smaller, thinner, with a 4 mm hole
uv run bubblegen --font Inter.ttf --chars "IGOR" --size 35 --puff 4 --hole 4

# fat and balloon-like
uv run bubblegen --font Inter.ttf --chars "OK" --puff 10 --dome 0.35 --profile smooth

# fast preview, then final quality
uv run bubblegen --font Inter.ttf --chars "A" --res 3 --zsteps 32 --smooth 0
uv run bubblegen --font Inter.ttf --chars "A" --res 8 --zsteps 96 --faces 80000
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
| `--puff` | `7` | Max half-thickness in mm. Total thickness is `2*puff`, or `puff` with `--flat-back` |
| `--roll` | `puff` | Distance over which the edge rounds up to full thickness. Smaller means a sharper shoulder |
| `--round` | `0.45*puff` | Silhouette rounding radius. This is what turns sharp glyph corners into bubble corners |
| `--dome` | `0.15` | Extra centre bulge, `0..1`. `0` keeps the top flat |
| `--profile` | `sphere` | Edge roll shape: `sphere` (pillow), `smooth` (balloon), `super` (fuller shoulder) |
| `--flat-back` | off | Flat bottom at `z = 0`. Prints with zero supports |
| `--hole` | `0` | Keyring hole diameter in mm |
| `--hole-wall` | `2` | Minimum material left around the hole |
| `--res` | `5` | Raster pixels per mm. Cost grows quadratically |
| `--zsteps` | `64` | Vertical samples for marching cubes |
| `--smooth` | `12` | Taubin smoothing passes |
| `--faces` | `40000` | Triangle budget after decimation. `0` keeps the dense mesh |
| `--bezier-steps` | `24` | Line segments per bezier when flattening the outline |
| `-v` / `-q` | | More or less logging |

### Tuning notes

- Letters look under-inflated: raise `--puff`, or lower `--roll` so full thickness is reached
  sooner.
- Sharp tips still sharp (`A`, `W`, `Ж`): raise `--round`.
- Thin strokes fuse together: lower `--round`.
- Facets or steps visible on the surface: raise `--res` and `--zsteps` before raising
  `--smooth`; smoothing cannot add detail that was never sampled.
- No room reported for the keyring hole: the stroke is thinner than `hole/2 + hole-wall`.
  Raise `--size`, or lower `--hole` / `--hole-wall`.

## Printing

`--flat-back` gives a flat bottom, so letters print face-up with no supports and no brim
fiddling. Meshes are exported watertight and resting on `z = 0`, in millimetres, so slicers
need no scaling. For two-sided pillows (no `--flat-back`) expect supports or a raft.

## Library use

```python
from pathlib import Path

from bubblegen import BubbleParams, Font, Profile, build_alphabet, export_stl

font = Font.load("Inter.ttf")
params = BubbleParams(size_mm=40, puff_mm=5, dome=0.3, profile=Profile.SMOOTH, flat_back=True)

for letter in build_alphabet(font, "IGOR", params):
    print(letter.char, letter.extents, letter.is_watertight)
    export_stl(letter, Path("out"))
```

`BubbleParams` is frozen and validated on construction, so bad values fail fast rather than
producing a broken mesh. `build_letter` raises `BubbleGenError` subclasses
(`GlyphNotFoundError`, `EmptyGlyphError`, `MeshError`); `build_alphabet` logs and skips them.

## Layout

```
src/bubblegen/
  config.py     BubbleParams, Profile: every tunable, validated
  fonts.py      outline extraction, bezier flattening, mm scaling
  raster.py     contours -> mask -> signed distance field
  inflate.py    signed distance -> half-thickness
  hole.py       keyring hole placement and boolean drilling
  mesh.py       marching cubes, cleanup, decimation, smoothing
  pipeline.py   character -> LetterMesh -> STL
  cli.py        argument parsing and logging
tests/          one module per source module
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

MIT. See [LICENSE](LICENSE).
