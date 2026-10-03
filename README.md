<p align="center">
  <img src="https://raw.githubusercontent.com/doydl-technologies/numbr/main/assets/png/numbr-primary-wordmark-1200x360.png" alt="numbr" width="700">
</p>

<p align="center">
  Parses and converts numbers represented as English cardinal words, English ordinal words, decimal digits, ordinal digits, and Roman numerals.
</p>


<p align="center">
  <a href="https://pypi.org/project/numbr/"><img src="https://img.shields.io/pypi/v/numbr" alt="PyPI version"></a>
  <a href="https://pypi.org/project/numbr/"><img src="https://img.shields.io/pypi/pyversions/numbr" alt="Supported Python versions"></a>
  <a href="https://pepy.tech/project/numbr"><img src="https://static.pepy.tech/badge/numbr" alt="Downloads"></a>
  <a href="https://doydl.com"><img src="https://img.shields.io/badge/Powered%20by-DOYDL%20Technologies-blue" alt="Powered by DOYDL Technologies"></a>
</p>

## Table of contents

- [Installation](#installation)
- [Representations](#representations)
- [Public API](#public-api)
  - [General conversion](#general-conversion)
  - [Parsing and formatting](#parsing-and-formatting)
- [Development](#development)
- [License](#license)

```python
import numbr

numbr.wordsToInt("one hundred sixty-seven")
# 167

numbr.Cast("forty-ninth", "Ordinal Number")
# "49th"

numbr.Cast("Ⅳ", "Ordinal Word")
# "fourth"

numbr.extractNumericValue("He scored twenty-one of 34 attempts")
# [21, 34]
```

## Installation

Install the latest release from PyPI:

```bash
python -m pip install numbr
```

Or install the current development version from GitHub:

```bash
python -m pip install 'numbr @ git+ssh://git@github.com/doydl-technologies/numbr.git'
```

Python 3.8 or newer is required. The package has no runtime dependencies.

## Representations

| Representation | Examples | `Type` result |
|---|---|---|
| Cardinal number | `42`, `"-42"` | `"Cardinal Number"` |
| Cardinal word | `"forty-two"` | `"Cardinal Word"` |
| Ordinal number | `"42nd"` | `"Ordinal Number"` |
| Ordinal word | `"forty-second"` | `"Ordinal Word"` |
| Roman numeral | `"XLII"`, `"Ⅳ"` | `"Roman Numeral"` |

`Cast` accepts those display names and common aliases such as `int`, `cardword`,
`ordnum`, and `roman`.

```python
numbr.Type("twenty-first")
# "Ordinal Word"

numbr.Cast("twenty-first", "Cardinal Number")
# 21

numbr.Cast(1994, "Roman Numeral")
# "MCMXCIV"
```

Roman output is limited to canonical values from 1 through 3999. English number
conversion supports integers whose absolute value is less than `10**24`.

## Public API

### General conversion

- `Type(value)` detects the representation or returns `None`.
- `Cast(value, target, *, as_str=False)` converts between representations and
  raises `ValueError` when the input or requested conversion is invalid.

### Parsing and formatting

- `wordsToInt`
- `ordinalWordsToInt`
- `stringToInt`
- `intToWords`
- `intToOrdinalWords`
- `romanToInt`
- `romanToWords`
- `intToRoman`
- `ordinalSuffix`
- `stripOrdinalSuffix`
- `extractNumericValue`
- `insertSep`
- `formatDecimal`

The direct cross-representation helpers from earlier releases remain available,
including `cardinalWordToOrdinalNum`, `ordinalNumToCardinalWord`, and related
functions.

Lower-level parsing functions return `None` for invalid input. Decimal conversion
spells digits after the point individually so that zeros are preserved:

```python
numbr.intToWords("1.05")
# "one point zero five"
```

## Development

```bash
git clone git@github.com:doydl-technologies/numbr.git
cd numbr
python -m venv .venv
source .venv/bin/activate  # .venv/Scripts/activate on MSYS2/Windows
python -m pip install -e '.[dev]'
pytest
ruff check .
python -m build
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md),
[CHANGELOG.md](CHANGELOG.md), and [RELEASING.md](RELEASING.md) for project
policies, release history, and the maintainer release procedure.

## License

Licensed under the [MIT License](LICENSE).
