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

import pytest

import numbr


@pytest.mark.parametrize(
    ("roman", "expected"),
    [("IV", 4), ("iv", 4), ("Ⅳ", 4), ("MCMXCIV", 1994), ("MMMCMXCIX", 3999)],
)
def test_roman_to_int(roman, expected):
    assert numbr.romanToInt(roman) == expected


@pytest.mark.parametrize("invalid", ["", "IIII", "IM", "MMMM", "VX"])
def test_rejects_noncanonical_roman_numerals(invalid):
    assert numbr.romanToInt(invalid) is None


def test_int_to_roman():
    assert numbr.intToRoman(1994) == "MCMXCIV"
    assert numbr.intToRoman(0) is None
    assert numbr.intToRoman(4000) is None


def test_roman_is_a_first_class_representation():
    assert numbr.Type("Ⅳ") == "Roman Numeral"
    assert numbr.Cast("Ⅳ", "Ordinal Word") == "fourth"
    assert numbr.Cast(1994, "Roman Numeral") == "MCMXCIV"
