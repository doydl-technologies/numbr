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

"""Parsing, conversion, extraction, normalization, and diagnostic operations.

Parsing is based on surface syntax rather than contextual inference. Accepted
inputs map to deterministic integer or exact decimal values. Formatting emits
canonical English, decimal, scientific, accounting, ordinal, or Roman forms
within their documented ranges.
"""

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from functools import WRAPPER_ASSIGNMENTS, reduce, update_wrapper
from typing import Dict, List, Literal, Optional, Tuple, Union

Rep = Literal[
    "CardinalWord",
    "CardinalNumber",
    "DecimalNumber",
    "ScientificNumber",
    "AccountingNumber",
    "OrdinalWord",
    "OrdinalNumber",
    "RomanNumeral",
]
NumLike = Union[int, float, Decimal, str]
NumericValue = Union[int, Decimal]


@dataclass(frozen=True)
class NumericMatch:
    """A normalized numeric expression located in source text."""

    text: str
    value: NumericValue
    representation: str
    start: int
    end: int
    is_ordinal: bool
    is_negative: bool

    @property
    def span(self) -> Tuple[int, int]:
        """Return the half-open source span for this match."""
        return (self.start, self.end)

    @property
    def normalized(self) -> NumericValue:
        """Return the normalized numeric value."""
        return self.value


@dataclass(frozen=True)
class ParseDiagnostic:
    """A machine-readable explanation of a parsing or conversion failure."""

    code: str
    message: str
    start: int
    end: int
    suggestion: Optional[str] = None
    severity: str = "error"

    @property
    def span(self) -> Tuple[int, int]:
        """Return the half-open source span associated with the diagnostic."""
        return (self.start, self.end)


@dataclass(frozen=True)
class ParseResult:
    """The normalized outcome and diagnostics for one numeric input."""

    source: object
    value: object
    source_representation: Optional[str]
    target_representation: Optional[str]
    diagnostics: Tuple[ParseDiagnostic, ...] = ()

    @property
    def ok(self) -> bool:
        """Return whether this result has no diagnostics."""
        return not self.diagnostics

    @property
    def representation(self) -> Optional[str]:
        """Return the output representation, or the detected source representation."""
        return self.target_representation or self.source_representation

    @property
    def error(self) -> Optional[ParseDiagnostic]:
        """Return the first diagnostic, or None when none are present."""
        return self.diagnostics[0] if self.diagnostics else None

    def unwrap(self):
        """Return the parsed value or raise ``ValueError`` with its diagnostic."""
        if self.error is not None:
            raise ValueError(self.error.message)
        return self.value


class BatchConversionError(ValueError):
    """Raised when a batch item cannot be parsed or converted."""

    def __init__(self, index: int, result: ParseResult):
        self.index = index
        self.result = result
        diagnostic = result.error
        message = diagnostic.message if diagnostic is not None else "Conversion failed"
        super().__init__(f"Batch item {index}: {message}")


_MAX_ABS_VALUE = 10**24

# Constants and compiled patterns

# Matches cardinal, ordinal, and decimal-point word tokens.
_NUM_ORDINAL_WRDS_RE = (
    r"zero|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
    r"hundred|thousand|million|billion|trillion|quadrillion|quintillion|sextillion|"
    r"first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
    r"eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|"
    r"eighteenth|nineteenth|twentieth|thirtieth|fortieth|fiftieth|sixtieth|"
    r"seventieth|eightieth|ninetieth|hundredth|thousandth|millionth|billionth|"
    r"trillionth|quadrillionth|quintillionth|sextillionth|zeroth|point"
)
# Matches complete number phrases, including hyphenation and optional "and".
_NUM_WORDS_RE = (
    r"\b(?:"
    + _NUM_ORDINAL_WRDS_RE
    + r")(?:[-\s]+(?:and[-\s]+)?(?:"
    + _NUM_ORDINAL_WRDS_RE
    + r"))*\b"
)

_UNIT_DIGITS_WORDS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

_TENS_MULTIPLES_WORDS = [
    "ten",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
]

_TEEN_NUMERALS_WORDS = [
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]

_DECIMAL_DIGIT_WORDS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
)

_ORDINAL_MAPPING = {
    "zeroth": 0,
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
    "fourteenth": 14,
    "fifteenth": 15,
    "sixteenth": 16,
    "seventeenth": 17,
    "eighteenth": 18,
    "nineteenth": 19,
    "twentieth": 20,
    "thirtieth": 30,
    "fortieth": 40,
    "fiftieth": 50,
    "sixtieth": 60,
    "seventieth": 70,
    "eightieth": 80,
    "ninetieth": 90,
    "hundredth": 100,
    "thousandth": 1000,
    "millionth": 1000000,
    "billionth": 1000000000,
    "trillionth": 1000000000000,
    "quadrillionth": 1000000000000000,
    "quintillionth": 1000000000000000000,
    "sextillionth": 1000000000000000000000,
}

_WORD_BASED_PATTERNS_RE = {
    r"zeroth$": ("zero", "th"),
    r"first$": ("one", "st"),
    r"second$": ("two", "nd"),
    r"third$": ("three", "rd"),
    r"fourth$": ("four", "th"),
    r"fifth$": ("five", "th"),
    r"sixth$": ("six", "th"),
    r"seventh$": ("seven", "th"),
    r"eighth$": ("eight", "th"),
    r"ninth$": ("nine", "th"),
    r"tenth$": ("ten", "th"),
    r"eleventh$": ("eleven", "th"),
    r"twelfth$": ("twelve", "th"),
    r"thirteenth$": ("thirteen", "th"),
    r"fourteenth$": ("fourteen", "th"),
    r"fifteenth$": ("fifteen", "th"),
    r"sixteenth$": ("sixteen", "th"),
    r"seventeenth$": ("seventeen", "th"),
    r"eighteenth$": ("eighteen", "th"),
    r"nineteenth$": ("nineteen", "th"),
    r"twentieth$": ("twenty", "th"),
    r"thirtieth$": ("thirty", "th"),
    r"fortieth$": ("forty", "th"),
    r"fiftieth$": ("fifty", "th"),
    r"sixtieth$": ("sixty", "th"),
    r"seventieth$": ("seventy", "th"),
    r"eightieth$": ("eighty", "th"),
    r"ninetieth$": ("ninety", "th"),
    r"hundredth$": ("hundred", "th"),
    r"thousandth$": ("thousand", "th"),
    r"millionth$": ("million", "th"),
    r"billionth$": ("billion", "th"),
    r"trillionth$": ("trillion", "th"),
    r"quadrillionth$": ("quadrillion", "th"),
    r"quintillionth$": ("quintillion", "th"),
    r"sextillionth$": ("sextillion", "th"),
}

_MULTIPLIERS = {
    "hundred": 100,
    "thousand": 1000,
    "million": 1000000,
    "billion": 1000000000,
    "trillion": 1000000000000,
    "quadrillion": 1000000000000000,
    "quintillion": 1000000000000000000,
    "sextillion": 1000000000000000000000,
}

_ROMAN_NUMERAL_MAPPING = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

# Enforces canonical thousands, hundreds, tens, and units groups for 1–3999.
_ROMAN_NUMERAL_RE = r"^(M{0,3})(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"

