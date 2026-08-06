"""Command line entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from bubblegen.config import BubbleParams
from bubblegen.errors import BubbleGenError
from bubblegen.fonts import Font
from bubblegen.pipeline import build_alphabet, export_stl

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger("bubblegen")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bubblegen",
        description=(
            "Generate inflated 'bubble' letter STLs from any TTF/OTF font: "
            "puffed on top, flat on the bottom, ready to print and hang."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    defaults = BubbleParams()

    parser.add_argument("--font", required=True, type=Path, help="path to a .ttf or .otf")
    parser.add_argument("--chars", required=True, help='characters, e.g. "ABCÞÐÆ" or "АБВ"')
    parser.add_argument("--out", type=Path, default=Path("out"), help="output directory")

    shape = parser.add_argument_group("shape")
    shape.add_argument("--size", type=float, default=defaults.size_mm, help="cap height in mm")
    shape.add_argument(
        "--puff",
        type=float,
        default=defaults.puff_mm,
        help="thickness in mm, capped per letter at the stroke half-width",
    )
    shape.add_argument(
        "--round",
        dest="round_r",
        type=float,
        default=None,
        help="max silhouette rounding radius in mm [default: 0.45*puff]",
    )
    shape.add_argument(
        "--base-round",
        type=float,
        default=None,
        help="underside fillet radius in mm [default: 0.25*puff]",
    )

    quality = parser.add_argument_group("quality and cost")
    quality.add_argument(
        "--res", type=float, default=defaults.resolution, help="raster pixels per mm"
    )
    quality.add_argument("--zsteps", type=int, default=defaults.z_steps, help="vertical samples")
    quality.add_argument(
        "--smooth", type=int, default=defaults.smooth_iterations, help="Taubin iterations"
    )
    quality.add_argument(
        "--faces",
        type=int,
        default=defaults.target_faces,
        help="target triangle count (0 = raw marching-cubes mesh)",
    )
    quality.add_argument(
        "--bezier-steps",
        type=int,
        default=defaults.bezier_steps,
        help="line segments per bezier",
    )

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose", action="store_true", help="log every pipeline step")
    verbosity.add_argument("-q", "--quiet", action="store_true", help="log warnings only")

    return parser


def params_from_args(args: argparse.Namespace) -> BubbleParams:
    return BubbleParams(
        size_mm=args.size,
        puff_mm=args.puff,
        round_mm=args.round_r,
        base_round_mm=args.base_round,
        resolution=args.res,
        z_steps=args.zsteps,
        smooth_iterations=args.smooth,
        target_faces=args.faces,
        bezier_steps=args.bezier_steps,
    )


def _configure_logging(args: argparse.Namespace) -> None:
    if args.verbose:
        level = logging.DEBUG
    elif args.quiet:
        level = logging.WARNING
    else:
        level = logging.INFO
    logging.basicConfig(level=level, format="%(message)s", stream=sys.stderr, force=True)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _configure_logging(args)

    try:
        params = params_from_args(args)
        font = Font.load(args.font)
    except (BubbleGenError, ValueError) as exc:
        logger.error("%s", exc)
        return 1

    logger.info(
        "font: %s  upem=%d  scale=%.5f mm/unit",
        font.name,
        font.units_per_em,
        font.scale_for(params.size_mm),
    )

    written = 0
    for letter in build_alphabet(font, args.chars, params):
        path = export_stl(letter, args.out)
        x, y, z = letter.extents
        logger.info(
            "  %s -> %s  %.1f x %.1f x %.1f mm  %d tris  watertight=%s",
            letter.char,
            path.name,
            x,
            y,
            z,
            letter.face_count,
            letter.is_watertight,
        )
        written += 1

    if not written:
        logger.error("nothing was generated for %r", args.chars)
        return 1

    logger.info("done, %d letter(s) -> %s", written, args.out.resolve())
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
