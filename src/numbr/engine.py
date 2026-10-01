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

"""Core parsing and formatting operations for supported numeric representations.

The parsers use surface syntax rather than contextual inference. Accepted
inputs map to deterministic integer values, and formatters emit canonical
English, decimal, ordinal, or Roman representations within their documented
ranges.
"""

import re
import unicodedata
from functools import WRAPPER_ASSIGNMENTS, reduce, update_wrapper
from typing import Dict, Literal, Optional, Union

Rep = Literal[
    "CardinalWord",
    "CardinalNumber",
    "OrdinalWord",
    "OrdinalNumber",
    "RomanNumeral",
]
NumLike = Union[int, str]

_MAX_ABS_VALUE = 10**24

# Constants and compiled patterns

# Matches spelled-out numbers, including cardinal and ordinal forms.
_NUM_ORDINAL_WRDS_RE = (
    r"zero|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
    r"hundred|thousand|million|billion|trillion|quadrillion|quintillion|sextillion|"
    r"first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
    r"eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|"
    r"eighteenth|nineteenth|twentieth|thirtieth|fortieth|fiftieth|sixtieth|"
    r"seventieth|eightieth|ninetieth|hundredth|thousandth|millionth|billionth|"
    r"trillionth|quadrillionth|quintillionth|sextillionth|zeroth"
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

# Currency tokens accepted by numeric-string validation.
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

_DIGIT_NUMBER_RE = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?")

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

    # Preserve source order across digit and word representations.
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
    """Validate a numeric value after removing known currency and sign tokens."""
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


def __switch(x):
    """Return the Boolean inverse of ``x``."""
    return not x


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
    """Return ``n`` with exactly ``place`` decimal digits, or ``None`` if invalid."""
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


def ordinalWordsToInt(s: str, to_num: bool = False, thousands_sep: bool = False, sep: str = ","):
    """Parse an ordinal English phrase as a suffixed string or integer.

    Negative prefixes and hyphenated forms are accepted. Invalid input returns
    ``None``. Thousands separators apply only when ``to_num`` is true.
    """
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

    def _from_decimal_string(value):
        whole_str, decimal_str = value.split(".", 1)
        if not whole_str or not decimal_str or not decimal_str.isdigit():
            return None
        whole_part = _from_int(int(whole_str))
        if whole_part is None:
            return None
        digit_words = (
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
        decimal_words = " ".join(digit_words[int(digit)] for digit in decimal_str)
        return f"{whole_part} point {decimal_words}"

    try:
        n_str = str(n).strip()

        if "." in n_str:
            return _from_decimal_string(n_str)
        else:
            return _from_int(int(n_str))

    except (ValueError, TypeError):
        return None


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
    """Return the English ordinal suffix for an integer-like value."""
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
    """Extract numeric values from text in source order.

    Digit, ordinal, and English word forms are recognized. A leading negative
    indicator applies only to the first value. One match is returned as an
    integer; multiple matches are returned as a list.
    """
    if not s:
        return None

    is_negative = False
    string = s.strip().lower()
    if string.startswith("negative "):
        is_negative = True
        string = string.replace("negative ", "", 1)
    elif string.startswith("minus "):
        is_negative = True
        string = string.replace("minus ", "", 1)

    tokens = __parseNumericToken(
        s, first_only=__switch(allnum), wrap_single=True
    )  # Token parsing uses the inverse option, ``first_only``.
    if not tokens:
        return None

    def _check_and_return(num):
        return num if isinstance(num, int) else None

    funcs_and_kwargs = [
        (ordinalWordsToInt, {"to_num": True}),
        (stringToInt, {"to_str": False}),
        (wordsToInt, {}),
    ]

    parsed_numbers = []
    for token in tokens:
        for func, kwargs in funcs_and_kwargs:
            result = func(token, **kwargs)
            number = _check_and_return(result)
            if number is not None:
                if is_negative and not parsed_numbers:
                    number = -abs(number)
                parsed_numbers.append(number)
                break

    if not parsed_numbers:
        return None
    return parsed_numbers[0] if len(parsed_numbers) == 1 else parsed_numbers


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
    """Append the correct ordinal suffix to an integer."""
    return f"{n}{ordinalSuffix(n)}"


def _ensure_int(x: NumLike) -> int:
    """Coerce an integer, digit string, or ordinal numeral to an integer."""
    if isinstance(x, int):
        return x

    if str(x).isdigit():
        return int(x)

    maybe = stringToInt(str(x))
    if maybe is None:
        return None
    return maybe


def _convert_numeric_representation(value: NumLike, from_rep: Rep, to_rep: Rep) -> NumLike:
    """Convert ``value`` between canonical representation identifiers."""
    if from_rep == to_rep:
        return value

    # Normalize every source representation through an integer value.
    if from_rep == "CardinalWord":
        base_int = wordsToInt(str(value))
    elif from_rep == "CardinalNumber":
        base_int = _ensure_int(value)
    elif from_rep == "OrdinalWord":
        base_int = ordinalWordsToInt(str(value), to_num=True)
    elif from_rep == "OrdinalNumber":
        base_int = _ensure_int(value)
    elif from_rep == "RomanNumeral":
        base_int = romanToInt(str(value))
    else:
        return None

    if base_int is None:
        return None

    if to_rep == "CardinalWord":
        return intToWords(base_int)
    elif to_rep == "CardinalNumber":
        return base_int
    elif to_rep == "OrdinalWord":
        return intToOrdinalWords(base_int)
    elif to_rep == "OrdinalNumber":
        return _cardinal_number_to_ordinal_number(base_int)
    elif to_rep == "RomanNumeral":
        return intToRoman(base_int)
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
    """Detect and convert the five supported numeric representations."""

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

        s = str(value).strip().lower()

        # Detection order resolves forms that could otherwise be interpreted as words.
        if _ORD_SUFFIX_RE.match(s) and stringToInt(s) is not None:
            return "Ordinal Number"

        if _DIGIT_ONLY_RE.match(s):
            return "Cardinal Number"

        if romanToInt(s) is not None:
            return "Roman Numeral"

        if ordinalWordToCardinalNum(s) is not None:
            return "Ordinal Word"

        if cardinalWordToCardinalNum(s) is not None:
            return "Cardinal Word"

        return None

    @classmethod
    def to_type(cls, value, target=None, *, as_str=False):
        """Convert ``value`` to ``target`` or return its detected type.

        Raises ``ValueError`` when the source cannot be detected, the target is
        unknown, or the requested conversion is unsupported.
        """
        src = cls.num_type(value)
        if src is None:
            raise ValueError(f"Cannot determine representation of {value!r}")

        target = cls._canon(target)

        if target is None or target == src:
            return src if target is None else value

        try:
            source_rep = cls._DISPLAY_TO_REP[src]
            target_rep = cls._DISPLAY_TO_REP[target]
        except KeyError as exc:
            raise ValueError(f"Unknown representation: {exc.args[0]!r}") from exc
        result = _convert_numeric_representation(value, source_rep, target_rep)
        if result is None:
            raise ValueError(f"Cannot convert {value!r} from {src} to {target}")

        if as_str and isinstance(result, int):
            result = str(result)
        return result


_numbers = __NumericConverter()


def Type(value):
    """Return the detected numeric representation for ``value``."""
    return _numbers.num_type(value)


def Cast(value, target=None, *, as_str=False):
    """Convert ``value`` to a supported numeric representation."""
    return _numbers.to_type(value, target, as_str=as_str)


# Copy method metadata without replacing the public wrapper names.
custom_assignments = tuple(
    attr for attr in WRAPPER_ASSIGNMENTS if attr not in ("__name__", "__qualname__")
)

update_wrapper(Cast, __NumericConverter.to_type, assigned=custom_assignments)
update_wrapper(Type, __NumericConverter.num_type, assigned=custom_assignments)


__all__ = [
    # Core conversion functions
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
]