# Currency tokens accepted by numeric validation and accounting notation.
_CURRENCY_SYMBOLS = [
    r"$",  # US Dollar
    r"€",  # Euro
    r"£",  # British Pound Sterling
    r"¥",  # Japanese Yen / Chinese Yuan
    r"₹",  # Indian Rupee
    r"₩",  # South Korean Won
    r"₽",  # Russian Ruble
    r"R$",  # Brazilian Real
    r"₺",  # Turkish Lira
    r"฿",  # Thai Baht
    r"₫",  # Vietnamese Dong
    r"₱",  # Philippine Peso
    r"₴",  # Ukrainian Hryvnia
    r"₸",  # Kazakhstani Tenge
    r"֏",  # Armenian Dram
    r"₦",  # Nigerian Naira
    r"₵",  # Ghanaian Cedi
    r"Br",  # Belarusian Ruble / Ethiopian Birr
    r"₾",  # Georgian Lari
    r"₪",  # Israeli Shekel
    r"R",  # South African Rand
    r"HK$",  # Hong Kong Dollar
    r"S$",  # Singapore Dollar
    r"RM",  # Malaysian Ringgit
    r"Rp",  # Indonesian Rupiah
    r"Kč",  # Czech Koruna
    r"zł",  # Polish Zloty
    r"kr",  # Scandinavian Krone (Denmark, Norway, Sweden)
    r"Ft",  # Hungarian Forint
    r"lei",  # Romanian Leu
    r"лв",  # Bulgarian Lev
    r"дин",  # Serbian Dinar
    r"kn",  # Croatian Kuna
    r"ден",  # Macedonian Denar
    r"L",  # Albanian Lek
    r"Br",  # Belarusian Ruble / Ethiopian Birr
    r"S/.",  # Peruvian Sol
    r"CHF",  # Swiss Franc
]

_ORD_SUFFIX_RE = re.compile(r"^-?\d+(st|nd|rd|th)$", re.IGNORECASE)

# Accepts an optional sign but excludes decimal points and separators.
_DIGIT_ONLY_RE = re.compile(r"^[+-]?\d+$")

_DIGIT_NUMBER_RE = re.compile(r"-?(?:(?:\d+(?:,\d{3})*)(?:\.\d+)?|\.\d+)")

_STRUCTURED_ORDINAL_RE = re.compile(
    r"(?<![\w,])[+\-\u2212]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:st|nd|rd|th)(?!\w)",
    flags=re.IGNORECASE,
)

_STRUCTURED_NUMBER_RE = re.compile(
    r"(?<![\w,.])[+\-\u2212]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)"
    r"(?!\w|,\d|\.\d)"
)

_SCIENTIFIC_NUMBER_RE = re.compile(
    r"^[+\-\u2212]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))[eE][+\-\u2212]?\d+$"
)

_STRUCTURED_SCIENTIFIC_RE = re.compile(
    r"(?<![\w,.])[+\-\u2212]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))"
    r"[eE][+\-\u2212]?\d+(?!\w|,\d|\.\d)"
)

_ROMAN_TOKEN_RE = re.compile(r"(?<!\w)(?:[IVXLCDM]+|[\u2160-\u2188]+)(?!\w)")

_SIGNED_WORD_PREFIX_RE = re.compile(r"\b(?:negative|minus)\s+$", flags=re.IGNORECASE)

_AND_WORD_RE = re.compile(r"\band\b", flags=re.IGNORECASE)

# Accepts fixed-point decimal syntax while enforcing canonical comma grouping.
_DECIMAL_NUMBER_RE = re.compile(r"^[+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d*)?|\.\d+)$")

_CURRENCY_SYMBOL_PATTERN = (
    "(?:"
    + "|".join(
        re.escape(symbol) for symbol in sorted(set(_CURRENCY_SYMBOLS), key=len, reverse=True)
    )
    + ")"
)

_ACCOUNTING_BODY_PATTERN = r"(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)"

_ACCOUNTING_NUMBER_RE = re.compile(
    rf"^(?:(?P<outer>{_CURRENCY_SYMBOL_PATTERN})\s*)?\(\s*"
    rf"(?:(?P<inner>{_CURRENCY_SYMBOL_PATTERN})\s*)?"
    rf"(?P<number>{_ACCOUNTING_BODY_PATTERN})\s*\)$"
)

_STRUCTURED_ACCOUNTING_RE = re.compile(
    rf"(?<!\w)(?:(?:{_CURRENCY_SYMBOL_PATTERN})\s*)?\(\s*"
    rf"(?:(?:{_CURRENCY_SYMBOL_PATTERN})\s*)?{_ACCOUNTING_BODY_PATTERN}\s*\)(?!\w)"
)

_COMMA_RE = re.compile(r",")

# Captures non-digit prefixes and suffixes around a numeric value.
_NUM_STR_BOUNDARY_RE = re.compile(r"(^\D*)(?:[\d,.]+)?(\D*$)")

_HYPHEN_OR_SPACE_RE = re.compile(r"[\s-]+")

_DIGIT_THEN_LETTER_RE = re.compile(r"^\d.*[a-zA-Z]$")

_SPACE_UNDERSCORE_RE = re.compile(r"[ _]+")

_CARDINAL_WORDS = ["zero", *_UNIT_DIGITS_WORDS, *_TEEN_NUMERALS_WORDS, *_TENS_MULTIPLES_WORDS]

_ORDINAL_WORDS = list(_ORDINAL_MAPPING.keys())

# Limits hyphen normalization to recognized number-word pairs.
_HYPHEN_BETWEEN_NUMBER_WORDS_RE = re.compile(
    rf"\b({'|'.join(_CARDINAL_WORDS + _ORDINAL_WORDS)})-({'|'.join(_CARDINAL_WORDS + _ORDINAL_WORDS)})\b",
    flags=re.IGNORECASE,
)


# Parsing helpers
def __parseNumericToken(s: str, first_only: bool = True, wrap_single: bool = False):
    """Return digit-based and spelled-out numeric tokens in source order."""
    if not s:
        return None if first_only else []

    matches = [
        (match.start(), _COMMA_RE.sub("", match.group(0))) for match in _DIGIT_NUMBER_RE.finditer(s)
    ]
    matches.extend(
        (match.start(), s[match.start() : match.end()])
        for match in re.finditer(_NUM_WORDS_RE, s, re.IGNORECASE)
    )
    matches.sort(key=lambda item: item[0])

    if not matches:
        return None if first_only else []

    found = [token for _, token in matches]
    if first_only:
        result = found[0]
        return [result] if wrap_single else result
    return found


def __parseRomanNumeral(s: str):
    """Return the value of a canonical Roman numeral, or ``None`` if invalid."""
    if not isinstance(s, str):
        return None

    normalized = unicodedata.normalize("NFKC", s).strip().upper()
    if not normalized or not re.fullmatch(_ROMAN_NUMERAL_RE, normalized):
        return None

    num, prev = 0, 0

    # Right-to-left scanning distinguishes subtractive pairs from additive symbols.
    for char in reversed(normalized):
        curr = _ROMAN_NUMERAL_MAPPING[char]
        num = num - curr if curr < prev else num + curr
        prev = curr

    return num if num > 0 else None


def __validate_numstr(n: Union[int, float, str], clean: bool = False) -> Optional[str]:
    """Return the original input, or cleaned text, when float parsing succeeds.

    Currency tokens, commas, and signs are removed before validation.
    Set clean to return the stripped text rather than the original input."""
    numstr = str(n)
    clean_numstr = reduce(lambda s, sign: s.replace(sign, ""), _CURRENCY_SYMBOLS, numstr).replace(
        ",", ""
    )
    clean_numstr = clean_numstr.replace("+", "").replace("-", "")
    try:
        float(clean_numstr)
    except ValueError:
        return None
    return clean_numstr if clean else n


def _coerce_fixed_decimal(value: NumLike) -> Optional[Decimal]:
    """Parse finite numeric values or canonically grouped fixed-point strings.

    Floats are converted from their decimal string representation. Boolean and
    non-finite values are rejected."""
    if isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value if value.is_finite() else None
    if isinstance(value, float):
        result = Decimal(str(value))
        return result if result.is_finite() else None

    text = str(value).strip().replace("−", "-")
    if not _DECIMAL_NUMBER_RE.fullmatch(text):
        return None

    try:
        result = Decimal(text.replace(",", ""))
    except InvalidOperation:
        return None
    return result if result.is_finite() else None


