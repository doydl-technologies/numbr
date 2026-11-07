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

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

import numbr


def test_extracts_mixed_entities_in_source_order_with_exact_spans():
    text = "He ranked 42nd with twenty-one points and 1.05 seconds."

    entities = numbr.extractNumericEntities(text)

    assert [entity.text for entity in entities] == ["42nd", "twenty-one", "1.05"]
    assert [entity.value for entity in entities] == [42, 21, Decimal("1.05")]
    assert [entity.representation for entity in entities] == [
        "Ordinal Number",
        "Cardinal Word",
        "Decimal Number",
    ]
    assert [text[entity.start : entity.end] for entity in entities] == [
        entity.text for entity in entities
    ]


def test_extracts_signed_word_phrases_and_preserves_decimal_precision():
    text = "Changes were negative one point zero five and minus forty-second."

    entities = numbr.extractNumericEntities(text)

    assert entities[0].text == "negative one point zero five"
    assert entities[0].value == Decimal("-1.05")
    assert entities[0].is_negative is True
    assert entities[0].is_ordinal is False
    assert entities[1].text == "minus forty-second"
    assert entities[1].value == -42
    assert entities[1].is_negative is True
    assert entities[1].is_ordinal is True


def test_extracts_signed_digit_forms_and_negative_zero():
    entities = numbr.extractNumericEntities("Use +12, -0.00, −2.5, and -3rd.")

    assert [entity.value for entity in entities] == [
        12,
        Decimal("-0.00"),
        Decimal("-2.5"),
        -3,
    ]
    assert [entity.is_negative for entity in entities] == [False, True, True, True]


def test_negative_decimal_word_zero_retains_its_sign():
    entity = numbr.extractNumericEntities("negative zero point zero")[0]

    assert entity.value.as_tuple() == Decimal("-0.0").as_tuple()
    assert entity.is_negative is True


def test_extracts_canonical_ascii_and_unicode_roman_numerals():
    entities = numbr.extractNumericEntities("Rounds XLII and Ⅳ were selected.")

    assert [(entity.text, entity.value) for entity in entities] == [("XLII", 42), ("Ⅳ", 4)]
    assert all(entity.representation == "Roman Numeral" for entity in entities)


def test_single_ascii_roman_numerals_are_opt_in():
    text = "I saw V results."

    assert numbr.extractNumericEntities(text) == []
    assert [
        entity.value for entity in numbr.extractNumericEntities(text, include_single_roman=True)
    ] == [1, 5]


def test_roman_extraction_can_be_disabled():
    assert numbr.extractNumericEntities("XLII and Ⅳ", include_roman=False) == []


def test_invalid_numeric_tokens_are_not_partially_extracted():
    assert numbr.extractNumericEntities("IIII, 1,23, and 1.2.3 are invalid.") == []


def test_ordinal_number_is_returned_once_instead_of_as_a_cardinal_prefix():
    entities = numbr.extractNumericEntities("The 42nd entry")

    assert len(entities) == 1
    assert entities[0].text == "42nd"
    assert entities[0].representation == "Ordinal Number"


def test_conjunction_between_distinct_entities_is_not_treated_as_invalid_grammar():
    entities = numbr.extractNumericEntities("negative one and two; first and second")

    assert [(entity.text, entity.value) for entity in entities] == [
        ("negative one", -1),
        ("two", 2),
        ("first", 1),
        ("second", 2),
    ]


@pytest.mark.parametrize("value", [None, 42, Decimal("1.0"), ""])
def test_non_text_and_empty_input_return_no_entities(value):
    assert numbr.extractNumericEntities(value) == []


def test_match_exposes_convenience_properties_and_is_immutable():
    entity = numbr.extractNumericEntities("Value: 12.50")[0]

    assert entity.span == (7, 12)
    assert entity.normalized == Decimal("12.50")
    with pytest.raises(FrozenInstanceError):
        entity.value = Decimal("0")
