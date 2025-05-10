
---

<div align="center">

# 🌟 **numbr** 🌟

> **It handles everything from *“forty-two”* → `42` to *“Ⅳ”* → *“fourth”* in a single call.**

</div>


**A lightweight NLP-focused Python toolkit for recognising, parsing, and transforming numbers expressed in natural-language or symbolic form.**  



[![PyPI Downloads](https://static.pepy.tech/badge/numbr)](https://pepy.tech/projects/numbr)
![Language](https://img.shields.io/badge/language-python-blue)
![License](https://img.shields.io/github/license/cedricmoorejr/numbr)
![PyPI](https://img.shields.io/pypi/v/numbr)
[![Engineered by DOYDL Technologies](https://img.shields.io/badge/Engineered%20by-DOYDL%20Technologies-blue)](https://doydl.com)


---

## ✨ Key capabilities
| Task | Example in | Example out | Function |
|------|------------|-------------|-----------|
| Spell-out → digits | `"one hundred sixty-seven"` | `167` | `wordsToInt` |
| Digits → words | `19007` | `"nineteen thousand seven"` | `intToWords` |
| Any form → **type detection** | `"3rd"` | `"Ordinal Number"` | `Type` |
| Cross-form **casting** | `"third"` → `"3"` | `"third"` | `Cast("third", "Cardinal Number")` |
| Roman → integer | `"MCMXCIV"` | `1994` | `romanToInt` |
| Batch extraction | `"He scored twenty-one of 34 attempts"` | `[21, 34]` | `extractNumericValue` |

*(full API listed below)*

---

## 🔧 Installation
```bash
pip install numbr     
# or install from source
pip install git+https://github.com/cedricmoorejr/numbr.git
```

---

## 🚀 Quick start
```python
import numbr

numbr.Type("forty-ninth")
# → 'Ordinal Word'

numbr.Cast("forty-ninth", target="Ordinal Number")
# → '49th'

numbr.Cast(512, target="Ordinal Word")
# → 'five hundred twelve th'
```

---

## 🧰 Public API Overview

`numbr` exposes a clean, top-level API designed for simplicity and readability.  
All functions listed below are available directly via:

```python
import numbr

numbr.Type("twenty-first")
numbr.Cast("Ⅳ", target="Ordinal Word")
```

No internal modules need to be accessed directly — everything is exposed at the package root.

---

### 1. High-Level Helpers

| Helper | Purpose |
|--------|---------|
| **`Type(value)`** | Detect and return the representation category of `value` — e.g., `"Cardinal Word"`, `"Ordinal Number"`, etc. |
| **`Cast(value, target, *, as_str=False)`** | Convert `value` to a target representation and optionally return it as a string. |

---

### 2. Core Conversion Functions

These functions handle numeric parsing, word formatting, Roman numeral conversion, and formatting:

- `wordsToInt`, `ordinalWordsToInt`, `stringToInt`  
- `intToWords`, `intToOrdinalWords`  
- `ordinalSuffix`, `stripOrdinalSuffix`  
- `romanToInt`, `romanToWords`  
- `insertSep`, `formatDecimal`, `extractNumericValue`  

---

### 3. Cross-Type Shorthands

These helpers provide direct one-step conversions between common forms:

- `cardinalWordToOrdinalNum`
- `ordinalNumToCardinalWord`
- `ordinalWordToCardinalNum`
- ...and many more.

Use these when you know the source and target types and want to avoid an intermediate call to `Cast`.

---

## 📝 Roadmap
- Locale & language plugins (FR, DE…)
- Currency-aware formatting
- CLI utility

---

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Contributing
Issues, pull-requests and feature ideas are very welcome to improve `numbr`!  
Clone the repo, create a branch, add tests, and open a PR.

---

### Happy number-crunching!
