from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

METADATA_NAMES = ("pyproject.toml", "package.json", "Cargo.toml", "go.mod", "pom.xml", "build.gradle")


def check_metadata(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*METADATA_NAMES)
    if matches:
        return CheckResult("metadata", "Package metadata", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("metadata", "Package metadata", Status.WARN, "No common package metadata file was found.", "Add ecosystem metadata such as pyproject.toml, package.json, Cargo.toml, or go.mod when applicable.")
