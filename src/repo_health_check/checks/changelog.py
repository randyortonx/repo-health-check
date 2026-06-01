from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

CHANGELOG_NAMES = ("CHANGELOG.md", "CHANGELOG.rst", "HISTORY.md", "RELEASES.md")


def check_changelog(snapshot: RepositorySnapshot) -> CheckResult:
    matches = _root_matching_files(snapshot, *CHANGELOG_NAMES)
    if matches:
        return CheckResult("changelog", "Changelog", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("changelog", "Changelog", Status.WARN, "No changelog or release notes file was found.", "Add CHANGELOG.md to document user-visible changes.")


def _root_matching_files(snapshot: RepositorySnapshot, *names: str) -> list[str]:
    wanted = {name.lower() for name in names}
    return sorted(path for path in snapshot.files if "/" not in path and path.lower() in wanted)
