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
    ("words", "expected"),
    [
        ("zero", 0),
        ("forty-two", 42),
        ("one hundred and five", 105),
        ("negative nine hundred ninety-nine", -999),
        ("one sextillion", 10**21),
        ("nine hundred ninety-nine sextillion", 999 * 10**21),
    ],
)
def test_words_to_int(words, expected):
    assert numbr.wordsToInt(words) == expected


@pytest.mark.parametrize(
    "invalid",
    [
        "one hundred hundred",
        "one thousand one million",
        "zero one",
        "and five",
        "five and",
        "one and five",
        "twenty thirteen",
    ],
)
def test_words_to_int_rejects_invalid_grammar(invalid):
    assert numbr.wordsToInt(invalid) is None


def test_cardinal_round_trip():
    for value in range(-2_000, 2_001):
        assert numbr.wordsToInt(numbr.intToWords(value)) == value


@pytest.mark.parametrize("value", [10**21, 10**23, 10**24 - 1])
def test_large_value_round_trip(value):
    assert numbr.wordsToInt(numbr.intToWords(value)) == value


def test_values_outside_documented_domain_are_rejected():
    assert numbr.intToWords(10**24) is None
    assert numbr.intToWords(-(10**24)) is None


def test_decimal_digits_are_preserved():
    assert numbr.intToWords("1.05") == "one point zero five"


@pytest.mark.parametrize(
    ("value", "expected"),
    [("1,234", 1234), ("-42", -42), ("21st", 21), ("-22nd", -22)],
)
def test_string_to_int(value, expected):
    assert numbr.stringToInt(value) == expected


def test_string_to_int_validates_ordinal_suffix():
    assert numbr.stringToInt("1th") is None
    assert numbr.stringToInt("12nd") is None
