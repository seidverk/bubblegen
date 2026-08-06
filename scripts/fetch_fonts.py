#!/usr/bin/env python
"""Download a few heavy display fonts into `fonts/`, ready for bubble letters.

Bubble letters need thick strokes: the rounding radius erodes by roughly half a
stroke, so light fonts dissolve. Everything here is SIL Open Font License.

Variable fonts are pinned to their heaviest instance, because glyph outlines are
read at the default location and that default is usually a light weight.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

GOOGLE_FONTS = "https://raw.githubusercontent.com/google/fonts/main"
FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"

STATIC = [
    "ofl/sniglet/Sniglet-ExtraBold.ttf",
    "ofl/modak/Modak-Regular.ttf",
    "ofl/titanone/TitanOne-Regular.ttf",
    "ofl/lilitaone/LilitaOne-Regular.ttf",
]

# (source path, output name, axis location) - Nunito also covers Cyrillic
VARIABLE = [
    ("ofl/gluten/Gluten%5Bslnt,wght%5D.ttf", "Gluten-Black.ttf", {"wght": 900, "slnt": 0}),
    ("ofl/nunito/Nunito%5Bwght%5D.ttf", "Nunito-Black.ttf", {"wght": 900}),
    ("ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf", "Fredoka-Bold.ttf", {"wght": 700, "wdth": 125}),
]


def download(remote_path: str, target: Path) -> None:
    url = f"{GOOGLE_FONTS}/{remote_path}"
    with urllib.request.urlopen(url) as response:
        target.write_bytes(response.read())
    print(f"  {target.name}  ({target.stat().st_size // 1024} KiB)")


def pin_instance(source: Path, target: Path, location: dict[str, float]) -> None:
    font = instancer.instantiateVariableFont(TTFont(source), location, inplace=False)
    font["OS/2"].usWeightClass = int(location["wght"])
    font.save(target)
    source.unlink()
    axes = ", ".join(f"{axis}={value:g}" for axis, value in location.items())
    print(f"  {target.name}  (pinned {axes})")


def main() -> None:
    FONTS_DIR.mkdir(exist_ok=True)
    print(f"fonts -> {FONTS_DIR}")

    for remote_path in STATIC:
        download(remote_path, FONTS_DIR / Path(remote_path).name)

    for remote_path, name, location in VARIABLE:
        raw = FONTS_DIR / "_variable.ttf"
        download(remote_path, raw)
        pin_instance(raw, FONTS_DIR / name, location)


if __name__ == "__main__":
    main()
