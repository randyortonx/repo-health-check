# Contributing

Thanks for helping improve `repo-health-check`.

## Development Setup

Use Python 3.11+ for local development.

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -v
```

## Pull Requests

- Keep checks small and deterministic.
- Add or update tests before changing behavior.
- Avoid network calls in core checks.
- Update README examples when CLI behavior changes.
