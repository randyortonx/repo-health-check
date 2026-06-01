from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")


def check_license(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*LICENSE_NAMES)
    if matches:
        return CheckResult("license", "License", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("license", "License", Status.FAIL, "No license file was found.", "Add an OSI-approved license file such as MIT, Apache-2.0, or BSD-3-Clause.")
