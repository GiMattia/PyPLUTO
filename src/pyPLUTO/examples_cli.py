"""CLI for packaged PyPLUTO examples."""

from __future__ import annotations

import argparse
import sys

from pyPLUTO.examples_api import (
    copy_examples,
    examples_path,
    list_examples,
    run_example,
)


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the ``pypluto-examples`` CLI."""
    parser = argparse.ArgumentParser(
        prog="pypluto-examples",
        description="Inspect, copy, or run packaged PyPLUTO examples.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("path", help="Print installed examples directory.")
    sub.add_parser("list", help="List runnable example scripts.")

    copy_parser = sub.add_parser(
        "copy", help="Copy examples to a local directory."
    )
    copy_parser.add_argument(
        "dst",
        nargs="?",
        default="pypluto_examples",
        help="Destination directory (default: pypluto_examples).",
    )
    copy_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow copying into an existing directory.",
    )

    run_parser = sub.add_parser("run", help="Run an example script by name.")
    run_parser.add_argument(
        "example", help="Example name, e.g. test01_sod or test01_sod.py"
    )
    run_parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Extra args for script."
    )

    return parser


def main() -> int:
    """Entry point for ``pypluto-examples``."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "path":
        print(examples_path())
        return 0

    if args.command == "list":
        for item in list_examples():
            print(item.name)
        return 0

    if args.command == "copy":
        dest = copy_examples(args.dst, overwrite=args.overwrite)
        print(dest)
        return 0

    if args.command == "run":
        forwarded = args.args
        if forwarded and forwarded[0] == "--":
            forwarded = forwarded[1:]
        return run_example(args.example, *forwarded)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
