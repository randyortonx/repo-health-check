from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot


def check_ci(snapshot: RepositorySnapshot) -> CheckResult:
    workflow_files = [path for path in snapshot.files_under(".github/workflows") if path.endswith((".yml", ".yaml"))]
    if workflow_files:
        return CheckResult("ci", "Continuous integration", Status.PASS, f"Found {len(workflow_files)} GitHub Actions workflow file(s).", "No action needed.")
    return CheckResult("ci", "Continuous integration", Status.FAIL, "No GitHub Actions workflow was found.", "Add a workflow under .github/workflows to run tests on pull requests.")