def _coerce_scientific_decimal(value: str) -> Optional[Decimal]:
    """Return a finite ``Decimal`` for canonical scientific notation."""
    if not isinstance(value, str):
        return None
    text = value.strip().replace("−", "-")
    if not _SCIENTIFIC_NUMBER_RE.fullmatch(text):
        return None
    try:
        result = Decimal(text)
    except InvalidOperation:
        return None
    return result if result.is_finite() else None


def _coerce_accounting_decimal(value: str) -> Optional[Decimal]:
    """Parse parenthesized accounting notation, preserving negative zero.

    Accept one currency token either before or inside the parentheses."""
    if not isinstance(value, str):
        return None
    match = _ACCOUNTING_NUMBER_RE.fullmatch(value.strip())
    if not match or (match.group("outer") and match.group("inner")):
        return None
    result = _coerce_fixed_decimal(match.group("number"))
    if result is None:
        return None
    return result.copy_abs().copy_negate()


def _coerce_decimal(value: NumLike) -> Optional[Decimal]:
    """Return a finite decimal from any supported decimal notation."""
    if isinstance(value, str):
        for parser in (
            _coerce_accounting_decimal,
            _coerce_scientific_decimal,
            _coerce_fixed_decimal,
        ):
            result = parser(value)
            if result is not None:
                return result
        return None
    return _coerce_fixed_decimal(value)


def _integral_value(value: Union[int, Decimal]) -> Optional[int]:
    """Return an integer when ``value`` has no fractional component."""
    if isinstance(value, int):
        return value
    if value == value.to_integral_value():
        return int(value)
    return None


# Numeric formatting
def insertSep(n: Union[int, float, str], sep: str = ",") -> Optional[str]:
    """Insert a thousands separator while preserving surrounding text."""
    num_str = str(n)
    num_str = " ".join(num_str.split())

    match = _NUM_STR_BOUNDARY_RE.match(num_str)
    if not match:
        return None

    prefix, suffix = match.groups()

    if not __validate_numstr(num_str):
        return None
    else:
        cleaned_numeric_part = __validate_numstr(num_str, True)

    if "." in cleaned_numeric_part:
        integer_part, decimal_part = cleaned_numeric_part.split(".")
        integer_part = int(integer_part)
    else:
        integer_part, decimal_part = int(cleaned_numeric_part), None

    formatted_integer_part = f"{integer_part:,}".replace(",", sep)

    if decimal_part is not None:
        formatted_number = f"{formatted_integer_part}.{decimal_part}"
    else:
        formatted_number = formatted_integer_part

    return f"{prefix}{formatted_number}{suffix}"


def formatDecimal(n: Union[int, float, str], place: int = 5) -> Optional[str]:
    """Pad or truncate the fractional part to place digits without rounding.

    Invalid numeric text returns None. The output retains a decimal point even
    when place is zero."""
    n = str(n)
    n = " ".join(n.split())

    if not __validate_numstr(n):
        return None

    place = int(place)

    if "." not in n:
        n = f"{n}.{str(10**place).replace('1', '')}"

    integer_part, decimal_part = n.split(".")
    if len(decimal_part) < place:
        decimal_part = decimal_part.ljust(place, "0")
    elif len(decimal_part) > place:
        decimal_part = decimal_part[:place]

    return f"{integer_part}.{decimal_part}"


# Core conversions
def wordsToInt(s: str, thousands_sep: bool = False, sep: str = ","):
    """Parse a cardinal English number phrase.

    Hyphenated forms and a grammatical ``and`` are accepted. Ordinal phrases,
    malformed expressions, and values outside the supported range return
    ``None``. When ``thousands_sep`` is true, the result is a formatted string.
    """
    if not s:
        return None

    is_negative = False
    s = s.strip().lower()
    if s.startswith("negative "):
        is_negative = True
        s = s.replace("negative ", "", 1)
    elif s.startswith("minus "):
        is_negative = True
        s = s.replace("minus ", "", 1)

    # Cardinal parsing must not consume an otherwise valid ordinal phrase.
    token = __parseNumericToken(s)
    if token and ordinalWordsToInt(token):
        return None

    units_dict = {"zero": 0, **{word: i + 1 for i, word in enumerate(_UNIT_DIGITS_WORDS)}}
    tens_dict = {word: (i + 1) * 10 for i, word in enumerate(_TENS_MULTIPLES_WORDS)}
    teens_dict = {word: i + 11 for i, word in enumerate(_TEEN_NUMERALS_WORDS)}

    words_list = _HYPHEN_OR_SPACE_RE.split(s)
    if not words_list or words_list[0] == "and" or words_list[-1] == "and":
        return None
    if any(a == b == "and" for a, b in zip(words_list, words_list[1:])):
        return None
    scale_words = set(_MULTIPLIERS)
    for index, word in enumerate(words_list):
        if word == "and":
            previous = words_list[index - 1]
            following = words_list[index + 1]
            if previous not in scale_words or following in scale_words | {"and"}:
                return None
    words_list = [word for word in words_list if word != "and"]

    if words_list == ["zero"]:
        return "0" if thousands_sep else 0
    if "zero" in words_list:
        return None

    number = 0
    group = 0
    last_large_scale = _MAX_ABS_VALUE
    previous_kind = None

    for word in words_list:
        if word in units_dict and word != "zero":
            if previous_kind in {"unit", "teen"}:
                return None
            group += units_dict[word]
            previous_kind = "unit"
        elif word in teens_dict:
            if previous_kind in {"unit", "teen", "tens"}:
                return None
            group += teens_dict[word]
            previous_kind = "teen"
        elif word in tens_dict:
            if previous_kind in {"unit", "teen", "tens"}:
                return None
            group += tens_dict[word]
            previous_kind = "tens"
        elif word == "hundred":
            if previous_kind != "unit" or not 1 <= group <= 9:
                return None
            group *= 100
            previous_kind = "hundred"
        elif word in _MULTIPLIERS:
            scale = _MULTIPLIERS[word]
            if scale >= last_large_scale or group == 0:
                return None
            number += group * scale
            group = 0
            last_large_scale = scale
            previous_kind = "scale"
        else:
            return None

    number += group
    if abs(number) >= _MAX_ABS_VALUE:
        return None

    if is_negative:
        number = -number
    if thousands_sep:
        number = insertSep(number, sep=sep)
    return number


def wordsToDecimal(s: str) -> Optional[Decimal]:
    """Parse an English cardinal or fixed-point phrase as a ``Decimal``.

    Digits following ``point`` must be spoken individually so their order and
    trailing zeros remain exact. Integer-only phrases are also accepted.
    """
    if not isinstance(s, str):
        return None

    text = " ".join(s.strip().lower().split())
    if not text:
        return None

    is_negative = False
    for prefix in ("negative ", "minus "):
        if text.startswith(prefix):
            is_negative = True
            text = text[len(prefix) :]
            break
    if text.startswith(("negative ", "minus ")):
        return None

    if "point" not in text:
        integer = wordsToInt(text)
        if integer is None:
            return None
        result = Decimal(integer)
        return -result if is_negative else result

    if text.count("point") != 1:
        return None

    whole_text, fractional_text = (part.strip() for part in text.split("point", 1))
    if not fractional_text:
        return None

    whole = 0 if not whole_text else wordsToInt(whole_text)
    if whole is None:
        return None

    fractional_words = _HYPHEN_OR_SPACE_RE.split(fractional_text)
    digit_values = {word: str(index) for index, word in enumerate(_DECIMAL_DIGIT_WORDS)}
    if not fractional_words or any(word not in digit_values for word in fractional_words):
        return None

    fractional_digits = "".join(digit_values[word] for word in fractional_words)
    result = Decimal(f"{whole}.{fractional_digits}")
    return -result if is_negative else result


