<p align="center">
  <img src="https://raw.githubusercontent.com/doydl-technologies/numbr/main/assets/png/numbr-lockup-endorsed-1118x344.png" alt="numbr" width="700">
</p>

<p align="center">
  Parses, extracts, normalizes, and converts English number words, integers, exact decimals, scientific and accounting notation, ordinal digits, and Roman numerals.
</p>


<p align="center">
  <a href="https://pypi.org/project/numbr/"><img src="https://img.shields.io/pypi/v/numbr" alt="PyPI version"></a>
  <a href="https://pypi.org/project/numbr/"><img src="https://img.shields.io/pypi/pyversions/numbr" alt="Supported Python versions"></a>
  <a href="https://pepy.tech/project/numbr"><img src="https://static.pepy.tech/badge/numbr" alt="Downloads"></a>
  <a href="https://doydl.com"><img src="https://img.shields.io/badge/Powered%20by-DOYDL%20Technologies-blue" alt="Powered by DOYDL Technologies"></a>
</p>

## Table of contents

- [What numbr does](#what-numbr-does)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Choosing the right API](#choosing-the-right-api)
- [Exact decimal values](#exact-decimal-values)
- [Representations](#representations)
- [Public API](#public-api)
  - [General conversion](#general-conversion)
  - [Scientific and accounting notation](#scientific-and-accounting-notation)
  - [Structured extraction](#structured-extraction)
  - [Whole-text normalization](#whole-text-normalization)
  - [Rich parsing diagnostics](#rich-parsing-diagnostics)
  - [Batch conversion](#batch-conversion)
  - [Parsing and formatting](#parsing-and-formatting)
- [Development](#development)
- [License](#license)

## What numbr does

`numbr` gives Python applications one consistent way to understand numbers
written in different forms. It can recognize that `"forty-two"`, `"42"`, and
`"XLII"` represent the same value, then convert them to the representation an
application needs.

The package is useful when numeric data arrives as human-written text rather
than a clean integer or decimal. Common examples include form responses,
documents, transcripts, scraped text, NLP pipelines, and imported business
data.

With `numbr`, an application can:

- identify the representation of one numeric value;
- convert between digits, English number words, ordinals, and Roman numerals;
- parse exact decimals, scientific notation, and accounting notation;
- find every numeric expression in a larger passage of text;
- replace numeric expressions while leaving the surrounding text intact;
- receive structured explanations for invalid input; and
- apply the same conversion or diagnostic operation to an iterable of values.

`numbr` is deterministic and rule-based. It does not use a language model,
network service, locale database, or heuristic confidence score. The same
supported input produces the same result on every platform.

## Installation

Install the latest release from PyPI:

```bash
python -m pip install numbr
```

Or install the current development version from GitHub:

```bash
python -m pip install 'numbr @ git+ssh://git@github.com/doydl-technologies/numbr.git'
```

Python 3.13 is required. The package has no runtime dependencies.

## Quick start

Import `numbr`, then choose an operation based on whether the input is one
value, a passage of text, or a collection of values.

```python
import numbr

# Identify how one value is written.
numbr.Type("forty-second")
# "Ordinal Word"

# Convert one value to a requested representation.
numbr.Cast("forty-second", "Cardinal Number")
# 42

numbr.Cast("1.050", "Cardinal Word")
# "one point zero five zero"

# Collect normalized values from a larger passage.
numbr.extractNumericValue("She placed 2nd with 1.05 points")
# [2, Decimal("1.05")]

# Collect values together with their original text and source positions.
numbr.extractNumericEntities("She placed 2nd with 1.05 points")
# [NumericMatch(text='2nd', value=2, representation='Ordinal Number', ...),
#  NumericMatch(text='1.05', value=Decimal('1.05'), representation='Decimal Number', ...)]

# Rewrite recognized expressions without changing the surrounding sentence.
numbr.normalizeNumericText("She placed forty-second with 1.20e3 points")
# "She placed 42nd with 1200 points"

# Apply one conversion to several values.
numbr.batchCast(["one", "2", "III"], "Cardinal Number")
# [1, 2, 3]
```

The `Decimal(...)` text shown above is Python's representation of the returned
value; the quick-start example does not need to import `Decimal`.

## Choosing the right API

| Goal | API | Result |
|---|---|---|
| Identify how one value is written | `Type(value)` | A representation name such as `"Ordinal Word"`, or `None` |
| Convert one value | `Cast(value, target)` | The value in the requested representation |
| Collect only values from text | `extractNumericValue(text)` | A list of normalized `int` or `Decimal` values |
| Collect values and source details | `extractNumericEntities(text)` | A list of `NumericMatch` records with text, type, value, and position |
| Rewrite numbers inside text | `normalizeNumericText(text)` | A new string with recognized expressions normalized |
| Explain why parsing failed | `diagnoseNumeric(value)` | A `ParseResult` containing either a value or structured diagnostics |
| Convert many inputs | `batchCast(values, target)` | A list of converted values using the selected error policy |
| Diagnose many inputs | `batchDiagnose(values, target)` | One index-stable `ParseResult` per input |

Conversion operates on one numeric value. Extraction searches a larger string
and returns the numbers it contains. Normalization also searches a larger
string, but returns rewritten text instead of match records.

## Exact decimal values

Decimal parsing returns [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal)
instead of `float`. `Decimal` is part of Python's standard library; it is not an
additional dependency. This avoids binary floating-point rounding and preserves
meaningful fractional zeros such as the final zero in `"1.050"`.

No `Decimal` import is required when the input is a string:

```python
import numbr

value = numbr.Cast("1.050", "Decimal Number")

value
# Decimal("1.050")

numbr.Cast(value, "Cardinal Word")
# "one point zero five zero"
```

Import `Decimal` only when application code needs to construct a decimal value
directly or perform decimal arithmetic:

```python
from decimal import Decimal

import numbr

numbr.decimalToAccounting(Decimal("-1234.50"), currency="$")
# "($1,234.50)"
```

## Representations

| Representation | Meaning | Examples | `Type` result |
|---|---|---|---|
| Cardinal number | A whole-number quantity written with digits | `42`, `"-42"` | `"Cardinal Number"` |
| Decimal number | A fixed-point value with a fractional part | `"1.05"`, `Decimal("1.050")` | `"Decimal Number"` |
| Scientific number | A coefficient multiplied by a power of ten | `"1.20e3"`, `"-4E-2"` | `"Scientific Number"` |
| Accounting number | A formatted business value whose parentheses indicate a negative amount | `"(1,234.50)"`, `"($50.00)"` | `"Accounting Number"` |
| Cardinal word | A quantity written with English words | `"forty-two"` | `"Cardinal Word"` |
| Ordinal number | A position or rank written with digits and a suffix | `"42nd"` | `"Ordinal Number"` |
| Ordinal word | A position or rank written with English words | `"forty-second"` | `"Ordinal Word"` |
| Roman numeral | A value written with Roman symbols | `"XLII"`, `"Ⅳ"` | `"Roman Numeral"` |

Decimal phrases such as `"one point zero five"` are cardinal-word forms. Digits
following `point` are interpreted individually so precision and trailing zeros
are preserved.

English-word parsing is intended for numeric expressions, not unrestricted
natural-language interpretation. Surrounding prose should be passed to an
extraction or normalization API rather than directly to `Type` or `Cast`.

`Cast` accepts the display names and common aliases such as `int`, `decimal`,
`scientific`, `accounting`, `cardword`, `ordnum`, and `roman`.

```python
numbr.Type("twenty-first")
# "Ordinal Word"

numbr.Cast("twenty-first", "Cardinal Number")
# 21

numbr.Cast(1994, "Roman Numeral")
# "MCMXCIV"

numbr.Type("-0.004")
# "Decimal Number"

numbr.Cast("-0.004", "Cardinal Word")
# "negative zero point zero zero four"
```

Roman output is limited to canonical values from 1 through 3999. English number
conversion supports values whose integer component has an absolute value less
than `10**24`.

## Public API

### General conversion

- `Type(value)` detects the representation or returns `None`.
- `Cast(value, target, *, as_str=False)` converts between representations and
  raises `ValueError` when the input or requested conversion is invalid.

Decimal-number conversions return `decimal.Decimal` to avoid binary floating-point
rounding and to preserve explicitly supplied fractional zeros. Non-integral
decimals cannot be cast to integer-only cardinal, ordinal, or Roman forms.

### Scientific and accounting notation

Scientific notation accepts signed coefficients and exponents, including forms
such as `.5e1` and `5.e2`. Accounting notation uses parentheses for negative
values and accepts a supported currency token either immediately outside or
inside the parentheses.

```python
numbr.scientificToDecimal("1.20e3")
# Decimal("1.20E+3")

numbr.accountingToDecimal("($1,234.50)")
# Decimal("-1234.50")

numbr.decimalToScientific(Decimal("1230.00"))
# "1.23e+3"

numbr.decimalToAccounting(Decimal("-1234.50"), currency="$")
# "($1,234.50)"
```

Both representations participate in `Type`, `Cast`, value extraction, and
structured extraction.

### Structured extraction

`extractNumericEntities(text)` returns an immutable `NumericMatch` for every
recognized expression in source order. Each match provides the original `text`,
normalized `value`, representation name, `start` and `end` offsets, `span`, and
`is_ordinal` and `is_negative` flags.

```python
matches = numbr.extractNumericEntities("She placed forty-second with -0.50 points in round XLII.")

matches[0].text, matches[0].value, matches[0].span
# ("forty-second", 42, (11, 23))

matches[1].value
# Decimal("-0.50")

matches[2].representation
# "Roman Numeral"
```

Canonical Roman numerals are included by default. Single-letter ASCII forms
such as `I`, `V`, and `X` are excluded because they are ambiguous in prose; pass
`include_single_roman=True` to include them. Pass `include_roman=False` to omit
Roman numerals entirely.

### Whole-text normalization

`normalizeNumericText(text, style="digits")` replaces every recognized entity
while preserving all surrounding characters. The default style renders
cardinals as digits and retains ordinal suffixes. Use `style="words"` to spell
values in English while retaining ordinal meaning.

```python
text = "She placed forty-second with 1.20e3 points and lost ($1,234.50)."

numbr.normalizeNumericText(text)
# "She placed 42nd with 1200 points and lost -1234.50."

numbr.normalizeNumericText("Ranked 2nd in round Ⅳ", style="words")
# "Ranked second in round four"
```

The Roman-numeral options are the same as those on `extractNumericEntities`.
Values outside the supported English-word range remain unchanged when using
the `words` style.

### Rich parsing diagnostics

`diagnoseNumeric(value, target=None)` returns an immutable `ParseResult`
instead of raising for invalid input. Successful results contain the normalized
or converted value and source and target representations. Failed results contain
one or more `ParseDiagnostic` objects with a stable code, message, source span,
severity, and suggested correction.

```python
result = numbr.diagnoseNumeric("22st")

result.ok
# False

result.error.code, result.error.span
# ("invalid_ordinal_suffix", (0, 4))

result.error.suggestion
# "Use '22nd'."
```

Diagnostic codes distinguish empty or unsupported inputs, malformed decimal,
scientific, accounting, ordinal, grouping, word, and Roman forms, unknown
targets, and unsupported conversions. Call `result.unwrap()` when exception
semantics are preferred after inspection.

### Batch conversion

`batchCast(values, target)` applies the same conversion rules as `Cast` to any
iterable. The `errors` policy controls failed items:

- `"raise"` raises `BatchConversionError` with the failing index and diagnostic
  result.
- `"coerce"` retains the input shape and places `None` at failed positions.
- `"ignore"` omits failed items.

```python
numbr.batchCast(["one", "invalid", "III"], "Cardinal Number", errors="coerce")
# [1, None, 3]

results = numbr.batchDiagnose(["1e3", "bad", "(2.00)"], "Decimal Number")
[result.ok for result in results]
# [True, False, True]
```

Use `batchDiagnose` when every input needs an index-stable structured result,
regardless of success or failure.

### Parsing and formatting

- `wordsToInt`
- `wordsToDecimal`
- `ordinalWordsToInt`
- `stringToInt`
- `stringToDecimal`
- `scientificToDecimal`
- `accountingToDecimal`
- `intToWords`
- `decimalToWords`
- `decimalToScientific`
- `decimalToAccounting`
- `intToOrdinalWords`
- `romanToInt`
- `romanToWords`
- `intToRoman`
- `ordinalSuffix`
- `stripOrdinalSuffix`
- `extractNumericValue`
- `extractNumericEntities`
- `normalizeNumericText`
- `diagnoseNumeric`
- `batchDiagnose`
- `batchCast`
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

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[CHANGELOG.md](CHANGELOG.md) for contribution guidelines, the security policy,
and release history.

## License

Licensed under the [MIT License](LICENSE).
