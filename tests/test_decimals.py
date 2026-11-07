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

from decimal import Decimal

import pytest

import numbr


@pytest.mark.parametrize(
    "value",
    ["1.05", ".75", "-0.004", "+12.5", "1,234.50", Decimal("2.00"), 1.25],
)
def test_type_detects_decimal_numbers(value):
    assert numbr.Type(value) == "Decimal Number"


def test_type_treats_decimal_words_as_cardinal_words():
    assert numbr.Type("one point zero five") == "Cardinal Word"


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        ("one point zero five", Decimal("1.05")),
        ("point seven five", Decimal("0.75")),
        ("negative zero point zero four", Decimal("-0.04")),
        ("minus twelve point seven", Decimal("-12.7")),
        ("forty-two", Decimal("42")),
    ],
)
def test_words_to_decimal(words, expected):
    assert numbr.wordsToDecimal(words) == expected


@pytest.mark.parametrize(
    "invalid",
    [
        "one point",
        "one point twenty",
        "one point five point six",
        "negative minus one point five",
        "point",
        "not a number",
    ],
)
def test_words_to_decimal_rejects_invalid_grammar(invalid):
    assert numbr.wordsToDecimal(invalid) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1,234.50", Decimal("1234.50")),
        (".75", Decimal("0.75")),
        ("5.", Decimal("5")),
        ("−0.004", Decimal("-0.004")),
    ],
)
def test_string_to_decimal(value, expected):
    assert numbr.stringToDecimal(value) == expected


@pytest.mark.parametrize("invalid", ["1,23.4", "1.2.3", "NaN", "Infinity", True])
def test_string_to_decimal_rejects_invalid_input(invalid):
    assert numbr.stringToDecimal(invalid) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("1.050"), "one point zero five zero"),
        (Decimal("-0.04"), "negative zero point zero four"),
        ("1234.50", "one thousand two hundred thirty-four point five zero"),
    ],
)
def test_decimal_to_words_preserves_fractional_digits(value, expected):
    assert numbr.decimalToWords(value) == expected


def test_decimal_to_words_rejects_values_outside_documented_domain():
    assert numbr.decimalToWords(Decimal("1e24")) is None


@pytest.mark.parametrize("value", [Decimal("1.050"), Decimal("-12.0070"), Decimal("0.0")])
def test_decimal_word_round_trip_preserves_sign_and_exponent(value):
    result = numbr.wordsToDecimal(numbr.decimalToWords(value))
    assert result.as_tuple() == value.as_tuple()


def test_cast_converts_between_decimal_numbers_and_words():
    assert numbr.Cast("one point zero five", "Decimal Number") == Decimal("1.05")
    assert numbr.Cast("1.05", "Cardinal Word") == "one point zero five"
    assert numbr.Cast(42, "Decimal Number") == Decimal("42")


def test_cast_normalizes_decimal_numbers_and_supports_aliases():
    assert numbr.Cast("1.050", "decimal") == Decimal("1.050")
    assert numbr.Cast("1.050", "decimal", as_str=True) == "1.050"


def test_integral_decimal_can_convert_to_integer_only_representations():
    assert numbr.Cast(Decimal("2.0"), "Cardinal Number") == 2
    assert numbr.Cast(Decimal("2.0"), "Ordinal Number") == "2nd"
    assert numbr.Cast(Decimal("4.0"), "Roman Numeral") == "IV"


@pytest.mark.parametrize("target", ["Cardinal Number", "Ordinal Number", "Roman Numeral"])
def test_fractional_decimal_rejects_integer_only_targets(target):
    with pytest.raises(ValueError):
        numbr.Cast(Decimal("2.5"), target)


def test_decimal_extraction_preserves_source_order_and_exact_values():
    text = "The values were 1.05, two point five, and 3.0."
    assert numbr.extractNumericValue(text) == [Decimal("1.05"), Decimal("2.5"), Decimal("3.0")]


def test_integer_extraction_remains_integer_typed():
    assert numbr.extractNumericValue("The values were 1 and two") == [1, 2]