def ordinalWordsToInt(s: str, to_num: bool = False, thousands_sep: bool = False, sep: str = ","):
    """Parse an English ordinal phrase, returning a suffixed string by default.

    Set to_num to return its integer value. With both to_num and
    thousands_sep enabled, return a grouped numeric string instead.
    Negative prefixes and hyphenated forms are accepted."""
    s = _HYPHEN_BETWEEN_NUMBER_WORDS_RE.sub(r"\1 \2", s)

    if not s:
        return None

    is_negative = False
    s = s.strip().lower()
    if s.startswith("negative "):
        is_negative = True
        s = s.replace("negative ", "", 1)
    elif s.startswith("minus "):
        is_negative = True
        s = s.replace("minus ", "", 1)

    token = __parseNumericToken(s)
    if not token:
        return None

    cardinal_form = stripOrdinalSuffix(token)
    if cardinal_form is None:
        return None

    magnitude = wordsToInt(cardinal_form[0])
    if magnitude is None:
        return None

    check_number = magnitude if to_num else f"{magnitude}{ordinalSuffix(magnitude)}"

    if is_negative:
        check_number = -check_number if isinstance(check_number, int) else f"-{check_number}"
    if to_num and thousands_sep:
        return insertSep(check_number, sep=sep)
    return check_number


def stringToInt(s: str, to_str: bool = False, thousands_sep: bool = False, sep: str = ","):
    """Parse digits or a correctly suffixed ordinal numeral.

    Comma grouping and negative prefixes are accepted. ``to_str`` controls the
    result type; ``thousands_sep`` applies only to string results.
    """
    if not s:
        return None

    is_negative = False
    number_str = s.strip()
    if number_str.startswith("-"):
        is_negative = True
        number_str = number_str[1:].strip()
    elif number_str.lower().startswith("negative "):
        is_negative = True
        number_str = number_str.lower().replace("negative ", "", 1)
    elif number_str.lower().startswith("minus "):
        is_negative = True
        number_str = number_str.lower().replace("minus ", "", 1)

    compact = _COMMA_RE.sub("", number_str)
    ordinal_match = re.fullmatch(r"(\d+)(st|nd|rd|th)", compact, re.IGNORECASE)
    if ordinal_match:
        val = int(ordinal_match.group(1))
        if ordinal_match.group(2).lower() != ordinalSuffix(val):
            return None
    elif compact.isdigit():
        val = int(compact)
    else:
        return None

    val = -val if is_negative else val
    if thousands_sep and to_str:
        return insertSep(val, sep=sep)
    return str(val) if to_str else val


def stringToDecimal(s: NumLike) -> Optional[Decimal]:
    """Parse supported fixed-point, scientific, or accounting notation."""
    return _coerce_decimal(s)


def scientificToDecimal(s: str) -> Optional[Decimal]:
    """Parse canonical scientific notation as an exact ``Decimal`` value."""
    return _coerce_scientific_decimal(s)


def accountingToDecimal(s: str) -> Optional[Decimal]:
    """Parse parenthesized accounting notation as a negative ``Decimal`` value."""
    return _coerce_accounting_decimal(s)


def intToWords(n: Union[int, float], thousands_sep: bool = False):
    """Render an integer or decimal value as English words.

    Decimal digits are spelled individually to preserve zeros. Values outside
    the supported integer range and malformed inputs return ``None``.
    """

    def _from_int(x):
        if abs(x) >= _MAX_ABS_VALUE:
            return None
        if x == 0:
            return "zero"

        def one(num):
            switcher = {
                1: "one",
                2: "two",
                3: "three",
                4: "four",
                5: "five",
                6: "six",
                7: "seven",
                8: "eight",
                9: "nine",
            }
            return switcher.get(num, "")

        def two_less_20(num):
            switcher = {
                10: "ten",
                11: "eleven",
                12: "twelve",
                13: "thirteen",
                14: "fourteen",
                15: "fifteen",
                16: "sixteen",
                17: "seventeen",
                18: "eighteen",
                19: "nineteen",
            }
            return switcher.get(num, "")

        def ten(num):
            switcher = {
                2: "twenty",
                3: "thirty",
                4: "forty",
                5: "fifty",
                6: "sixty",
                7: "seventy",
                8: "eighty",
                9: "ninety",
            }
            return switcher.get(num, "")

        def two(num):
            if not num:
                return ""
            elif num < 10:
                return one(num)
            elif num < 20:
                return two_less_20(num)
            else:
                tenner = num // 10
                rest = num % 10
                return ten(tenner) + ("-" + one(rest) if rest else "")

        def three(num):
            hundred = num // 100
            rest = num % 100
            if hundred and rest:
                return one(hundred) + " hundred " + two(rest)
            elif hundred and not rest:
                return one(hundred) + " hundred"
            else:
                return two(rest)

        remainder = abs(x)
        segments = []
        scales = (
            (10**21, "sextillion"),
            (10**18, "quintillion"),
            (10**15, "quadrillion"),
            (10**12, "trillion"),
            (10**9, "billion"),
            (10**6, "million"),
            (10**3, "thousand"),
        )
        for scale, name in scales:
            group, remainder = divmod(remainder, scale)
            if group:
                segments.append(f"{three(group)} {name}")
        if remainder:
            segments.append(three(remainder))

        result = ""
        if segments:
            if thousands_sep and len(segments) > 1:
                result = ", ".join(seg for seg in segments if seg).strip()
            else:
                result = " ".join(seg for seg in segments if seg).strip()
        else:
            result = "zero"

        if x < 0:
            result = "negative " + result

        return result

    try:
        n_str = str(n).strip()

        if isinstance(n, (Decimal, float)) or "." in n_str:
            return decimalToWords(n)
        else:
            return _from_int(int(n_str))

    except (ValueError, TypeError):
        return None


def decimalToWords(n: NumLike) -> Optional[str]:
    """Render a finite decimal as English words without losing fractional zeros."""
    value = _coerce_decimal(n)
    if value is None or value.copy_abs() >= Decimal(_MAX_ABS_VALUE):
        return None

    is_negative = value.is_signed()
    normalized = format(value.copy_abs(), "f")
    whole_text, separator, fractional_text = normalized.partition(".")
    whole_words = intToWords(int(whole_text), thousands_sep=False)
    if whole_words is None:
        return None
    if is_negative:
        whole_words = f"negative {whole_words}"
    if not separator:
        return whole_words

    fractional_words = " ".join(_DECIMAL_DIGIT_WORDS[int(digit)] for digit in fractional_text)
    return f"{whole_words} point {fractional_words}"


def decimalToScientific(n: NumLike, *, uppercase: bool = False) -> Optional[str]:
    """Render scientific notation without redundant trailing mantissa zeros.

    Preserve the sign of zero and use an explicit signed exponent. Set
    uppercase to emit E rather than e."""
    value = _coerce_decimal(n)
    if value is None:
        return None

    sign, raw_digits, exponent = value.as_tuple()
    digits = list(raw_digits)
    if not any(digits):
        mantissa = "-0" if sign else "0"
        scientific_exponent = 0
    else:
        while len(digits) > 1 and digits[-1] == 0:
            digits.pop()
            exponent += 1
        digit_text = "".join(str(digit) for digit in digits)
        mantissa = digit_text[0]
        if len(digit_text) > 1:
            mantissa += f".{digit_text[1:]}"
        if sign:
            mantissa = f"-{mantissa}"
        scientific_exponent = exponent + len(digits) - 1

    marker = "E" if uppercase else "e"
    return f"{mantissa}{marker}{scientific_exponent:+d}"


def decimalToAccounting(
    n: NumLike,
    *,
    currency: str = "",
    grouping: bool = True,
) -> Optional[str]:
    """Format accounting notation while preserving fractional scale.

    Negative values, including signed zero, use parentheses. The currency
    prefix is inserted verbatim; grouping controls thousands separators."""
    value = _coerce_decimal(n)
    if value is None or not isinstance(currency, str) or not isinstance(grouping, bool):
        return None

    fixed = format(value.copy_abs(), "f")
    whole, separator, fraction = fixed.partition(".")
    if grouping:
        whole = f"{int(whole):,}"
    number = whole if not separator else f"{whole}.{fraction}"
    number = f"{currency}{number}"
    return f"({number})" if value.is_signed() else number


