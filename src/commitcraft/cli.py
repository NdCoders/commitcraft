"""Command-line interface for commitcraft."""

from __future__ import annotations

import argparse
import sys

from commitcraft.core import update_commit_message

DEFAULT_REGEX = r"[A-Z]+-\d+"
DEFAULT_FORMAT = "{ticket} {commit_msg}"


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="commitcraft",
        description="Add ticket info to commit messages based on branch name.",
    )
    parser.add_argument(
        "filename",
        help="Path to the commit message file (provided by git)",
    )
    parser.add_argument(
        "--regex",
        default=DEFAULT_REGEX,
        help=f"Regex pattern to extract ticket from branch name (default: {DEFAULT_REGEX})",
    )
    parser.add_argument(
        "--format",
        dest="format_template",
        default=DEFAULT_FORMAT,
        help=(
            "Format template for commit subject. "
            "Placeholders: {ticket}, {tickets}, {commit_msg} "
            f"(default: {DEFAULT_FORMAT})"
        ),
    )
    parser.add_argument(
        "--body",
        dest="body_template",
        default=None,
        help=(
            "Format template for commit body. "
            "Placeholders: {ticket}, {tickets}. "
            "Example: 'Ticket: [{ticket}](https://jira.example.com/browse/{ticket})'"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        update_commit_message(
            filename=args.filename,
            regex=args.regex,
            format_template=args.format_template,
            body_template=args.body_template,
        )
    except Exception as e:
        print(f"commitcraft error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
