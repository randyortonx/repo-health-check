from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

CONTRIBUTING_NAMES = ("CONTRIBUTING.md", "CONTRIBUTING.rst", "CONTRIBUTING.txt")


def check_contributing(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*CONTRIBUTING_NAMES)
    if matches:
        return CheckResult("contributing", "Contributing guide", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("contributing", "Contributing guide", Status.WARN, "No contributing guide was found.", "Add CONTRIBUTING.md with setup, testing, and pull request expectations.")
