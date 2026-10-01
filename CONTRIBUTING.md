# Contributing

Thank you for helping improve `numbr`.

## Development setup

```bash
git clone git@github.com:cedricmoorejr/numbr.git
cd numbr
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

On Windows with MSYS2 UCRT64, activate the environment with:

```bash
source .venv/Scripts/activate
```

## Before opening a pull request

```bash
ruff check .
ruff format --check .
pytest
python -m build
python -m twine check dist/*
```

Add regression tests for behavior changes. Keep public API changes documented in
`README.md` and `CHANGELOG.md`.

Maintainers should follow [RELEASING.md](RELEASING.md) when preparing a GitHub
and PyPI release.
