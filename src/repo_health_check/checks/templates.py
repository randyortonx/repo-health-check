from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot


def check_templates(snapshot: RepositorySnapshot) -> CheckResult:
    issue_templates = snapshot.files_under(".github/ISSUE_TEMPLATE")
    pr_templates = [path for path in (".github/pull_request_template.md", ".github/PULL_REQUEST_TEMPLATE.md") if snapshot.has_file(path)]
    if issue_templates and pr_templates:
        return CheckResult("templates", "Issue and PR templates", Status.PASS, "Found issue and pull request templates.", "No action needed.")
    return CheckResult("templates", "Issue and PR templates", Status.WARN, "Issue or pull request templates are missing.", "Add issue templates and .github/pull_request_template.md.")
