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
    ("source", "expected"),
    [
        ("1.25e3", Decimal("1.25E+3")),
        ("-4E-2", Decimal("-0.04")),
        ("−3.0e+2", Decimal("-3.0E+2")),
        (".5e1", Decimal("5")),
        ("5.e2", Decimal("5E+2")),
    ],
)
def test_scientific_to_decimal_is_exact(source, expected):
    assert numbr.scientificToDecimal(source) == expected
    assert numbr.stringToDecimal(source) == expected
    assert numbr.Type(source) == "Scientific Number"


@pytest.mark.parametrize(
    "source",
    ["1e", "e3", "1,000e2", "NaN", "Infinity", "1e2.3", "1e3suffix"],
)
def test_scientific_to_decimal_rejects_invalid_notation(source):
    assert numbr.scientificToDecimal(source) is None


def test_decimal_to_scientific_emits_canonical_notation():
    assert numbr.decimalToScientific(Decimal("1230.00")) == "1.23e+3"
    assert numbr.decimalToScientific(Decimal("-0.00")) == "-0e+0"
    assert numbr.decimalToScientific("0.00120", uppercase=True) == "1.2E-3"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("(1,234.50)", Decimal("-1234.50")),
        ("($1,234.50)", Decimal("-1234.50")),
        ("$ (1,234.50)", Decimal("-1234.50")),
        ("(CHF 12.50)", Decimal("-12.50")),
    ],
)
def test_accounting_to_decimal_supports_currency_placement(source, expected):
    assert numbr.accountingToDecimal(source) == expected
    assert numbr.stringToDecimal(source) == expected
    assert numbr.Type(source) == "Accounting Number"


def test_accounting_negative_zero_retains_its_sign():
    result = numbr.accountingToDecimal("(0.00)")

    assert result.as_tuple() == Decimal("-0.00").as_tuple()


@pytest.mark.parametrize(
    "source",
    ["1,234.50", "(-1.00)", "($€1.00)", "(1,23.00)", "(1.00"],
)
def test_accounting_to_decimal_rejects_invalid_notation(source):
    assert numbr.accountingToDecimal(source) is None


def test_decimal_to_accounting_preserves_scale_and_supports_currency():
    assert numbr.decimalToAccounting(Decimal("-1234.50"), currency="$") == "($1,234.50)"
    assert numbr.decimalToAccounting(Decimal("1234.50"), currency="$") == "$1,234.50"
    assert numbr.decimalToAccounting(Decimal("-1234.50"), grouping=False) == "(1234.50)"
    assert numbr.Type(numbr.decimalToAccounting(1200)) == "Cardinal Number"


def test_cast_supports_scientific_and_accounting_representations():
    assert numbr.Cast("1.2e3", "Cardinal Number") == 1200
    assert numbr.Cast("(1,200.00)", "Scientific Number") == "-1.2e+3"
    assert numbr.Cast("1.2e3", "Accounting Number") == "1,200"
    assert numbr.Cast("($1,234.50)", "Cardinal Word") == (
        "negative one thousand two hundred thirty-four point five zero"
    )


def test_structured_extraction_recognizes_new_notations_without_partial_matches():
    text = "Values: 1.20e3 and ($1,234.50)."

    entities = numbr.extractNumericEntities(text)

    assert [entity.text for entity in entities] == ["1.20e3", "($1,234.50)"]
    assert [entity.value for entity in entities] == [
        Decimal("1.20E+3"),
        Decimal("-1234.50"),
    ]
    assert [entity.representation for entity in entities] == [
        "Scientific Number",
        "Accounting Number",
    ]
    assert all(text[entity.start : entity.end] == entity.text for entity in entities)


def test_legacy_value_extraction_supports_new_notations():
    assert numbr.extractNumericValue("Values: 1.20e3 and ($1,234.50).") == [
        Decimal("1.20E+3"),
        Decimal("-1234.50"),
    ]


def test_whole_text_normalization_to_digits_preserves_other_text():
    text = "She placed forty-second with 1.20e3 points and lost ($1,234.50) in round XLII."

    result = numbr.normalizeNumericText(text)

    assert result == "She placed 42nd with 1200 points and lost -1234.50 in round 42."
    assert numbr.normalizeNumericText(result) == result


def test_whole_text_normalization_to_words_preserves_ordinal_semantics():
    text = "Ranked 2nd with -0.50 points in round Ⅳ."

    assert numbr.normalizeNumericText(text, style="words") == (
        "Ranked second with negative zero point five zero points in round four."
    )


def test_normalization_respects_roman_options():
    assert numbr.normalizeNumericText("I saw V results.") == "I saw V results."
    assert numbr.normalizeNumericText("I saw V results.", include_single_roman=True) == (
        "1 saw 5 results."
    )
    assert numbr.normalizeNumericText("Round XLII", include_roman=False) == "Round XLII"


def test_word_normalization_leaves_values_outside_the_word_range_unchanged():
    assert numbr.normalizeNumericText("Value 1e24", style="words") == "Value 1e24"


def test_normalization_validates_arguments():
    with pytest.raises(TypeError, match="s must be a string"):
        numbr.normalizeNumericText(42)
    with pytest.raises(ValueError, match="style"):
        numbr.normalizeNumericText("one", style="roman")
