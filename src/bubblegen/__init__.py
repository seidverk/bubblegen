"""Parametric inflated 3D bubble letters from any TTF/OTF font."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from bubblegen.config import BubbleParams
from bubblegen.errors import (
    BubbleGenError,
    EmptyGlyphError,
    FontError,
    GlyphNotFoundError,
    TweaksError,
)
from bubblegen.fonts import Font
from bubblegen.pipeline import LetterMesh, build_alphabet, build_letter, export_stl
from bubblegen.stand import StandParams, build_stand
from bubblegen.tweaks import DeepenOp, StretchOp, ThickenOp, load_tweaks

try:
    __version__ = version("bubblegen")
except PackageNotFoundError:  # pragma: no cover - running from a source tree
    __version__ = "0.0.0.dev0"

__all__ = [
    "BubbleGenError",
    "BubbleParams",
    "DeepenOp",
    "EmptyGlyphError",
    "Font",
    "FontError",
    "GlyphNotFoundError",
    "LetterMesh",
    "StandParams",
    "StretchOp",
    "ThickenOp",
    "TweaksError",
    "__version__",
    "build_alphabet",
    "build_letter",
    "build_stand",
    "export_stl",
    "load_tweaks",
]
