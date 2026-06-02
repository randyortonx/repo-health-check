# Contributing

Thanks for helping improve `repo-health-check`.

## Development Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest -v
```

## Pull Requests

- Keep checks small and deterministic.
- Add or update tests before changing behavior.
- Avoid network calls in core checks.
- Update README examples when CLI behavior changes.
