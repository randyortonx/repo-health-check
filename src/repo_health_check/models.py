from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    title: str
    status: Status
    summary: str
    suggestion: str


@dataclass(frozen=True)
class Report:
    repo_path: str
    results: list[CheckResult]

    @property
    def counts(self) -> dict[str, int]:
        return {
            Status.PASS.value: sum(1 for result in self.results if result.status == Status.PASS),
            Status.WARN.value: sum(1 for result in self.results if result.status == Status.WARN),
            Status.FAIL.value: sum(1 for result in self.results if result.status == Status.FAIL),
        }

    @property
    def score(self) -> int:
        if not self.results:
            return 0
        earned = 0.0
        for result in self.results:
            if result.status == Status.PASS:
                earned += 1.0
            elif result.status == Status.WARN:
                earned += 0.5
        return round((earned / len(self.results)) * 100)

    @property
    def next_actions(self) -> list[CheckResult]:
        failures = [result for result in self.results if result.status == Status.FAIL]
        warnings = [result for result in self.results if result.status == Status.WARN]
        return failures + warnings
