"""Parametric inflated 3D bubble letters from any TTF/OTF font."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from bubblegen.config import BubbleParams, Profile
from bubblegen.errors import (
    BubbleGenError,
    EmptyGlyphError,
    FontError,
    GlyphNotFoundError,
    MeshError,
)
from bubblegen.fonts import Font
from bubblegen.pipeline import LetterMesh, build_alphabet, build_letter, export_stl

try:
    __version__ = version("bubblegen")
except PackageNotFoundError:  # pragma: no cover - running from a source tree
    __version__ = "0.0.0.dev0"

__all__ = [
    "BubbleGenError",
    "BubbleParams",
    "EmptyGlyphError",
    "Font",
    "FontError",
    "GlyphNotFoundError",
    "LetterMesh",
    "MeshError",
    "Profile",
    "__version__",
    "build_alphabet",
    "build_letter",
    "export_stl",
]