def intToOrdinalWords(n: int):
    """Render an integer as an English ordinal phrase, or ``None`` if invalid."""
    try:
        n = int(str(n).strip())
    except (ValueError, TypeError):
        return None

    words = intToWords(n, thousands_sep=False)
    if not words:
        return None

    # English ordinal inflection applies to the final lexical component.
    word_parts = words.split()
    if not word_parts:
        return None

    is_negative = False
    if word_parts[0] == "negative":
        is_negative = True
        word_parts = word_parts[1:]

    last_word = word_parts[-1]

    def _replace_end(full_word, old_end, new_end):
        return full_word[: -len(old_end)] + new_end if full_word.endswith(old_end) else full_word

    if last_word.endswith("one"):
        word_parts[-1] = _replace_end(last_word, "one", "first")
    elif last_word.endswith("two"):
        word_parts[-1] = _replace_end(last_word, "two", "second")
    elif last_word.endswith("three"):
        word_parts[-1] = _replace_end(last_word, "three", "third")
    elif last_word.endswith("five"):
        word_parts[-1] = _replace_end(last_word, "five", "fifth")
    elif last_word.endswith("eight"):
        word_parts[-1] = _replace_end(last_word, "eight", "eighth")
    elif last_word.endswith("nine"):
        word_parts[-1] = _replace_end(last_word, "nine", "ninth")
    elif last_word.endswith("twelve"):
        word_parts[-1] = _replace_end(last_word, "twelve", "twelfth")
    elif last_word.endswith("y"):
        word_parts[-1] = _replace_end(
            last_word, "y", "ieth"
        )  # Cardinal tens ending in "y" use the ordinal ending "ieth".
    elif last_word.endswith("teen"):
        word_parts[-1] = _replace_end(
            last_word, "teen", "teenth"
        )  # Cardinal teens use the ordinal ending "teenth".
    else:
        word_parts[-1] = word_parts[-1] + "th"

    if is_negative:
        return "negative " + " ".join(word_parts)
    else:
        return " ".join(word_parts)


def ordinalSuffix(n: Union[int, str]) -> str:
    """Return the English ordinal suffix, or None for invalid input."""
    try:
        if _DIGIT_THEN_LETTER_RE.match(str(n).strip()):
            n = ordinalNumToCardinalNum(n)
        n = int(str(n).strip())
    except (ValueError, TypeError):
        return None

    last_two = abs(n) % 100
    last_digit = abs(n) % 10
    if last_two in (11, 12, 13):
        return "th"
    else:
        if last_digit == 1:
            return "st"
        elif last_digit == 2:
            return "nd"
        elif last_digit == 3:
            return "rd"
        else:
            return "th"


def stripOrdinalSuffix(s: str):
    """Return the cardinal phrase and suffix for an English ordinal phrase."""
    number_str = s
    suffix = None
    for pattern, (replacement, suffix_to_remove) in _WORD_BASED_PATTERNS_RE.items():
        if re.search(pattern, s, flags=re.IGNORECASE):
            suffix = suffix_to_remove
            number_str = re.sub(pattern, replacement, number_str, flags=re.IGNORECASE)
            break
    if suffix is None:
        return None
    return (number_str, suffix)


def extractNumericValue(s: str, allnum: bool = True):
    """Extract numeric values in source order, or None when none are found.

    Integer, decimal, scientific, accounting, ordinal, and English word forms
    are recognized. Set allnum to false to return only the first value;
    otherwise return a single value directly or a list of multiple values."""
    if not isinstance(s, str) or not s:
        return None

    entities = extractNumericEntities(s, include_roman=False)
    if not entities:
        return None

    values = [entity.value for entity in entities]
    if s.strip().lower().startswith(("negative ", "minus ")) and not entities[0].is_negative:
        first = values[0]
        values[0] = first.copy_abs().copy_negate() if isinstance(first, Decimal) else -abs(first)

    if not allnum:
        return values[0]
    return values[0] if len(values) == 1 else values


def _numeric_match(
    source: str,
    start: int,
    end: int,
    value: NumericValue,
    representation: str,
) -> NumericMatch:
    """Preserve source offsets and signed decimal zero in a structured match."""
    is_negative = value.is_signed() if isinstance(value, Decimal) else value < 0
    return NumericMatch(
        text=source[start:end],
        value=value,
        representation=representation,
        start=start,
        end=end,
        is_ordinal=representation.startswith("Ordinal"),
        is_negative=is_negative,
    )


def _word_numeric_match(source: str, start: int, end: int) -> Optional[NumericMatch]:
    """Parse a word phrase and include any adjacent negative or minus prefix."""
    sign_match = _SIGNED_WORD_PREFIX_RE.search(source[:start])
    if sign_match:
        start = sign_match.start()
    raw = source[start:end]
    representation = Type(raw)
    if representation == "Ordinal Word":
        value = ordinalWordsToInt(raw, to_num=True)
    elif representation == "Cardinal Word":
        value = wordsToDecimal(raw) if "point" in raw.lower().split() else wordsToInt(raw)
        if (
            isinstance(value, Decimal)
            and not value.is_signed()
            and raw.lower().startswith(("negative ", "minus "))
        ):
            value = value.copy_negate()
    else:
        return None
    if value is None:
        return None
    return _numeric_match(source, start, end, value, representation)


def extractNumericEntities(
    s: str,
    *,
    include_roman: bool = True,
    include_single_roman: bool = False,
) -> List[NumericMatch]:
    """Extract structured, non-overlapping numeric entities in source order.

    Cardinal and ordinal digits, exact decimal, scientific, and accounting
    notation, English cardinal and ordinal phrases, and canonical Roman
    numerals are recognized. Ambiguous single-letter ASCII Roman numerals are
    excluded unless ``include_single_roman`` is true.
    """
    if not isinstance(s, str) or not s:
        return []

    candidates = []

    for match in _STRUCTURED_ACCOUNTING_RE.finditer(s):
        value = accountingToDecimal(match.group(0))
        if value is not None:
            candidates.append(
                (
                    match.start(),
                    match.end(),
                    0,
                    _numeric_match(s, match.start(), match.end(), value, "Accounting Number"),
                )
            )

    for match in _STRUCTURED_SCIENTIFIC_RE.finditer(s):
        value = scientificToDecimal(match.group(0))
        if value is not None:
            candidates.append(
                (
                    match.start(),
                    match.end(),
                    1,
                    _numeric_match(s, match.start(), match.end(), value, "Scientific Number"),
                )
            )

    for match in _STRUCTURED_ORDINAL_RE.finditer(s):
        raw = match.group(0)
        normalized = raw.replace("−", "-")
        value = stringToInt(normalized[1:] if normalized.startswith("+") else normalized)
        if value is not None:
            candidates.append(
                (
                    match.start(),
                    match.end(),
                    2,
                    _numeric_match(s, match.start(), match.end(), value, "Ordinal Number"),
                )
            )

    for match in _STRUCTURED_NUMBER_RE.finditer(s):
        raw = match.group(0)
        decimal_value = stringToDecimal(raw)
        if decimal_value is None:
            continue
        value = decimal_value if "." in raw else int(decimal_value)
        representation = "Decimal Number" if isinstance(value, Decimal) else "Cardinal Number"
        candidates.append(
            (
                match.start(),
                match.end(),
                3,
                _numeric_match(s, match.start(), match.end(), value, representation),
            )
        )

    for match in re.finditer(_NUM_WORDS_RE, s, flags=re.IGNORECASE):
        entity = _word_numeric_match(s, match.start(), match.end())
        if entity is not None:
            candidates.append((entity.start, entity.end, 4, entity))
            continue

        conjunctions = list(_AND_WORD_RE.finditer(s, match.start(), match.end()))
        segment_start = match.start()
        for conjunction in conjunctions:
            segment_end = conjunction.start()
            while segment_end > segment_start and s[segment_end - 1] in " \t\r\n\f\v-":
                segment_end -= 1
            entity = _word_numeric_match(s, segment_start, segment_end)
            if entity is not None:
                candidates.append((entity.start, entity.end, 4, entity))
            segment_start = conjunction.end()
            while segment_start < match.end() and s[segment_start] in " \t\r\n\f\v-":
                segment_start += 1

        entity = _word_numeric_match(s, segment_start, match.end())
        if entity is not None:
            candidates.append((entity.start, entity.end, 4, entity))

    if include_roman:
        for match in _ROMAN_TOKEN_RE.finditer(s):
            raw = match.group(0)
            if raw.isascii() and len(raw) == 1 and not include_single_roman:
                continue
            value = romanToInt(raw)
            if value is not None:
                candidates.append(
                    (
                        match.start(),
                        match.end(),
                        5,
                        _numeric_match(s, match.start(), match.end(), value, "Roman Numeral"),
                    )
                )

    # Prefer the longest span at each offset; priority breaks equal-span ties.
    candidates.sort(key=lambda item: (item[0], -(item[1] - item[0]), item[2]))
    selected = []
    selected_end = -1
    for start, end, _, entity in candidates:
        if start < selected_end:
            continue
        selected.append(entity)
        selected_end = end
    return selected


