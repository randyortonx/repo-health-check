from __future__ import annotations

import json

from repo_health_check.models import CheckResult, Report


STATUS_LABELS = {
    "pass": "PASS",
    "warn": "WARN",
    "fail": "FAIL",
}


def render_markdown(report: Report) -> str:
    lines = [
        "# Repository Health Report",
        "",
        f"Repository: `{report.repo_path}`",
        f"Score: {report.score}/100",
        "",
        "## Summary",
        "",
        f"- Pass: {report.counts['pass']}",
        f"- Warn: {report.counts['warn']}",
        f"- Fail: {report.counts['fail']}",
        "",
        "## Results",
        "",
    ]
    for result in report.results:
        lines.extend(_render_result(result))

    lines.extend(["## Next Actions", ""])
    if not report.next_actions:
        lines.append("No required actions.")
    else:
        for result in report.next_actions:
            lines.append(f"- **{result.title}**: {result.suggestion}")
    lines.append("")
    return "\n".join(lines)


def _render_result(result: CheckResult) -> list[str]:
    label = STATUS_LABELS[result.status.value]
    return [
        f"### {label}: {result.title}",
        "",
        result.summary,
        "",
        f"Suggested fix: {result.suggestion}",
        "",
    ]


def render_json(report: Report) -> str:
    payload = {
        "repo_path": report.repo_path,
        "score": report.score,
        "counts": report.counts,
        "results": [
            {
                "check_id": result.check_id,
                "title": result.title,
                "status": result.status.value,
                "summary": result.summary,
                "suggestion": result.suggestion,
            }
            for result in report.results
        ],
        "next_actions": [result.check_id for result in report.next_actions],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
