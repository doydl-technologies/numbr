# -*- coding: utf-8 -*-

#
# DOYDL's Numeric Parsing & Normalization Engine — numbr
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

import pytest

import numbr


@pytest.mark.parametrize(
    ("words", "expected_number", "expected_ordinal"),
    [
        ("zeroth", 0, "0th"),
        ("first", 1, "1st"),
        ("twenty-first", 21, "21st"),
        ("one hundredth", 100, "100th"),
        ("ten thousandth", 10_000, "10000th"),
        ("negative twenty-first", -21, "-21st"),
    ],
)
def test_ordinal_words_to_int(words, expected_number, expected_ordinal):
    assert numbr.ordinalWordsToInt(words, to_num=True) == expected_number
    assert numbr.ordinalWordsToInt(words) == expected_ordinal


def test_ordinal_round_trip():
    for value in range(-2_000, 2_001):
        words = numbr.intToOrdinalWords(value)
        assert numbr.ordinalWordsToInt(words, to_num=True) == value


@pytest.mark.parametrize("value", [10**21, -(10**23), 10**24 - 1])
def test_large_ordinal_round_trip(value):
    words = numbr.intToOrdinalWords(value)
    assert numbr.ordinalWordsToInt(words, to_num=True) == value


@pytest.mark.parametrize(
    ("value", "suffix"),
    [(1, "st"), (2, "nd"), (3, "rd"), (4, "th"), (11, "th"), (112, "th")],
)
def test_ordinal_suffix(value, suffix):
    assert numbr.ordinalSuffix(value) == suffix