def normalizeNumericText(
    s: str,
    *,
    style: Literal["digits", "words"] = "digits",
    include_roman: bool = True,
    include_single_roman: bool = False,
) -> str:
    """Normalize numeric entities while preserving surrounding source text.

    The digits style keeps ordinal suffixes and renders other values with
    decimal digits. The words style preserves ordinal semantics and leaves
    entities unchanged when they cannot be rendered as English words."""
    if not isinstance(s, str):
        raise TypeError("s must be a string")
    if style not in ("digits", "words"):
        raise ValueError("style must be 'digits' or 'words'")

    entities = extractNumericEntities(
        s,
        include_roman=include_roman,
        include_single_roman=include_single_roman,
    )
    if not entities:
        return s

    normalized_parts = []
    source_end = 0
    for entity in entities:
        normalized_parts.append(s[source_end : entity.start])
        if style == "digits":
            if entity.is_ordinal:
                replacement = _cardinal_number_to_ordinal_number(int(entity.value))
            elif isinstance(entity.value, Decimal):
                replacement = format(entity.value, "f")
            else:
                replacement = str(entity.value)
        elif entity.is_ordinal:
            replacement = intToOrdinalWords(int(entity.value))
        elif isinstance(entity.value, Decimal):
            replacement = decimalToWords(entity.value)
        else:
            replacement = intToWords(entity.value)

        normalized_parts.append(replacement if replacement is not None else entity.text)
        source_end = entity.end

    normalized_parts.append(s[source_end:])
    return "".join(normalized_parts)


# Roman numerals
def romanToInt(s: str, to_str: bool = False):
    """Parse a canonical Roman numeral as an integer or numeric string."""
    num = __parseRomanNumeral(s)
    return str(num) if num is not None and to_str else num


def romanToWords(s: str):
    """Render a canonical Roman numeral as cardinal English words."""
    num = __parseRomanNumeral(s)
    return intToWords(num) if num is not None else None


def intToRoman(n: int):
    """Convert an integer from 1 through 3999 to canonical Roman notation."""
    try:
        value = int(str(n).strip())
    except (TypeError, ValueError):
        return None
    if not 1 <= value <= 3999:
        return None

    numerals = (
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    )
    result = []
    for amount, numeral in numerals:
        count, value = divmod(value, amount)
        result.append(numeral * count)
    return "".join(result)


# Representation conversion helpers
def _cardinal_number_to_ordinal_number(n: int) -> str:
    return f"{n}{ordinalSuffix(n)}"


def _ensure_int(x: NumLike) -> int:
    """Coerce integral decimals, digit strings, and ordinal numerals to integers.

    Return None for fractional values or unsupported input."""
    if isinstance(x, int) and not isinstance(x, bool):
        return x

    decimal_value = _coerce_fixed_decimal(x)
    if decimal_value is not None:
        return _integral_value(decimal_value)

    maybe = stringToInt(str(x))
    if maybe is None:
        return None
    return maybe


def _convert_numeric_representation(value: NumLike, from_rep: Rep, to_rep: Rep) -> NumLike:
    """Convert ``value`` between canonical representation identifiers."""
    if from_rep == to_rep:
        if from_rep == "CardinalNumber":
            return _ensure_int(value)
        if from_rep == "DecimalNumber":
            return _coerce_fixed_decimal(value)
        if from_rep == "ScientificNumber":
            return decimalToScientific(value)
        if from_rep == "AccountingNumber":
            return decimalToAccounting(value)
        return value

    # Normalize source representations through an exact integer or decimal value.
    if from_rep == "CardinalWord":
        base_value = wordsToInt(str(value))
        if base_value is None:
            base_value = wordsToDecimal(str(value))
    elif from_rep == "CardinalNumber":
        base_value = _ensure_int(value)
    elif from_rep == "DecimalNumber":
        base_value = _coerce_fixed_decimal(value)
    elif from_rep == "ScientificNumber":
        base_value = _coerce_scientific_decimal(value)
    elif from_rep == "AccountingNumber":
        base_value = _coerce_accounting_decimal(value)
    elif from_rep == "OrdinalWord":
        base_value = ordinalWordsToInt(str(value), to_num=True)
    elif from_rep == "OrdinalNumber":
        base_value = _ensure_int(value)
    elif from_rep == "RomanNumeral":
        base_value = romanToInt(str(value))
    else:
        return None

    if base_value is None:
        return None

    if to_rep == "CardinalWord":
        if isinstance(base_value, Decimal):
            return decimalToWords(base_value)
        return intToWords(base_value)
    elif to_rep == "CardinalNumber":
        return _integral_value(base_value)
    elif to_rep == "DecimalNumber":
        return base_value if isinstance(base_value, Decimal) else Decimal(base_value)
    elif to_rep == "ScientificNumber":
        return decimalToScientific(base_value)
    elif to_rep == "AccountingNumber":
        return decimalToAccounting(base_value)
    elif to_rep == "OrdinalWord":
        integer = _integral_value(base_value)
        return intToOrdinalWords(integer) if integer is not None else None
    elif to_rep == "OrdinalNumber":
        integer = _integral_value(base_value)
        return _cardinal_number_to_ordinal_number(integer) if integer is not None else None
    elif to_rep == "RomanNumeral":
        integer = _integral_value(base_value)
        return intToRoman(integer) if integer is not None else None
    return None


def cardinalWordToCardinalNum(s: str):
    """Convert a cardinal English phrase to an integer."""
    return _convert_numeric_representation(s, "CardinalWord", "CardinalNumber")


def cardinalWordToOrdinalWord(s: str):
    """Convert a cardinal English phrase to an ordinal English phrase."""
    return _convert_numeric_representation(s, "CardinalWord", "OrdinalWord")


def cardinalWordToOrdinalNum(s: str):
    """Convert a cardinal English phrase to an ordinal numeral."""
    return _convert_numeric_representation(s, "CardinalWord", "OrdinalNumber")


def cardinalNumToCardinalWord(n: int):
    """Convert an integer-like value to a cardinal English phrase."""
    try:
        n = int(str(n).strip())
        return _convert_numeric_representation(n, "CardinalNumber", "CardinalWord")
    except (ValueError, TypeError):
        return None


def cardinalNumToOrdinalWord(n: int):
    """Convert an integer-like value to an ordinal English phrase."""
    try:
        n = int(str(n).strip())
        return _convert_numeric_representation(n, "CardinalNumber", "OrdinalWord")
    except (ValueError, TypeError):
        return None


