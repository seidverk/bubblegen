"""Exception hierarchy: every expected failure is a `BubbleGenError`."""

from __future__ import annotations


class BubbleGenError(Exception):
    """Base class for all bubblegen failures."""


class FontError(BubbleGenError):
    """Font file missing, unreadable, or not a font."""


class GlyphNotFoundError(BubbleGenError):
    """The font has no glyph for the requested character."""


class EmptyGlyphError(BubbleGenError):
    """The glyph exists but has no outline (space, control character)."""
