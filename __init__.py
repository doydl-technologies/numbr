# -*- coding: utf-8 -*-

#
# DOYDL's Symbolic Integer Representation Engine — numbr
#
# The `numbr` module implements a formalized system for parsing, classifying,
# and transforming symbolic representations of integers. Designed to support
# natural language processing (NLP) pipelines, knowledge extraction, and
# symbolic reasoning, it provides a deterministic interface for converting
# between cardinal words, ordinal phrases, Roman numerals, and standard digit
# forms.
#
# All conversions are unambiguous and invertible over ℤ ∩ [–10²⁴, 10²⁴), with
# parsing grammars tailored to the structure and semantics of English number
# words. This system is well-suited for use in contexts where numeric meaning
# must be inferred from or rendered into language — such as automated
# annotation, question answering, legal text processing, and mathematical dialogue.
#
# Copyright (c) 2024 by DOYDL Technologies. All rights reserved.
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

"""
A lightweight NLP-focused Python toolkit for recognising, 
parsing, and transforming numbers expressed in natural-language 
or symbolic form.

This module formalizes and operationalizes the core types of numerical representation
encountered in mathematical language, computational linguistics, and symbolic parsing.
It establishes precise, invertible mappings between various integer representations,
with an emphasis on consistency, mathematical clarity, and linguistic correctness.

Supported Representations:
    • Cardinal Number     — digit form (e.g., 4)
    • Cardinal Word       — English word form (e.g., "four")
    • Ordinal Number      — ordinal numeral (e.g., "4th")
    • Ordinal Word        — ordinal word form (e.g., "fourth")
    • Roman Numeral       — Latin script (e.g., "IV")

This library is intended to be used in contexts where exact treatment of numerals
and their semantic roles is critical — such as data normalization, legal or
scientific text analysis, symbolic reasoning engines, and intelligent voice agents.
All conversions are lossless and deterministic for the domain of integers
|n| < 10²⁴ (quintillions), a practical bound for most real-world applications.

──────────────────────────────────────────────────────────────────────────────
Mathematical Formalism
──────────────────────────────────────────────────────────────────────────────
Let Σ be the set of input tokens (strings) and ℤ be the set of integers.

Each parser ρ: Σ → ℤ maps a symbolic or lexical representation to its numeric
value. The inverse formatter σ: ℤ → Σ maps integers to a canonical string
representation, consistent with English syntactic rules.

For example:

    • ρ("fourth") = 4          — ordinalWordsToInt
    • σ(4) = "fourth"          — intToOrdinalWords

    • ρ("two hundred") = 200   — wordsToInt
    • σ(200) = "two hundred"   — intToWords

Suffix selection for ordinal numerals adheres to linguistic rules:

    • suffix(n) = "th" if n mod 100 ∈ {11,12,13}
      otherwise suffix(n) = "st", "nd", or "rd" according to n mod 10

All transformation functions conform to a uniform model: they either produce
a well-defined result for valid input or raise `ValueError` for invalid input,
depending on context.

──────────────────────────────────────────────────────────────────────────────
API Overview
──────────────────────────────────────────────────────────────────────────────
Core Converters:
    wordsToInt(s: str)               → int
    ordinalWordsToInt(s: str)        → int
    stringToInt(s: str)              → int
    romanToInt(s: str)               → int
    romanToWords(s: str)             → str
    intToWords(n: int)               → str
    intToOrdinalWords(n: int)        → str
    ordinalSuffix(n: int)            → str
    stripOrdinalSuffix(s: str)       → tuple[str, str]
    insertSep(n, sep=',')            → str
    formatDecimal(n, place=5)        → str
    extractNumericValue(s: str)      → list[int] | int | None

Cross-Type Mappings:
    - All canonical conversions between:
        {Cardinal Number, Cardinal Word, Ordinal Number, Ordinal Word}
    - Example:
        cardinalWordToOrdinalNum("twenty-one") → "21st"
        ordinalNumToCardinalWord("3rd")        → "three"

Unified Interface:
    Type(value: str|int)             → str
        Returns the detected representation of the input.
        → One of: "Cardinal Word", "Cardinal Number",
                  "Ordinal Word", "Ordinal Number"

    Cast(value, target: str, *, as_str=False) → int | str
        Converts the input to a specified numeric representation.
        Valid targets match those returned by `Type()`.

──────────────────────────────────────────────────────────────────────────────
Examples
──────────────────────────────────────────────────────────────────────────────
    Type("seventh")                  → "Ordinal Word"
    Cast("seventh", "Cardinal Number") → 7
    Cast("21", "Ordinal Word")       → "twenty-first"
    Cast(5, "Ordinal Number")        → "5th"
    Cast("fifth", "Cardinal Word")   → "five"

    wordsToInt("one thousand and four") → 1004
    ordinalWordsToInt("thirtieth")      → 30
    intToWords(42)                      → "forty-two"
    intToOrdinalWords(42)               → "forty-second"

──────────────────────────────────────────────────────────────────────────────
Design Considerations
──────────────────────────────────────────────────────────────────────────────
• All spelling adheres to conventional American English.
• “and” is permitted but ignored in number words (e.g., "one hundred and ten").
• Hyphenation is parsed but not required ("twenty-one" = "twenty one").
• Roman numeral support is limited to the standard range (1–3999), validated
  against canonical ordering rules (e.g., "IM" is not valid for 999).

Internally, this module separates parsing from formatting to allow each
conversion to be independently extended or overridden.

──────────────────────────────────────────────────────────────────────────────
Limitations
──────────────────────────────────────────────────────────────────────────────
• Does not currently support fractional, decimal, or scientific notation.
• Only integer-valued representations are permitted.
• No support for non-English linguistic forms or pluralization.

──────────────────────────────────────────────────────────────────────────────
Performance
──────────────────────────────────────────────────────────────────────────────
All core operations are O(L) in the length of the input string, with low
constant factors. No recursion or deep grammars are used. Designed to be
efficient in batch-processing pipelines and real-time applications.

──────────────────────────────────────────────────────────────────────────────
"""

from . import engine as __engine

__all__ = [
    # "replaceNumericValue",    
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
]

# Reference functions using __engine alias
# replaceNumericValue = __engine.replaceNumericValue
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
formatDecimal = __engine.formatDecimal
insertSep = __engine.insertSep
cardinalWordToCardinalNum = __engine.cardinalWordToCardinalNum
cardinalWordToOrdinalWord    = __engine.cardinalWordToOrdinalWord
cardinalWordToOrdinalNum  = __engine.cardinalWordToOrdinalNum
cardinalNumToCardinalWord   = __engine.cardinalNumToCardinalWord
cardinalNumToOrdinalWord    = __engine.cardinalNumToOrdinalWord
cardinalNumToOrdinalNum  = __engine.cardinalNumToOrdinalNum
ordinalWordToCardinalWord   = __engine.ordinalWordToCardinalWord
ordinalWordToCardinalNum = __engine.ordinalWordToCardinalNum
ordinalWordToOrdinalNum  = __engine.ordinalWordToOrdinalNum
ordinalNumToCardinalWord   = __engine.ordinalNumToCardinalWord
ordinalNumToCardinalNum = __engine.ordinalNumToCardinalNum
ordinalNumToOrdinalWord    = __engine.ordinalNumToOrdinalWord
Type    = __engine.Type
Cast    = __engine.Cast

del engine
