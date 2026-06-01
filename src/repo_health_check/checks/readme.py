from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

README_NAMES = ("README.md", "README.rst", "README.txt", "README")
HELPFUL_TERMS = ("install", "installation", "usage", "quickstart", "contributing", "maintain")


def check_readme(snapshot: RepositorySnapshot) -> CheckResult:
    matches = _root_matching_files(snapshot, *README_NAMES)
    if not matches:
        return CheckResult("readme", "README", Status.FAIL, "No README file was found.", "Add a README with installation, usage, and contribution guidance.")
    try:
        content = snapshot.read_text(matches[0]).lower()
    except UnicodeDecodeError:
        return CheckResult("readme", "README", Status.WARN, f"Found {matches[0]}, but it could not be decoded as UTF-8 text.", "Replace or re-encode README as UTF-8 text.")
    if any(term in content for term in HELPFUL_TERMS):
        return CheckResult("readme", "README", Status.PASS, f"Found {matches[0]} with usage-oriented content.", "No action needed.")
    return CheckResult("readme", "README", Status.WARN, f"Found {matches[0]}, but it has limited usage guidance.", "Add installation, usage, or contribution sections.")


def _root_matching_files(snapshot: RepositorySnapshot, *names: str) -> list[str]:
    wanted = {name.lower() for name in names}
    return sorted(path for path in snapshot.files if "/" not in path and path.lower() in wanted)
