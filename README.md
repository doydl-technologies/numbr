<p align="center">
  <img src="https://raw.githubusercontent.com/doydl-technologies/numbr/main/assets/png/numbr-lockup-endorsed-1118x344.png" alt="numbr" width="700">
</p>

<p align="center">
  🔢 Parses, extracts, normalizes, and converts English number words, integers, exact decimals, scientific and accounting notation, ordinal digits, and Roman numerals.
</p>

<p align="center">
  <a href="https://pypi.org/project/numbr/"><img src="https://img.shields.io/pypi/v/numbr" alt="PyPI version"></a>
  <a href="https://pypi.org/project/numbr/"><img src="https://img.shields.io/pypi/pyversions/numbr" alt="Supported Python versions"></a>
  <a href="https://pepy.tech/project/numbr"><img src="https://static.pepy.tech/badge/numbr" alt="Downloads"></a>
  <a href="https://doydl.com"><img src="https://img.shields.io/badge/Powered%20by-DOYDL%20Technologies-blue" alt="Powered by DOYDL Technologies"></a>
</p>

---

## 🧭 Table of contents

- [🔍 What numbr does](#-what-numbr-does)
- [📦 Installation](#-installation)
- [🚀 Quick start](#-quick-start)
- [🧰 Choosing the right API](#-choosing-the-right-api)
- [🎯 Exact decimal values](#-exact-decimal-values)
- [🔢 Representations](#-representations)
- [🛠️ Public API](#️-public-api)
  - [🔄 General conversion](#-general-conversion)
  - [🧪 Scientific and accounting notation](#-scientific-and-accounting-notation)
  - [🔎 Structured extraction](#-structured-extraction)
  - [📝 Whole-text normalization](#-whole-text-normalization)
  - [🩺 Rich parsing diagnostics](#-rich-parsing-diagnostics)
  - [📚 Batch conversion](#-batch-conversion)
  - [🧩 Parsing and formatting](#-parsing-and-formatting)
- [👨‍💻 Development](#-development)
- [⚖️ License](#️-license)

---

## 🔍 What numbr does

**numbr** gives Python applications one consistent way to understand numbers written in different forms.

For example, it recognizes that:

| Input | Representation | Numeric value |
|---|---|---|
| `"forty-two"` | 🔤 English words | `42` |
| `"42"` | 🔢 Integer | `42` |
| `"XLII"` | 🏛️ Roman numeral | `42` |

All three represent the **same underlying value**, which can then be converted into whichever representation your application needs.

### 💡 When is numbr useful?

The package is especially useful when numeric data arrives as human-written text rather than a clean integer or decimal.

Common use cases include:

- 📝 Form responses and documents
- 🎙️ Transcripts and speech-to-text output
- 🌐 Web scraping and extracted text
- 🧠 NLP and text-processing pipelines
- 🏢 Imported business and financial data

### ✨ What can it do?

With `numbr`, your application can:

- 🔍 **Detect** the representation of a numeric value.
- 🔄 **Convert** between digits, English number words, ordinals, and Roman numerals.
- 🎯 **Parse** exact decimals, scientific notation, and accounting notation.
- 📖 **Extract** numeric expressions from larger passages.
- ✏️ **Normalize** numeric expressions while preserving surrounding text.
- 🩺 **Diagnose** invalid input with structured explanations.
- 📚 **Process batches** of values using consistent conversion rules.

### ⚙️ How it works

**numbr is deterministic and rule-based.**

It does not use:

- ❌ Language models
- ❌ Network services
- ❌ Locale databases
- ❌ Heuristic confidence scores

✅ The same supported input produces the same result on every platform.

---

## 📦 Installation

### 1️⃣ Install from PyPI

Install the latest published release:

```bash
python -m pip install numbr
```

### 2️⃣ Alternative: Install from GitHub

Install the current development version:

```bash
python -m pip install 'numbr @ git+ssh://git@github.com/doydl-technologies/numbr.git'
```

### 📋 Requirements

| Requirement | Details |
|---|---|
| 🐍 Python | Version 3.13 |
| 📦 Runtime dependencies | None |
| 🌐 Network service | Not required for library operations |

**✅ Lightweight by design:** The package has no runtime dependencies.

---

## 🚀 Quick start

Import `numbr`, then choose an operation based on whether you're working with one value, a passage of text, or a collection.

### 🔍 Identify a representation

```python
import numbr

numbr.Type("forty-second")

# "Ordinal Word"
```

### 🔄 Convert between representations

```python
numbr.Cast("forty-second", "Cardinal Number")

# 42

numbr.Cast("1.050", "Cardinal Word")

# "one point zero five zero"
```

### 📖 Extract values from text

```python
numbr.extractNumericValue("She placed 2nd with 1.05 points")

# [2, Decimal("1.05")]
```

### 📍 Extract values with source positions

```python
numbr.extractNumericEntities("She placed 2nd with 1.05 points")

# [NumericMatch(text='2nd', value=2, representation='Ordinal Number', ...),
#  NumericMatch(text='1.05', value=Decimal('1.05'), representation='Decimal Number', ...)]
```

### ✏️ Normalize a sentence

```python
numbr.normalizeNumericText("She placed forty-second with 1.20e3 points")

# "She placed 42nd with 1200 points"
```

### 📚 Convert multiple values

```python
numbr.batchCast(["one", "2", "III"], "Cardinal Number")

# [1, 2, 3]
```

> **💡 Note:** The `Decimal(...)` text shown above is Python's representation of the returned value. You do not need to import `Decimal` for this quick-start example.

---

## 🧰 Choosing the right API

Not sure which function to use? Start here.

| Goal | API | Result |
|---|---|---|
| 🔍 Identify one value | `Type(value)` | A representation name, or `None` |
| 🔄 Convert one value | `Cast(value, target)` | Value in the requested representation |
| 🔢 Extract values | `extractNumericValue(text)` | List of normalized `int` or `Decimal` values |
| 📍 Extract with details | `extractNumericEntities(text)` | `NumericMatch` records with source information |
| ✏️ Rewrite numeric text | `normalizeNumericText(text)` | Text with recognized expressions normalized |
| 🩺 Explain parsing failures | `diagnoseNumeric(value)` | `ParseResult` containing values or diagnostics |
| 📚 Convert multiple inputs | `batchCast(values, target)` | Converted values under the selected error policy |
| 📋 Diagnose multiple inputs | `batchDiagnose(values, target)` | Index-stable `ParseResult` records |

### 🤔 What's the difference?

- **🔄 Conversion:** Operates on one numeric value.
- **🔍 Extraction:** Searches a larger string and returns the numbers it contains.
- **✏️ Normalization:** Searches a larger string and returns rewritten text instead of match records.

---

## 🎯 Exact decimal values

**Precision matters**, especially when working with financial or structured numeric data.

Instead of Python's `float`, decimal parsing returns [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal).

### ✅ Why Decimal?

- Avoids binary floating-point representation errors.
- Preserves meaningful fractional zeros.
- Supports exact decimal arithmetic.

For example, `"1.050"` retains its trailing zero.

### 🐍 Example: Preserve decimal precision

```python
import numbr

value = numbr.Cast("1.050", "Decimal Number")

value

# Decimal("1.050")

numbr.Cast(value, "Cardinal Word")

# "one point zero five zero"
```

**💡 No additional dependency needed:** `Decimal` belongs to Python's standard library.

You only need to import it when constructing decimal values directly or performing decimal arithmetic.

### 💵 Example: Accounting formatting

```python
from decimal import Decimal

import numbr

numbr.decimalToAccounting(Decimal("-1234.50"), currency="$")

# "($1,234.50)"
```

---

## 🔢 Representations

numbr supports eight major numeric representations.

| Representation | Meaning | Examples | `Type` result |
|---|---|---|---|
| 🔢 Cardinal number | Whole-number quantity written in digits | `42`, `"-42"` | `"Cardinal Number"` |
| 🎯 Decimal number | Fixed-point value with fractional digits | `"1.05"`, `Decimal("1.050")` | `"Decimal Number"` |
| 🧪 Scientific number | Coefficient multiplied by a power of ten | `"1.20e3"`, `"-4E-2"` | `"Scientific Number"` |
| 💵 Accounting number | Business notation using parentheses for negative values | `"(1,234.50)"`, `"($50.00)"` | `"Accounting Number"` |
| 🔤 Cardinal word | Quantity written in English | `"forty-two"` | `"Cardinal Word"` |
| 🥈 Ordinal number | Rank written with digits and suffix | `"42nd"` | `"Ordinal Number"` |
| 🏅 Ordinal word | Rank written in English | `"forty-second"` | `"Ordinal Word"` |
| 🏛️ Roman numeral | Value written with Roman symbols | `"XLII"`, `"Ⅳ"` | `"Roman Numeral"` |

### 📖 Understanding word-based decimals

Decimal phrases such as `"one point zero five"` are cardinal-word forms.

Digits after `point` are interpreted individually, preserving precision and trailing zeros.

**⚠️ Important:** English-word parsing is designed for numeric expressions, not unrestricted natural-language interpretation.

Pass surrounding prose to an extraction or normalization API instead of directly to `Type` or `Cast`.

### 🏷️ Accepted representation aliases

`Cast` accepts display names and common aliases, including:

`int`, `decimal`, `scientific`, `accounting`, `cardword`, `ordnum`, and `roman`.

### 🐍 Conversion examples

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

### 📏 Supported ranges

- 🏛️ **Roman numerals:** Canonical values from `1` through `3999`.
- 🔤 **English number conversion:** Integer components with absolute values less than `10**24`.

---

## 🛠️ Public API

### 🔄 General conversion

Two primary functions handle individual numeric expressions.

| Function | Purpose |
|---|---|
| `Type(value)` | Detects the representation or returns `None` |
| `Cast(value, target, *, as_str=False)` | Converts a value to the requested representation |

**⚠️ Error handling:** `Cast` raises `ValueError` when the input or requested conversion is invalid.

Decimal-number conversions return `decimal.Decimal`, avoiding binary floating-point rounding and preserving explicitly supplied fractional zeros.

Non-integral decimals cannot be cast to integer-only cardinal, ordinal, or Roman forms.

### 🧪 Scientific and accounting notation

numbr supports both scientific notation and accounting-style numeric formatting.

**🔬 Scientific notation**

Accepts signed coefficients and exponents, including:

- `.5e1`
- `5.e2`
- `1.20e3`

**💵 Accounting notation**

Uses parentheses to represent negative amounts and accepts supported currency tokens immediately outside or inside the parentheses.

### 🐍 Conversion examples

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

✅ Both representations participate in `Type`, `Cast`, value extraction, and structured extraction.

### 🔎 Structured extraction

Use `extractNumericEntities(text)` to locate every recognized numeric expression in a larger passage.

Each result is an immutable `NumericMatch` record.

### 📋 What each match contains

- 📝 Original `text`
- 🔢 Normalized `value`
- 🏷️ Representation name
- 📍 `start` and `end` offsets
- 📐 Source `span`
- 🥈 `is_ordinal` flag
- ➖ `is_negative` flag

### 🐍 Example: Extract entities and positions

```python
matches = numbr.extractNumericEntities("She placed forty-second with -0.50 points in round XLII.")

matches[0].text, matches[0].value, matches[0].span

# ("forty-second", 42, (11, 23))

matches[1].value

# Decimal("-0.50")

matches[2].representation

# "Roman Numeral"
```

### 🏛️ Roman numeral handling

Canonical Roman numerals are included by default.

However, single-letter ASCII forms such as `I`, `V`, and `X` are excluded because they can be ambiguous in ordinary prose.

**⚙️ Options:**

- `include_single_roman=True` — include single-letter Roman numerals.
- `include_roman=False` — exclude Roman numerals entirely.

### 📝 Whole-text normalization

Use `normalizeNumericText(text, style="digits")` to replace recognized numeric expressions while preserving all surrounding characters.

### 🎨 Available styles

| Style | Behavior |
|---|---|
| 🔢 `style="digits"` | Converts recognized values into digits and retains ordinal suffixes |
| 🔤 `style="words"` | Spells recognized values in English while retaining ordinal meaning |

### 🐍 Example: Normalize complete sentences

```python
text = "She placed forty-second with 1.20e3 points and lost ($1,234.50)."

numbr.normalizeNumericText(text)

# "She placed 42nd with 1200 points and lost -1234.50."

numbr.normalizeNumericText("Ranked 2nd in round Ⅳ", style="words")

# "Ranked second in round four"
```

**📌 Additional behavior**

Roman-numeral options match those available on `extractNumericEntities`.

Values outside the supported English-word range remain unchanged when using the `words` style.

### 🩺 Rich parsing diagnostics

Instead of raising an exception for invalid input, `diagnoseNumeric(value, target=None)` returns an immutable `ParseResult`.

This provides structured information about whether parsing succeeded and why it may have failed.

### ✅ Successful results include

- Normalized or converted value
- Source representation
- Target representation

### ❌ Failed results include

One or more `ParseDiagnostic` objects containing:

- 🏷️ Stable error code
- 📝 Explanatory message
- 📍 Source span
- 🚦 Severity
- 💡 Suggested correction

### 🐍 Example: Diagnose an invalid ordinal

```python
result = numbr.diagnoseNumeric("22st")

result.ok

# False

result.error.code, result.error.span

# ("invalid_ordinal_suffix", (0, 4))

result.error.suggestion

# "Use '22nd'."
```

### 🧰 Supported diagnostic categories

Diagnostic codes distinguish:

- Empty or unsupported input
- Malformed decimals
- Invalid scientific notation
- Invalid accounting notation
- Invalid ordinal suffixes
- Invalid numeric grouping
- Invalid English-number words
- Invalid Roman numerals
- Unknown conversion targets
- Unsupported conversions

**💡 Prefer exceptions?** Call `result.unwrap()` after inspection.

### 📚 Batch conversion

Use `batchCast(values, target)` to apply the same conversion rules to any iterable.

### ⚙️ Error-handling policies

| Policy | Behavior |
|---|---|
| 🛑 `"raise"` | Raises `BatchConversionError` with the failing index and diagnostic result |
| 🟡 `"coerce"` | Retains the input shape and replaces failed positions with `None` |
| ⏭️ `"ignore"` | Omits failed items |

### 🐍 Example: Convert with error handling

```python
numbr.batchCast(["one", "invalid", "III"], "Cardinal Number", errors="coerce")

# [1, None, 3]
```

### 🔍 Example: Diagnose a batch

```python
results = numbr.batchDiagnose(["1e3", "bad", "(2.00)"], "Decimal Number")

[result.ok for result in results]

# [True, False, True]
```

**📌 When to use `batchDiagnose`:** Choose it when every input needs an index-stable structured result, regardless of success or failure.

### 🧩 Parsing and formatting

numbr also exposes lower-level parsing, conversion, and formatting helpers.

| Category | Available functions |
|---|---|
| 🔤 English words | `wordsToInt`, `wordsToDecimal`, `ordinalWordsToInt` |
| 🔢 Numeric strings | `stringToInt`, `stringToDecimal` |
| 🧪 Scientific and accounting | `scientificToDecimal`, `accountingToDecimal` |
| ✏️ Number formatting | `intToWords`, `decimalToWords`, `decimalToScientific`, `decimalToAccounting` |
| 🥈 Ordinals | `intToOrdinalWords`, `ordinalSuffix`, `stripOrdinalSuffix` |
| 🏛️ Roman numerals | `romanToInt`, `romanToWords`, `intToRoman` |
| 🔍 Text extraction | `extractNumericValue`, `extractNumericEntities` |
| 📝 Text normalization | `normalizeNumericText` |
| 🩺 Diagnostics | `diagnoseNumeric`, `batchDiagnose` |
| 📚 Batch operations | `batchCast`, `batchDiagnose` |
| 🧰 Utilities | `insertSep`, `formatDecimal` |

### 🔙 Backward compatibility

Direct cross-representation helpers from earlier releases remain available, including:

- `cardinalWordToOrdinalNum`
- `ordinalNumToCardinalWord`
- Related conversion functions

### 🎯 Decimal formatting behavior

Lower-level parsing functions return `None` for invalid input.

Decimal conversion spells digits after the point individually, preserving zeros.

```python
numbr.intToWords("1.05")

# "one point zero five"
```

---

## 👨‍💻 Development

Want to contribute or work with the source code?

### 1️⃣ Clone the repository

```bash
git clone git@github.com:doydl-technologies/numbr.git
cd numbr
```

### 2️⃣ Create a virtual environment

```bash
python -m venv .venv
```

### 3️⃣ Activate the environment

**Linux / macOS:**

```bash
source .venv/bin/activate
```

**MSYS2 / Windows:**

```bash
source .venv/Scripts/activate
```

### 4️⃣ Install development dependencies

```bash
python -m pip install -e '.[dev]'
```

### 5️⃣ Run tests and quality checks

**🧪 Run the test suite**

```bash
pytest
```

**🔍 Run Ruff**

```bash
ruff check .
```

**📦 Build the distribution**

```bash
python -m build
```

### 📚 Contributor resources

- 🤝 [Contribution guidelines](https://github.com/doydl-technologies/numbr/blob/main/CONTRIBUTING.md)
- 🔐 [Security policy](https://github.com/doydl-technologies/numbr/blob/main/SECURITY.md)
- 🕘 [Release history](https://github.com/doydl-technologies/numbr/blob/main/CHANGELOG.md)

---

## ⚖️ License

Licensed under the [MIT License](https://github.com/doydl-technologies/numbr/blob/main/LICENSE).

---

<p align="center">
  <strong>🔢 numbr</strong>
</p>

<p align="center">
  Built for predictable numeric parsing, extraction, normalization, and conversion.
</p>

<p align="center">
  Powered by <a href="https://doydl.com">DOYDL Technologies</a>
</p>
