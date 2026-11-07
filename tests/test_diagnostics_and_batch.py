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


@pytest.mark.parametrize(
    ("source", "representation", "expected"),
    [
        ("twenty-one", "Cardinal Word", 21),
        ("42nd", "Ordinal Number", 42),
        ("1.20e3", "Scientific Number", Decimal("1.20E+3")),
        ("($1,234.50)", "Accounting Number", Decimal("-1234.50")),
        ("XLII", "Roman Numeral", 42),
    ],
)
def test_diagnose_numeric_returns_normalized_values(source, representation, expected):
    result = numbr.diagnoseNumeric(source)

    assert result.ok is True
    assert result.value == expected
    assert result.source_representation == representation
    assert result.representation == representation
    assert result.diagnostics == ()
    assert result.unwrap() == expected


def test_diagnose_numeric_reports_successful_target_conversion():
    result = numbr.diagnoseNumeric("1.2e3", "Accounting Number")

    assert result.ok is True
    assert result.value == "1,200"
    assert result.source_representation == "Scientific Number"
    assert result.target_representation == "Accounting Number"
    assert result.representation == "Accounting Number"


@pytest.mark.parametrize(
    ("source", "code"),
    [
        ("", "empty_input"),
        ("1e", "invalid_scientific_notation"),
        ("(1,234.50", "invalid_accounting_notation"),
        ("22st", "invalid_ordinal_suffix"),
        ("1,23", "invalid_grouping"),
        ("1.2.3", "invalid_decimal_notation"),
        ("IIII", "invalid_roman_numeral"),
        ("one two", "invalid_number_words"),
        ("@", "unrecognized_numeric_input"),
    ],
)
def test_diagnose_numeric_uses_stable_error_codes(source, code):
    result = numbr.diagnoseNumeric(source)

    assert result.ok is False
    assert result.value is None
    assert result.error.code == code
    assert result.error.severity == "error"
    assert result.error.suggestion
    with pytest.raises(ValueError, match=result.error.message):
        result.unwrap()


def test_diagnostic_span_excludes_surrounding_whitespace():
    result = numbr.diagnoseNumeric("  1,23  ")

    assert result.error.span == (2, 6)
    assert result.source[result.error.start : result.error.end] == "1,23"


def test_ordinal_diagnostic_suggests_the_correct_suffix():
    result = numbr.diagnoseNumeric("11st")

    assert result.error.code == "invalid_ordinal_suffix"
    assert result.error.suggestion == "Use '11th'."


@pytest.mark.parametrize(
    ("source", "code"),
    [
        (True, "unsupported_type"),
        (object(), "unsupported_type"),
        (Decimal("NaN"), "non_finite_number"),
        (float("inf"), "non_finite_number"),
    ],
)
def test_diagnostics_cover_invalid_non_text_values(source, code):
    assert numbr.diagnoseNumeric(source).error.code == code


def test_diagnostics_distinguish_unknown_targets_and_unsupported_conversions():
    unknown = numbr.diagnoseNumeric("one", "not-a-representation")
    unsupported = numbr.diagnoseNumeric("1.5", "Roman Numeral")

    assert unknown.error.code == "unknown_target"
    assert unsupported.error.code == "unsupported_conversion"
    assert unsupported.source_representation == "Decimal Number"
    assert unsupported.target_representation == "Roman Numeral"


def test_diagnostic_results_are_immutable():
    result = numbr.diagnoseNumeric("1,23")

    with pytest.raises(FrozenInstanceError):
        result.value = 123
    with pytest.raises(FrozenInstanceError):
        result.error.code = "changed"


def test_batch_cast_converts_mixed_representations_consistently():
    assert numbr.batchCast(["one", "2", "III", "3e0"], "Cardinal Number") == [1, 2, 3, 3]
    assert numbr.batchCast(["one", 2, "III"], "Decimal Number") == [
        Decimal("1"),
        Decimal("2"),
        Decimal("3"),
    ]


def test_batch_cast_supports_generators_and_string_results():
    values = (value for value in ["one", "2", "III"])

    assert numbr.batchCast(values, "Cardinal Number", as_str=True) == ["1", "2", "3"]


def test_batch_cast_error_policies_preserve_their_documented_shape():
    values = ["one", "invalid", "III"]

    assert numbr.batchCast(values, "Cardinal Number", errors="coerce") == [1, None, 3]
    assert numbr.batchCast(values, "Cardinal Number", errors="ignore") == [1, 3]


def test_batch_cast_raise_policy_exposes_index_and_diagnostic_result():
    with pytest.raises(numbr.BatchConversionError) as exc_info:
        numbr.batchCast(["one", "invalid", "III"], "Cardinal Number")

    error = exc_info.value
    assert error.index == 1
    assert error.result.source == "invalid"
    assert error.result.error.code == "invalid_number_words"
    assert str(error).startswith("Batch item 1:")


def test_batch_diagnose_returns_one_result_per_input():
    results = numbr.batchDiagnose(["1e3", "bad", "(2.00)"], "Decimal Number")

    assert len(results) == 3
    assert [result.ok for result in results] == [True, False, True]
    assert results[0].value == Decimal("1E+3")
    assert results[1].error.code == "invalid_number_words"
    assert results[2].value == Decimal("-2.00")


def test_batch_helpers_validate_container_and_error_policy():
    with pytest.raises(TypeError, match="not a string"):
        numbr.batchDiagnose("one")
    with pytest.raises(TypeError, match="iterable"):
        numbr.batchDiagnose(42)
    with pytest.raises(ValueError, match="errors"):
        numbr.batchCast(["one"], "Cardinal Number", errors="replace")
