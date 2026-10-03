# Changelog

All notable changes to this project are documented here. The project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [2.1.1] - 2026-10-03

### Changed

- Transfer project links and release documentation to the `doydl-technologies` GitHub organization.
- Standardize package authorship, copyright notices, and project headers under DOYDL Technologies.
- Refresh the README with DOYDL branding, project badges, and a table of contents.
- Add official numbr and DOYDL Technologies logo assets.

## [2.1.0] - 2026-09-30

### Added

- Modern `pyproject.toml` packaging with a `src/` layout.
- Automated tests, linting, build validation, and trusted publishing workflows.
- First-class Roman numeral detection and casting, including compatible Unicode numerals.
- `intToRoman` and package-level `__version__`.
- Project security, contribution, and issue-reporting documentation.

### Fixed

- Preserve source order when extracting mixed digit and word values.
- Parse zero as a valid cardinal number.
- Correct negative and scale-based ordinal parsing.
- Reject invalid repeated or ascending English scale expressions.
- Preserve every decimal digit when converting decimals to words.
- Support the documented integer domain `-10^24 < n < 10^24`.
- Align the declared minimum Python version with the implementation.

## [2.0.6] - 2025-04-30

- Previous PyPI release.

[Unreleased]: https://github.com/doydl-technologies/numbr/compare/v2.1.1...HEAD
[2.1.1]: https://github.com/doydl-technologies/numbr/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/doydl-technologies/numbr/compare/v2.0.6...v2.1.0
[2.0.6]: https://github.com/doydl-technologies/numbr/releases/tag/v2.0.6