def cardinalNumToOrdinalNum(n: int):
    """Convert an integer-like value to an ordinal numeral."""
    try:
        n = int(str(n).strip())
        return _convert_numeric_representation(n, "CardinalNumber", "OrdinalNumber")
    except (ValueError, TypeError):
        return None


def ordinalWordToCardinalWord(s: str):
    """Convert an ordinal English phrase to a cardinal English phrase."""
    return _convert_numeric_representation(s, "OrdinalWord", "CardinalWord")


def ordinalWordToCardinalNum(s: str):
    """Convert an ordinal English phrase to an integer."""
    return _convert_numeric_representation(s, "OrdinalWord", "CardinalNumber")


def ordinalWordToOrdinalNum(s: str):
    """Convert an ordinal English phrase to an ordinal numeral."""
    return _convert_numeric_representation(s, "OrdinalWord", "OrdinalNumber")


def ordinalNumToCardinalWord(s: str):
    """Convert an ordinal numeral to a cardinal English phrase."""
    return _convert_numeric_representation(s, "OrdinalNumber", "CardinalWord")


def ordinalNumToCardinalNum(s: str):
    """Convert an ordinal numeral to an integer."""
    return _convert_numeric_representation(s, "OrdinalNumber", "CardinalNumber")


def ordinalNumToOrdinalWord(s: str):
    """Convert an ordinal numeral to an ordinal English phrase."""
    return _convert_numeric_representation(s, "OrdinalNumber", "OrdinalWord")


class __NumericConverter:
    """Detect and convert the supported numeric representations."""

    # Accepted aliases are normalized to the public display names.
    _LABEL_ALIASES: Dict[str, str] = {
        # Cardinal Number
        "cardinalnumber": "Cardinal Number",
        "cardnum": "Cardinal Number",
        "card-num": "Cardinal Number",
        "cn": "Cardinal Number",
        "cnum": "Cardinal Number",
        "digit": "Cardinal Number",
        "number": "Cardinal Number",
        "num": "Cardinal Number",
        "int": "Cardinal Number",
        # Decimal Number
        "decimalnumber": "Decimal Number",
        "decimal-num": "Decimal Number",
        "decimal": "Decimal Number",
        "decnum": "Decimal Number",
        "dec": "Decimal Number",
        "dn": "Decimal Number",
        # Scientific Number
        "scientificnumber": "Scientific Number",
        "scientific-num": "Scientific Number",
        "scientific": "Scientific Number",
        "exponential": "Scientific Number",
        "sci": "Scientific Number",
        "exp": "Scientific Number",
        "sn": "Scientific Number",
        # Accounting Number
        "accountingnumber": "Accounting Number",
        "accounting-num": "Accounting Number",
        "accounting": "Accounting Number",
        "parenthesized": "Accounting Number",
        "acct": "Accounting Number",
        "an": "Accounting Number",
        # Cardinal Word
        "cardinalword": "Cardinal Word",
        "cardword": "Cardinal Word",
        "card-word": "Cardinal Word",
        "cw": "Cardinal Word",
        "wordnum": "Cardinal Word",
        "wordnumber": "Cardinal Word",
        "cword": "Cardinal Word",
        # Ordinal Number
        "ordinalnumber": "Ordinal Number",
        "ordnum": "Ordinal Number",
        "ord-num": "Ordinal Number",
        "on": "Ordinal Number",
        "onum": "Ordinal Number",
        "rank": "Ordinal Number",
        "position": "Ordinal Number",
        "place": "Ordinal Number",
        # Ordinal Word
        "ordinalword": "Ordinal Word",
        "ordword": "Ordinal Word",
        "ord-word": "Ordinal Word",
        "ow": "Ordinal Word",
        "wordord": "Ordinal Word",
        "wordordinal": "Ordinal Word",
        "oword": "Ordinal Word",
        # Roman Numeral
        "romannumeral": "Roman Numeral",
        "roman": "Roman Numeral",
        "rn": "Roman Numeral",
    }

    _DISPLAY_TO_REP = {
        "Cardinal Number": "CardinalNumber",
        "Decimal Number": "DecimalNumber",
        "Scientific Number": "ScientificNumber",
        "Accounting Number": "AccountingNumber",
        "Cardinal Word": "CardinalWord",
        "Ordinal Number": "OrdinalNumber",
        "Ordinal Word": "OrdinalWord",
        "Roman Numeral": "RomanNumeral",
    }

    @classmethod
    def _canon(cls, label=None):
        """Normalize a representation alias while preserving unknown labels."""
        if label is None:
            return None
        norm = _SPACE_UNDERSCORE_RE.sub("", str(label).strip().lower())
        return cls._LABEL_ALIASES.get(norm, label)

    @classmethod
    def num_type(cls, value):
        """Return the public representation name for ``value``, if recognized."""
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return "Cardinal Number"
        if isinstance(value, (Decimal, float)):
            return "Decimal Number" if _coerce_decimal(value) is not None else None

        raw_s = str(value).strip()
        s = raw_s.lower()

        # Detection order resolves forms that could otherwise be interpreted as words.
        if _ORD_SUFFIX_RE.match(s) and stringToInt(s) is not None:
            return "Ordinal Number"

        if _DIGIT_ONLY_RE.match(s) or ("." not in s and _coerce_fixed_decimal(raw_s) is not None):
            return "Cardinal Number"

        if accountingToDecimal(raw_s) is not None:
            return "Accounting Number"

        if scientificToDecimal(raw_s) is not None:
            return "Scientific Number"

        if "." in s and _coerce_fixed_decimal(raw_s) is not None:
            return "Decimal Number"

        if romanToInt(s) is not None:
            return "Roman Numeral"

        if ordinalWordToCardinalNum(s) is not None:
            return "Ordinal Word"

        if wordsToDecimal(s) is not None:
            return "Cardinal Word"

        return None

    @classmethod
    def to_type(cls, value, target=None, *, as_str=False):
        """Convert value to target, or return its detected type when target is None.

        Unknown sources, unknown targets, and unsupported conversions raise
        ValueError. Set as_str to stringify integer and Decimal results."""
        src = cls.num_type(value)
        if src is None:
            raise ValueError(f"Cannot determine representation of {value!r}")

        target = cls._canon(target)

        if target is None:
            return src

        try:
            source_rep = cls._DISPLAY_TO_REP[src]
            target_rep = cls._DISPLAY_TO_REP[target]
        except KeyError as exc:
            raise ValueError(f"Unknown representation: {exc.args[0]!r}") from exc
        result = _convert_numeric_representation(value, source_rep, target_rep)
        if result is None:
            raise ValueError(f"Cannot convert {value!r} from {src} to {target}")

        if as_str and isinstance(result, (int, Decimal)):
            result = str(result)
        return result


_numbers = __NumericConverter()


def Type(value):
    """Return the detected numeric representation for ``value``."""
    return _numbers.num_type(value)


def Cast(value, target=None, *, as_str=False):
    """Convert ``value`` to a supported numeric representation."""
    return _numbers.to_type(value, target, as_str=as_str)


def _diagnostic_span(value) -> Tuple[int, int]:
    """Return trimmed string offsets, or (0, 0) for non-string input."""
    if not isinstance(value, str):
        return (0, 0)
    start = len(value) - len(value.lstrip())
    end = len(value.rstrip())
    return (start, max(start, end))


