from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

CHANGELOG_NAMES = ("CHANGELOG.md", "CHANGELOG.rst", "HISTORY.md", "RELEASES.md")


def check_changelog(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*CHANGELOG_NAMES)
    if matches:
        return CheckResult("changelog", "Changelog", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("changelog", "Changelog", Status.WARN, "No changelog or release notes file was found.", "Add CHANGELOG.md to document user-visible changes.")
