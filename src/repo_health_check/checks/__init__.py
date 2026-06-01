from __future__ import annotations

from collections.abc import Callable

from repo_health_check.checks.changelog import check_changelog
from repo_health_check.checks.ci import check_ci
from repo_health_check.checks.contributing import check_contributing
from repo_health_check.checks.license import check_license
from repo_health_check.checks.metadata import check_metadata
from repo_health_check.checks.readme import check_readme
from repo_health_check.checks.security import check_security
from repo_health_check.checks.templates import check_templates
from repo_health_check.models import CheckResult
from repo_health_check.scanner import RepositorySnapshot

Check = Callable[[RepositorySnapshot], CheckResult]

CHECKS: tuple[Check, ...] = (
    check_readme,
    check_license,
    check_ci,
    check_contributing,
    check_security,
    check_templates,
    check_changelog,
    check_metadata,
)


def run_checks(snapshot: RepositorySnapshot) -> list[CheckResult]:
    return [check(snapshot) for check in CHECKS]
