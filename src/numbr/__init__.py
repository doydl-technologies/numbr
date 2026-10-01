# -*- coding: utf-8 -*-

#
# doydl's Numeric Parsing & Normalization Engine — numbr
#
# The `numbr` module is a deterministic engine for parsing, classifying, converting, and
# normalizing numeric expressions across natural and symbolic language contexts — built for NLP
# workflows, numeric extraction, and consistent representation conversion.
#
# Designed with formal grammatical rigor, `numbr` interprets expressions like “twenty-one,”
# “42nd,” and “Ⅳ” — handling cardinal and ordinal words, decimal numerals, Roman numerals, and
# mixed numeric references with predictable validation.
#
# The engine combines structured tokenization, symbolic transformation, and rule-based semantic
# conversion to support precision across tasks such as entity recognition, information extraction,
# and numeric normalization in noisy or informal text.
#
# It guarantees deterministic, transparent, and cross-platform-consistent conversions within the
# documented numeric ranges while preserving NLP-grade flexibility for English-language number
# constructions.
#
# Whether embedded in intelligent agents, ETL pipelines, or legal/medical NLP systems, `numbr` brings
# clarity and structure to numeric meaning — bridging symbolic notation with real-world language.
#
# Copyright (c) 2024 by doydl technologies. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""Parse and convert cardinal, ordinal, digit, and Roman numeral forms.

English integer conversions support values whose absolute value is less than
``10**24``. Roman numeral conversions use canonical notation from 1 through
3999. Lower-level conversion functions return ``None`` for invalid input;
``Cast`` raises ``ValueError`` when detection or conversion fails.
"""

from importlib.metadata import version as _distribution_version

from . import engine as __engine

__version__ = _distribution_version("numbr")

__all__ = [
    "wordsToInt",
    "ordinalSuffix",
    "intToWords",
    "intToOrdinalWords",
    "stripOrdinalSuffix",
    "ordinalWordsToInt",
    "stringToInt",
    "extractNumericValue",
    "romanToWords",
    "romanToInt",
    "intToRoman",
    "formatDecimal",
    "insertSep",
    "cardinalWordToCardinalNum",
    "cardinalWordToOrdinalWord",
    "cardinalWordToOrdinalNum",
    "cardinalNumToCardinalWord",
    "cardinalNumToOrdinalWord",
    "cardinalNumToOrdinalNum",
    "ordinalWordToCardinalWord",
    "ordinalWordToCardinalNum",
    "ordinalWordToOrdinalNum",
    "ordinalNumToCardinalWord",
    "ordinalNumToCardinalNum",
    "ordinalNumToOrdinalWord",
    "Type",
    "Cast",
    "__version__",
]

wordsToInt = __engine.wordsToInt
ordinalSuffix = __engine.ordinalSuffix
intToWords = __engine.intToWords
intToOrdinalWords = __engine.intToOrdinalWords
stripOrdinalSuffix = __engine.stripOrdinalSuffix
ordinalWordsToInt = __engine.ordinalWordsToInt
stringToInt = __engine.stringToInt
extractNumericValue = __engine.extractNumericValue
romanToWords = __engine.romanToWords
romanToInt = __engine.romanToInt
intToRoman = __engine.intToRoman
formatDecimal = __engine.formatDecimal
insertSep = __engine.insertSep
cardinalWordToCardinalNum = __engine.cardinalWordToCardinalNum
cardinalWordToOrdinalWord = __engine.cardinalWordToOrdinalWord
cardinalWordToOrdinalNum = __engine.cardinalWordToOrdinalNum
cardinalNumToCardinalWord = __engine.cardinalNumToCardinalWord
cardinalNumToOrdinalWord = __engine.cardinalNumToOrdinalWord
cardinalNumToOrdinalNum = __engine.cardinalNumToOrdinalNum
ordinalWordToCardinalWord = __engine.ordinalWordToCardinalWord
ordinalWordToCardinalNum = __engine.ordinalWordToCardinalNum
ordinalWordToOrdinalNum = __engine.ordinalWordToOrdinalNum
ordinalNumToCardinalWord = __engine.ordinalNumToCardinalWord
ordinalNumToCardinalNum = __engine.ordinalNumToCardinalNum
ordinalNumToOrdinalWord = __engine.ordinalNumToOrdinalWord
Type = __engine.Type
Cast = __engine.Cast

del __engine
del _distribution_version
