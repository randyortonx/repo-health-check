from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

SECURITY_NAMES = ("SECURITY.md", "SECURITY.rst", "SECURITY.txt")


def check_security(snapshot: RepositorySnapshot) -> CheckResult:
    matches = _root_matching_files(snapshot, *SECURITY_NAMES)
    if matches:
        return CheckResult("security", "Security policy", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("security", "Security policy", Status.WARN, "No security policy was found.", "Add SECURITY.md with vulnerability reporting guidance.")


def _root_matching_files(snapshot: RepositorySnapshot, *names: str) -> list[str]:
    wanted = {name.lower() for name in names}
    return sorted(path for path in snapshot.files if "/" not in path and path.lower() in wanted)
