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

import numbr


def test_mixed_extraction_preserves_source_order():
    text = "He scored twenty-one of 34 attempts and finished third."
    assert numbr.extractNumericValue(text) == [21, 34, 3]


def test_first_extraction_uses_source_order():
    assert numbr.extractNumericValue("twenty-one of 34", allnum=False) == 21


def test_single_extraction_returns_an_integer():
    assert numbr.extractNumericValue("There were 42 entries") == 42


def test_no_values_returns_none():
    assert numbr.extractNumericValue("nothing to parse") is None
