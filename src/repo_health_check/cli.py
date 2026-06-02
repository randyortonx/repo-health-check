from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from repo_health_check.checks import run_checks
from repo_health_check.models import Report, Status
from repo_health_check.report import render_json, render_markdown
from repo_health_check.scanner import scan_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit OSS repository health signals.")
    parser.add_argument("path", help="Path to the repository to scan.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Report output format.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        snapshot = scan_repository(args.path)
    except (FileNotFoundError, NotADirectoryError, PermissionError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    report = Report(repo_path=str(snapshot.root), results=run_checks(snapshot))
    if args.format == "json":
        print(render_json(report), end="")
    else:
        print(render_markdown(report), end="")

    return 1 if any(result.status == Status.FAIL for result in report.results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
