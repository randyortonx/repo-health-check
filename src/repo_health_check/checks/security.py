from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

SECURITY_NAMES = ("SECURITY.md", "SECURITY.rst", "SECURITY.txt")


def check_security(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*SECURITY_NAMES)
    if matches:
        return CheckResult("security", "Security policy", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("security", "Security policy", Status.WARN, "No security policy was found.", "Add SECURITY.md with vulnerability reporting guidance.")