def _invalid_parse_diagnostic(value) -> ParseDiagnostic:
    """Classify an unrecognized input using stable diagnostic codes."""
    start, end = _diagnostic_span(value)
    if isinstance(value, bool):
        return ParseDiagnostic(
            "unsupported_type",
            "Boolean values are not treated as numbers.",
            start,
            end,
            "Use an integer or a supported numeric string.",
        )
    if isinstance(value, (Decimal, float)):
        return ParseDiagnostic(
            "non_finite_number",
            "NaN and infinite values are not supported.",
            start,
            end,
            "Use a finite numeric value.",
        )
    if not isinstance(value, str):
        return ParseDiagnostic(
            "unsupported_type",
            f"Values of type {type(value).__name__!r} are not supported.",
            start,
            end,
            "Use an integer, Decimal, float, or supported numeric string.",
        )

    text = value[start:end]
    if not text:
        return ParseDiagnostic(
            "empty_input",
            "Numeric input cannot be empty.",
            start,
            end,
            "Provide a supported numeric expression.",
        )

    if "(" in text or ")" in text:
        return ParseDiagnostic(
            "invalid_accounting_notation",
            "Accounting notation requires one balanced pair of parentheses around an unsigned value.",
            start,
            end,
            "Use a form such as (1,234.50) or ($1,234.50).",
        )

    if ("e" in text.lower()) and any(char.isdigit() for char in text):
        return ParseDiagnostic(
            "invalid_scientific_notation",
            "Scientific notation requires a coefficient and an integer exponent.",
            start,
            end,
            "Use a form such as 1.25e3 or -4E-2.",
        )

    compact = text.replace(",", "").replace("−", "-")
    ordinal_match = re.fullmatch(r"([+-]?\d+)(st|nd|rd|th)", compact, re.IGNORECASE)
    if ordinal_match:
        number = int(ordinal_match.group(1))
        expected = _cardinal_number_to_ordinal_number(number)
        return ParseDiagnostic(
            "invalid_ordinal_suffix",
            f"The ordinal suffix does not agree with {number}.",
            start,
            end,
            f"Use {expected!r}.",
        )

    if "," in text and re.fullmatch(r"[+\-−]?[\d,.]+", text):
        return ParseDiagnostic(
            "invalid_grouping",
            "Thousands separators must divide groups of exactly three digits.",
            start,
            end,
            "Use a form such as 1,234 or 1,234.50.",
        )

    if text.count(".") > 1 and re.fullmatch(r"[+\-−]?[\d.]+", text):
        return ParseDiagnostic(
            "invalid_decimal_notation",
            "A decimal number can contain only one decimal point.",
            start,
            end,
            "Remove the extra decimal point.",
        )

    if re.fullmatch(r"(?:[IVXLCDM]+|[\u2160-\u2188]+)", text, flags=re.IGNORECASE):
        return ParseDiagnostic(
            "invalid_roman_numeral",
            "The Roman numeral is not in canonical form.",
            start,
            end,
            "Use canonical subtractive notation, such as IV instead of IIII.",
        )

    if any(char.isalpha() for char in text):
        return ParseDiagnostic(
            "invalid_number_words",
            "The input is not a valid English number phrase.",
            start,
            end,
            "Check the word order, spelling, and use of 'and'.",
        )

    return ParseDiagnostic(
        "unrecognized_numeric_input",
        "The input is not a recognized numeric representation.",
        start,
        end,
        "Use digits, English number words, scientific or accounting notation, or Roman numerals.",
    )


def _normalized_source_value(value, representation: str):
    """Return the canonical numeric value for a detected representation."""
    if representation == "Cardinal Word":
        integer = wordsToInt(str(value))
        return integer if integer is not None else wordsToDecimal(str(value))
    if representation in ("Decimal Number", "Scientific Number", "Accounting Number"):
        return Cast(value, "Decimal Number")
    return Cast(value, "Cardinal Number")


def diagnoseNumeric(value, target=None, *, as_str: bool = False) -> ParseResult:
    """Parse or convert one value without raising for invalid numeric input.

    The result includes the normalized value and detected representations on
    success. Failures include a stable diagnostic code, source span, message,
    and suggested correction.
    """
    source_representation = Type(value)
    if source_representation is None:
        return ParseResult(
            source=value,
            value=None,
            source_representation=None,
            target_representation=None,
            diagnostics=(_invalid_parse_diagnostic(value),),
        )

    target_representation = None
    if target is not None:
        canonical_target = _numbers._canon(target)
        if (
            not isinstance(canonical_target, str)
            or canonical_target not in _numbers._DISPLAY_TO_REP
        ):
            diagnostic = ParseDiagnostic(
                "unknown_target",
                f"Unknown numeric representation: {target!r}.",
                0,
                0,
                "Use a representation accepted by Cast.",
            )
            return ParseResult(
                source=value,
                value=None,
                source_representation=source_representation,
                target_representation=None,
                diagnostics=(diagnostic,),
            )
        target_representation = canonical_target

    try:
        if target_representation is None:
            result = _normalized_source_value(value, source_representation)
            if as_str and isinstance(result, (int, Decimal)):
                result = str(result)
        else:
            result = Cast(value, target_representation, as_str=as_str)
    except (TypeError, ValueError) as exc:
        start, end = _diagnostic_span(value)
        diagnostic = ParseDiagnostic(
            "unsupported_conversion",
            str(exc),
            start,
            end,
            "Choose a representation compatible with this numeric value.",
        )
        return ParseResult(
            source=value,
            value=None,
            source_representation=source_representation,
            target_representation=target_representation,
            diagnostics=(diagnostic,),
        )

    return ParseResult(
        source=value,
        value=result,
        source_representation=source_representation,
        target_representation=target_representation,
    )


def batchDiagnose(values, target=None, *, as_str: bool = False) -> List[ParseResult]:
    """Eagerly diagnose every input and return results in input order.

    Strings, bytes, and non-iterable containers raise TypeError."""
    if isinstance(values, (str, bytes)):
        raise TypeError("values must be an iterable of numeric inputs, not a string")
    try:
        iterator = iter(values)
    except TypeError as exc:
        raise TypeError("values must be an iterable of numeric inputs") from exc
    return [diagnoseNumeric(value, target, as_str=as_str) for value in iterator]


def batchCast(
    values,
    target,
    *,
    errors: Literal["raise", "coerce", "ignore"] = "raise",
    as_str: bool = False,
) -> List[object]:
    """Convert an iterable with configurable handling of conversion failures.

    All inputs are diagnosed before applying the error policy. The raise policy
    raises BatchConversionError for the first failed item; coerce substitutes
    None for failures, while ignore omits failed items."""
    if errors not in ("raise", "coerce", "ignore"):
        raise ValueError("errors must be 'raise', 'coerce', or 'ignore'")

    converted = []
    for index, result in enumerate(batchDiagnose(values, target, as_str=as_str)):
        if result.ok:
            converted.append(result.value)
        elif errors == "raise":
            raise BatchConversionError(index, result)
        elif errors == "coerce":
            converted.append(None)
    return converted


# Copy method metadata without replacing the public wrapper names.
custom_assignments = tuple(
    attr for attr in WRAPPER_ASSIGNMENTS if attr not in ("__name__", "__qualname__")
)

update_wrapper(Cast, __NumericConverter.to_type, assigned=custom_assignments)
update_wrapper(Type, __NumericConverter.num_type, assigned=custom_assignments)


__all__ = [
    "NumericMatch",
    "ParseDiagnostic",
    "ParseResult",
    "BatchConversionError",
    # Core conversion functions
    "wordsToInt",
    "wordsToDecimal",
    "ordinalSuffix",
    "intToWords",
    "decimalToWords",
    "intToOrdinalWords",
    "stripOrdinalSuffix",
    "ordinalWordsToInt",
    "stringToInt",
    "stringToDecimal",
    "scientificToDecimal",
    "accountingToDecimal",
    "extractNumericValue",
    "extractNumericEntities",
    "normalizeNumericText",
    "decimalToScientific",
    "decimalToAccounting",
    "romanToWords",
    "romanToInt",
    "intToRoman",
    "insertSep",
    "formatDecimal",
    # Direct cross-representation helpers
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
    # Public detection and conversion helpers
    "Type",
    "Cast",
    "diagnoseNumeric",
    "batchDiagnose",
    "batchCast",
]
