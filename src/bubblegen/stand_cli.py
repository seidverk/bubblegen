"""Command line entry point for the painting stand.

Separate from `bubblegen.cli` on purpose: that parser is flat and requires `--font`, so
folding the stand into it as a subcommand would break every existing invocation.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from bubblegen.stand import StandParams, build_stand

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger("bubblegen.stand")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bubblegen-stand",
        description=(
            "Generate a low stand with a honeycomb deck: it holds a letter on wall "
            "crests while you paint it with UV resin, so the resin drips through "
            "instead of gluing the letter down."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    defaults = StandParams()

    parser.add_argument("--out", type=Path, default=Path("out/stand.stl"), help="output .stl path")

    shape = parser.add_argument_group("shape")
    shape.add_argument("--size", type=float, default=defaults.size_mm, help="deck side in mm")
    shape.add_argument(
        "--height", type=float, default=defaults.height_mm, help="total height in mm"
    )
    shape.add_argument("--deck", type=float, default=defaults.deck_mm, help="deck thickness in mm")
    shape.add_argument("--leg", type=float, default=defaults.leg_mm, help="corner post section")

    honeycomb = parser.add_argument_group("honeycomb")
    honeycomb.add_argument(
        "--cell", type=float, default=defaults.cell_mm, help="hexagon across the flats"
    )
    honeycomb.add_argument(
        "--wall", type=float, default=defaults.wall_mm, help="wall thickness at the underside"
    )
    honeycomb.add_argument(
        "--crest",
        type=float,
        default=defaults.crest_mm,
        help="wall thickness where the letter touches; thinner drafts the cells more",
    )
    honeycomb.add_argument(
        "--rim", type=float, default=defaults.rim_mm, help="solid border around the cells"
    )

    output = parser.add_argument_group("output")
    output.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    output.add_argument("-q", "--quiet", action="store_true", help="warnings only")
    return parser


def params_from_args(args: argparse.Namespace) -> StandParams:
    return StandParams(
        size_mm=args.size,
        height_mm=args.height,
        deck_mm=args.deck,
        cell_mm=args.cell,
        wall_mm=args.wall,
        crest_mm=args.crest,
        rim_mm=args.rim,
        leg_mm=args.leg,
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
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    stand = build_stand(params)
    out: Path = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    stand.export(out)

    x, y, z = stand.extents
    logger.info(
        "%s  %.1f x %.1f x %.1f mm  %d tris  watertight=%s",
        out,
        x,
        y,
        z,
        len(stand.faces),
        stand.is_watertight,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
