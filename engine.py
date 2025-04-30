# -*- coding: utf-8 -*-

#
# DOYDL's Symbolic Integer Representation Engine — numbr
#
# The `numbr` module implements a formalized system for parsing, classifying,
# and transforming symbolic representations of integers. Designed to support
# natural language processing (NLP) pipelines, knowledge extraction, and
# symbolic reasoning, it provides a deterministic interface for converting
# between cardinal words, ordinal phrases, Roman numerals, and standard digit
# forms.
#
# All conversions are unambiguous and invertible over ℤ ∩ [–10²⁴, 10²⁴), with
# parsing grammars tailored to the structure and semantics of English number
# words. This system is well-suited for use in contexts where numeric meaning
# must be inferred from or rendered into language — such as automated
# annotation, question answering, legal text processing, and mathematical dialogue.
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

"""
This module constitutes the core semantic engine for parsing, normalizing,
and interconverting between symbolic representations of natural numbers.
It is intended for use in computational linguistics, formal reasoning systems,
and symbolic data extraction, where unambiguous interpretation of numeric
tokens is essential.

The functions defined herein reduce numerically-expressive strings to canonical
integer values (ℤ), and emit deterministic re-renderings in various notational
conventions. All routines operate under the assumption that numbers exist in
discrete representation classes, each with fixed grammar and semantics.

────────────────────────────────────────────────────
Typology of Numeric Representations
────────────────────────────────────────────────────
We define five principal forms of symbolic integers, treated as disjoint
syntactic categories with a shared underlying value domain ℤ⁺:

┍━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┑
│ Example │              Type             │                             Description                       │
┝━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┥
│   four  │  Cardinal number (word form)  │ English lexeme expressing absolute magnitude (e.g., "four").  │
│    4    │ Cardinal numeral (digit form) │ Decimal numeral expressing cardinality (e.g., 4).             │
│  fourth │   Ordinal number (word form)  │ Lexical form denoting position or rank (e.g., "fourth").      │
│   4th   │  Ordinal numeral (digit form) │ Arabic numeral with ordinal suffix (e.g., "4th").             │
│    IV   │         Roman numeral         │ Additive-subtractive Roman symbol encoding the value 4.       │
┕━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┙

Each representation class maps injectively to ℤ, up to a well-defined maximum
(bounded here at 10²⁴). Parsing functions serve as partial functions
ρ : Σ → ℤ, while rendering functions act as canonical inverse maps
σ : ℤ → Σ, where Σ ⊂ strings conforming to the target syntax.

This module defines no ambiguity: every accepted input resolves to a single
integer, and each output form is deterministic and linguistically valid.

────────────────────────────────────────────────────
Mathematical Context and Use
────────────────────────────────────────────────────
This engine may be embedded in pipelines involving:
    • Rule-based document analysis (contracts, forms, regulations)
    • Natural language understanding (token to value extraction)
    • Human-machine symbolic interfacing (voice agents, formal dialogs)
    • Language-adjacent theorem provers or educational tools

The system prioritizes:
    • Deterministic transformation
    • Invertible encoding/decoding
    • Linguistic fidelity to natural English syntax
    • Algorithmic tractability: all transformations are O(n)

No inference is performed. The system relies on surface forms, not contextual
semantics. As such, "eleven" parses to 11 regardless of nearby tokens.

This module forms the computational foundation upon which higher-level
abstractions (e.g., type guessing, inference, semantic tagging) may be layered.
"""

import re
import inspect
from typing import Literal, Union, Optional, Dict
from functools import reduce, update_wrapper, WRAPPER_ASSIGNMENTS


Rep = Literal["CardinalWord", "CardinalNumber", "OrdinalWord", "OrdinalNumber"]
NumLike = Union[int, str]

## Module-Level Constants & Dictionaries
##━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Matches spelled-out numbers, including cardinal and ordinal forms.
_NUM_ORDINAL_WRDS_RE = (
    r'zero|one|two|three|four|five|six|seven|eight|nine|ten|'
    r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|'
    r'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|'
    r'hundred|thousand|million|billion|trillion|quadrillion|quintillion|'
    r'first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|'
    r'eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|'
    r'eighteenth|nineteenth|twentieth|thirtieth|fortieth|fiftieth|sixtieth|'
    r'seventieth|eightieth|ninetieth|hundredth|thousandth|millionth|billionth|'
    r'trillionth|quadrillionth|quintillionth'
)
# # Matches entire spelled-out numbers, allowing hyphenated and space-separated formats.
# # Also accommodates "and" usage within numbers (e.g., "one hundred and twenty").
_NUM_WORDS_RE = (
    r'\b(?:'
    + _NUM_ORDINAL_WRDS_RE
    + r')(?:[-\s]+(?:and[-\s]+)?(?:'
    + _NUM_ORDINAL_WRDS_RE
    + r'))*\b'
)

# Basic unit digits (1-9) as words.
_UNIT_DIGITS_WORDS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

# Multiples of ten (10-90) as words.
_TENS_MULTIPLES_WORDS = ["ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

# Special cases for numbers between 11 and 19.
_TEEN_NUMERALS_WORDS = ["eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]

# Maps ordinal words (e.g., "first", "second", "twentieth") to their corresponding numeric values.
_ORDINAL_MAPPING = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
    "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14,
    "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18,
    "nineteenth": 19, "twentieth": 20, "thirtieth": 30, "fortieth": 40,
    "fiftieth": 50, "sixtieth": 60, "seventieth": 70, "eightieth": 80,
    "ninetieth": 90, "hundredth": 100, "thousandth": 1000,
    "millionth": 1000000, "billionth": 1000000000,
    "trillionth": 1000000000000,
    "quadrillionth": 1000000000000000,
    "quintillionth": 1000000000000000000,
}

# Dictionary that maps spelled-out ordinal words to their corresponding cardinal form and ordinal suffix.
_WORD_BASED_PATTERNS_RE = {
    r'first$': ('one', 'st'),
    r'second$': ('two', 'nd'),
    r'third$': ('three', 'rd'),
    r'fourth$': ('four', 'th'),
    r'fifth$': ('five', 'th'),
    r'sixth$': ('six', 'th'),
    r'seventh$': ('seven', 'th'),
    r'eighth$': ('eight', 'th'),
    r'ninth$': ('nine', 'th'),
    r'tenth$': ('ten', 'th'),
    r'eleventh$': ('eleven', 'th'),
    r'twelfth$': ('twelve', 'th'),
    r'thirteenth$': ('thirteen', 'th'),
    r'fourteenth$': ('fourteen', 'th'),
    r'fifteenth$': ('fifteen', 'th'),
    r'sixteenth$': ('sixteen', 'th'),
    r'seventeenth$': ('seventeen', 'th'),
    r'eighteenth$': ('eighteen', 'th'),
    r'nineteenth$': ('nineteen', 'th'),
    r'twentieth$': ('twenty', 'th'),
    r'thirtieth$': ('thirty', 'th'),
    r'fortieth$': ('forty', 'th'),
    r'fiftieth$': ('fifty', 'th'),
    r'sixtieth$': ('sixty', 'th'),
    r'seventieth$': ('seventy', 'th'),
    r'eightieth$': ('eighty', 'th'),
    r'ninetieth$': ('ninety', 'th'),
    r'hundredth$': ('hundred', 'th'),
    r'thousandth$': ('thousand', 'th'),
    r'millionth$': ('million', 'th'),
    r'billionth$': ('billion', 'th'),
    r'trillionth$': ('trillion', 'th'),
    r'quadrillionth$': ('quadrillion', 'th'),
    r'quintillionth$': ('quintillion', 'th'),
}

# Mapping for number multipliers used to scale values.
_MULTIPLIERS = {
    "hundred": 100,
    "thousand": 1000,
    "million": 1000000,
    "billion": 1000000000,
    "trillion": 1000000000000,
    "quadrillion": 1000000000000000,
    "quintillion": 1000000000000000000,
}

# Maps individual Roman numeral symbols to their corresponding integer values based on the standard numeral system.
_ROMAN_NUMERAL_MAPPING = {
    'I': 1, 'V': 5, 'X': 10, 'L': 50, 
    'C': 100, 'D': 500, 'M': 1000
}

# This regex pattern ensures strict validation of Roman numerals.
# It follows the standard Roman numeral rules and supports numbers from 1 (I) to 3999 (MMMCMXCIX).
# The pattern is divided into four groups:
#  - (M{0,3})    → Matches 0 to 3 occurrences of 'M' (1000s place).
#  - (CM|CD|D?C{0,3}) → Matches 900 (CM), 400 (CD), or up to 3 'C' after optional 'D' (100s place).
#  - (XC|XL|L?X{0,3}) → Matches 90 (XC), 40 (XL), or up to 3 'X' after optional 'L' (10s place).
#  - (IX|IV|V?I{0,3}) → Matches 9 (IX), 4 (IV), or up to 3 'I' after optional 'V' (1s place).
_ROMAN_NUMERAL_RE = r"^(M{0,3})(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"

# List of common currency symbols from around the world
_CURRENCY_SYMBOLS = [
    r"$",   # US Dollar
    r"€",   # Euro
    r"£",   # British Pound Sterling
    r"¥",   # Japanese Yen / Chinese Yuan
    r"₹",   # Indian Rupee
    r"₩",   # South Korean Won
    r"₽",   # Russian Ruble
    r"R$",  # Brazilian Real
    r"₺",   # Turkish Lira
    r"฿",   # Thai Baht
    r"₫",   # Vietnamese Dong
    r"₱",   # Philippine Peso
    r"₴",   # Ukrainian Hryvnia
    r"₸",   # Kazakhstani Tenge
    r"֏",   # Armenian Dram
    r"₦",   # Nigerian Naira
    r"₵",   # Ghanaian Cedi
    r"Br",  # Belarusian Ruble / Ethiopian Birr
    r"₾",   # Georgian Lari
    r"₪",   # Israeli Shekel
    r"R",   # South African Rand
    r"HK$", # Hong Kong Dollar
    r"S$",  # Singapore Dollar
    r"RM",  # Malaysian Ringgit
    r"Rp",  # Indonesian Rupiah
    r"Kč",  # Czech Koruna
    r"zł",  # Polish Zloty
    r"kr",  # Scandinavian Krone (Denmark, Norway, Sweden)
    r"Ft",  # Hungarian Forint
    r"lei", # Romanian Leu
    r"лв",  # Bulgarian Lev
    r"дин", # Serbian Dinar
    r"kn",  # Croatian Kuna
    r"ден", # Macedonian Denar
    r"L",   # Albanian Lek
    r"Br",  # Repeated for Belarusian Ruble / Ethiopian Birr
    r"S/.", # Peruvian Sol
    r"CHF"  # Swiss Franc
]

# Match ordinal numbers in digit form with suffix (e.g., "1st", "42nd", "103rd")
_ORD_SUFFIX_RE = re.compile(r"^\d+(st|nd|rd|th)$", re.IGNORECASE)

# Match strings that contain digits only (e.g., "123", "4567") — no signs, decimals, or commas
_DIGIT_ONLY_RE = re.compile(r"^\d+$")

# Matches digit-based numbers (e.g., 1,234.56 or -42)
_DIGIT_NUMBER_RE = re.compile(r'-?\d+(?:,\d{3})*(?:\.\d+)?')

# Matches a comma (used for cleanup after matching)
_COMMA_RE = re.compile(r',')

# Captures any non-digit characters at the beginning and end of a numeric string.
# Groups:
#   1. Prefix  (e.g. currency symbol, quote)
#   2. Suffix  (e.g. unit, symbol, trailing chars)
_NUM_STR_BOUNDARY_RE = re.compile(r"(^\D*)(?:[\d,.]+)?(\D*$)")

# This pattern breaks up compound number phrases (e.g., "twenty-one" or "one hundred and five")
_HYPHEN_OR_SPACE_RE = re.compile(r"[\s-]+")

# Matches the final word token at the end of a string
_LAST_WORD_RE = re.compile(r'\b(\w+)\b$')

# Removes the final word token (and any space before it) from the end of a string
_STRIP_LAST_WORD_RE = re.compile(r'\s*\b\w+\b$')

# Matches a string of optional negative sign followed by digits only
_PURE_DIGITS_RE = re.compile(r'^-?\d+$')
    
# Detects mixed numeric strings starting with a digit and ending in letters
_DIGIT_THEN_LETTER_RE = re.compile(r'^\d.*[a-zA-Z]$')    
    
# Normalizes label strings by removing spaces and underscores
_SPACE_UNDERSCORE_RE = re.compile(r"[ _]+")    
    
# A complete list of spelled-out cardinal numbers used for token splitting.
# Includes "zero", unit digits, teen numbers, and multiples of ten.
_CARDINAL_WORDS = ['zero', *_UNIT_DIGITS_WORDS, *_TEEN_NUMERALS_WORDS, *_TENS_MULTIPLES_WORDS]

# A list of all recognized ordinal words (e.g., "first", "twentieth").
# Derived from the _ORDINAL_MAPPING dictionary.
_ORDINAL_WORDS = list(_ORDINAL_MAPPING.keys())

# Matches a hyphen between two valid number words (e.g., "twenty-first"),
# so that compound forms can be safely rewritten with a space for parsing.
# This facilitates downstream processing of multi-word ordinals as separate tokens.
_HYPHEN_BETWEEN_NUMBER_WORDS_RE = re.compile(
    rf'\b({"|".join(_CARDINAL_WORDS + _ORDINAL_WORDS)})-({"|".join(_CARDINAL_WORDS + _ORDINAL_WORDS)})\b',
    flags=re.IGNORECASE
)
    
    
    
## Helper Functions
##━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# String Parsing & Tokenization
#────────────────────────────────────────────────────────────────────────────
def __parseNumericToken(s: str, first_only: bool = True, wrap_single: bool = False):
    """
    Finds spelled-out or digit-based tokens in a string and returns
    either the first match or all.

    This function searches for numeric tokens in two ways:
      1. Digit-based (e.g., '42', '1,234', '2.50')
      2. Spelled-out (e.g., 'twenty-five', 'third')
    """
    def _tokenize_digit(text: str, first_only: bool = True):
        """
        Finds digit-based tokens in a string, including optional decimals and commas.
        """
        matches = list(_DIGIT_NUMBER_RE.finditer(text))
        if not matches:
            return None if first_only else []

        # Convert each match to a string, removing commas
        found = [_COMMA_RE.sub('', m.group(0)) for m in matches]

        return [found[0]] if first_only else found
       
    def _tokenize_alpha(text: str, first_only: bool = True):
        """
        Finds spelled-out numbers or ordinals in a string, using _NUM_WORDS_RE.
        """
        matches = list(re.finditer(_NUM_WORDS_RE, text, re.IGNORECASE))
        if not matches:
            return None if first_only else []

        # Extract each spelled-out token
        found = [text[m.start():m.end()] for m in matches]

        if first_only:
            return [found[0]]
        else:
            return found
    
    if not s:
        return None if first_only else []

    # Get all digit-based tokens
    digit_tokens = _tokenize_digit(s, first_only=False)  # get all
    # Get all spelled-out tokens
    alpha_tokens = _tokenize_alpha(s, first_only=False)  # get all

    # Combine results
    combined = []
    if digit_tokens:
        combined += digit_tokens
    if alpha_tokens:
        combined += alpha_tokens

    if not combined:
        return None if first_only else []

    # If user wants only the first match, return the first item
    if first_only:
        result = combined[0]
        return [result] if wrap_single else result  # Wrap in list if requested
    else:
        return combined
   
def __parseRomanNumeral(s: str):
    """
    Parses a Roman numeral string and converts it into an integer.

    This function ensures the Roman numeral follows valid ordering rules and
    correctly applies subtractive notation.
    """
    if not s or not re.match(_ROMAN_NUMERAL_RE, s):
        return None

    num, prev = 0, 0

    # Convert from right to left
    for char in reversed(s):
        curr = _ROMAN_NUMERAL_MAPPING[char]
        num = num - curr if curr < prev else num + curr
        prev = curr

    return num if num > 0 else None  # Ensure non-zero positive value
   
def __validate_numstr(n: Union[int, float, str], clean: bool = False) -> Optional[str]:
    """
    Validates whether the input contains a valid numeric value after removing 
    currency symbols and commas.

    This function converts the input to a string, removes known currency symbols 
    and commas, and checks if the remaining content is a valid numeric value.
    """	
    numstr = str(n)
    clean_numstr = reduce(lambda s, sign: s.replace(sign, ""), _CURRENCY_SYMBOLS, numstr).replace(",", "")
    clean_numstr = clean_numstr.replace("+", "").replace("-", "")    
    # Check if the string is a valid number
    try:
        float(clean_numstr)  # Check for validity
    except ValueError:
        return None    
    return clean_numstr if clean else n

# Boolean & Utility Functions
#────────────────────────────────────────────────────────────────────────────
def __switch(x):
    """
    Toggle a boolean value.

    Parameters:
    ──────────────────────────        	
        x (bool): The boolean value to switch.

    Returns:
    ──────────────────────────        	
        bool: The opposite of the input boolean value.
    """
    return not x



## General Formatting & Numeric Processing
##━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# These are intermediate utility functions for number formatting
#────────────────────────────────────────────────────────────────────────────
def insertSep(n: Union[int, float, str], sep: str = ",") -> Optional[str]:
    """
    Formats a number by inserting a specified thousands separator while preserving 
    any non-numeric characters (e.g., currency symbols, quotes).

    This function extracts the numeric portion of the input, formats it with 
    the specified thousands separator, and then restores the original non-numeric 
    characters at the beginning and end.

    Parameters:
    ──────────────────────────     	
        n (str, int, or float): The input number, which may contain non-numeric characters.
        sep (str, optional): The separator to use for thousands grouping. Default is a comma (",").

    Returns:
    ──────────────────────────     
        str: The formatted number with thousands separators, retaining any original non-numeric characters.
        None: If the input does not contain a valid number.
    """
    num_str = str(n)  # Ensure the input is a string
    num_str = " ".join(num_str.split()) 
    
    # Extract non-numeric characters at the beginning and end
    match = _NUM_STR_BOUNDARY_RE.match(num_str)
    if not match:
        return None

    prefix, suffix = match.groups()

    # Check if the string is a valid number
    if not __validate_numstr(num_str):
        return None
    else:
        cleaned_numeric_part = __validate_numstr(num_str, True)
        
    # Determine if the number contains a decimal
    if '.' in cleaned_numeric_part:
        integer_part, decimal_part = cleaned_numeric_part.split('.')
        integer_part = int(integer_part)  # Convert to int to remove leading zeros if any
    else:
        integer_part, decimal_part = int(cleaned_numeric_part), None

    # Format the integer part with the specified separator
    formatted_integer_part = f"{integer_part:,}".replace(",", sep)

    # Reassemble the formatted number with the original non-numeric characters
    if decimal_part is not None:
        formatted_number = f"{formatted_integer_part}.{decimal_part}"
    else:
        formatted_number = formatted_integer_part

    return f"{prefix}{formatted_number}{suffix}"

def formatDecimal(n: Union[int, float, str], place: int = 5) -> Optional[str]:
    """
    Formats a given number to ensure it has a fixed number of decimal places.

    Parameters:
    ──────────────────────────     	
        n (Union[int, float, str]): The input number as a string, integer, or float.
        place (int, optional): The number of decimal places to enforce. Default is **5**.

    Returns:
    ──────────────────────────     	
        Optional[str]: The formatted number with the specified decimal places.
        Returns **None** if the input is invalid.
    """
    # Ensure the input is a string
    n = str(n)
    n = " ".join(n.split())     
    
    # Check if the string is a valid number
    if not __validate_numstr(n):
        return None
       
    place = int(place)    

    if '.' not in n:
        n = f'{n}.{str(10**place).replace("1", "")}'        
        
    integer_part, decimal_part = n.split('.')
    if len(decimal_part) < place:
        decimal_part = decimal_part.ljust(place, '0')
    elif len(decimal_part) > place:
        decimal_part = decimal_part[:place]
        
    return f"{integer_part}.{decimal_part}"




## Main Conversion Logic
##━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# WORD-BASED NUMBER TO INTEGER: CONVERT CARDINAL NUMBERS IN WORD FORM (E.G., "TWENTY-FIVE") TO INTEGERS
#───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def wordsToInt(s: str, thousands_sep: bool = False, sep: str = ","):
    """
    Converts a spelled-out number in English into its integer equivalent.

    This function processes cardinal numbers written in words and returns their 
    corresponding integer values. It supports numbers up to quintillions, including 
    multi-word formats and hyphenated numbers (e.g., "twenty-one"). Negative numbers 
    are also recognized if prefixed with "negative" or "minus".

    The function can optionally format the output with thousands separators for better readability.

    Parameters:
    ──────────────────────────     	
        s (str): A string representing a number in English (e.g., "two hundred and fifty-six").
        thousands_sep (bool, optional): If True, formats the output with a separator (default is False).
        sep (str, optional): The character used as a thousands separator when `thousands_sep` is True (default is ',').

    Returns:
    ──────────────────────────     	
        int or None: The integer representation of the input if successfully parsed, otherwise None.

    Notes:
    ──────────────────────────     	
		    - Does not process ordinal numbers (e.g., "first", "twenty-first").
		    - Assumes grammatically correct number formatting.
		    - Ignores the word "and" as it does not affect numerical value (e.g., "one hundred and five" = "one hundred five").
		    - Recognizes and processes compound words (e.g., "forty-two", "ninety-nine").
		    - If an unrecognized word is found, the function returns `None`.
    """
    if not s:
        return None

    # Detect negative at the front
    is_negative = False
    s = s.strip().lower()
    if s.startswith("negative "):
        is_negative = True
        s = s.replace("negative ", "", 1)
    elif s.startswith("minus "):
        is_negative = True
        s = s.replace("minus ", "", 1)

    # If it's an ordinal phrase, we skip it by returning None
    token = __parseNumericToken(s)
    if token and ordinalWordsToInt(token):
        return None

    units_dict = {word: i + 1 for i, word in enumerate(_UNIT_DIGITS_WORDS)}
    tens_dict = {word: (i + 1) * 10 for i, word in enumerate(_TENS_MULTIPLES_WORDS)}
    teens_dict = {word: i + 11 for i, word in enumerate(_TEEN_NUMERALS_WORDS)}

    # Pre-compute some compound forms (e.g. "twenty-hundred" though not standard, etc.)
    for mult in _MULTIPLIERS:
        for word_list in [_UNIT_DIGITS_WORDS, _TENS_MULTIPLES_WORDS]:
            for w in word_list:
                compound = w + "-" + mult
                if w in tens_dict:
                    units_dict[compound] = tens_dict[w] * _MULTIPLIERS[mult]
                else:
                    units_dict[compound] = units_dict[w] * _MULTIPLIERS[mult]

    # Split out hyphens/spaces, skip "and" tokens
    words_list = _HYPHEN_OR_SPACE_RE.split(s)
    words_list = [w for w in words_list if w != "and"]  # skip "and"

    number = 0
    temp_number = 0

    for word in words_list:
        if word in units_dict:
            temp_number += units_dict[word]
        elif word in teens_dict:
            temp_number += teens_dict[word]
        elif word in tens_dict:
            temp_number += tens_dict[word]
        elif word in _MULTIPLIERS:
            # For 'hundred', multiply the existing temp_number by 100
            # For thousand/million/etc., multiply and then "commit" to number
            temp_number *= _MULTIPLIERS[word]
            if _MULTIPLIERS[word] >= 1000:
                number += temp_number
                temp_number = 0
        else:
            # If unknown word, fail
            return None

    number += temp_number

    if number == 0:
        return None

    if is_negative:
        number = -number        
    if thousands_sep:
        number = insertSep(number, sep=sep)
    return number




# WORD-BASED NUMBER TO INTEGER: CONVERT ORDINAL NUMBERS IN WORD FORM (E.G., "TWENTY-FIRST") TO INTEGERS
#───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def ordinalWordsToInt(s: str, to_num: bool = False, thousands_sep: bool = False, sep: str = ","):
    """
    Converts a spelled-out ordinal number in English to its numeric form.

    This function processes ordinal words and converts them into either a numeric 
    string with a suffix (e.g., "1st", "21st") or an integer (if `to_num=True`). 
    It handles multi-word ordinals, hyphenated ordinals, and recognizes negative 
    ordinal numbers when prefixed with "negative" or "minus".

    Parameters:
    ──────────────────────────      	
        s (str): A string representing an ordinal number in English 
                             (e.g., "twenty-first", "hundredth").
        to_num (bool, optional): If True, returns the ordinal as an integer instead 
                                 of a string with a suffix. Default is False.
        thousands_sep (bool, optional): If True, formats the output with a separator (default is False).
        sep (str, optional): The character used as a thousands separator when `thousands_sep` is True (default is ',').                                 

    Returns:
    ──────────────────────────          	
        str or int or None: The numeric ordinal representation as a string with a suffix 
                            (e.g., "21st") or as an integer (if `to_num=True`), or 
                            None if parsing fails.
    """
    # # Define lists of spelled-out cardinal and ordinal numbers and combine both lists
    # cardinal_numbers = ['zero', *_UNIT_DIGITS_WORDS, *_TEEN_NUMERALS_WORDS, *_TENS_MULTIPLES_WORDS]
    # ordinal_numbers = list(_ORDINAL_MAPPING.keys())
    # number_words = cardinal_numbers + ordinal_numbers
    # 
    # # Build a regex pattern that matches a hyphen only if it is between two valid number words
    # pattern = r'\b(' + '|'.join(number_words) + r')-(' + '|'.join(number_words) + r')\b'
    
    # Replaces hyphens only if they are between spelled-out cardinal or ordinal number words.    
    # s = re.sub(pattern, r'\1 \2', s, flags=re.IGNORECASE)
    s = _HYPHEN_BETWEEN_NUMBER_WORDS_RE.sub(r'\1 \2', s)    

    if not s:
        return None

    # Detect negative at the front (rare for ordinals, but let's allow it)
    is_negative = False
    s = s.strip().lower()
    if s.startswith("negative "):
        is_negative = True
        s = s.replace("negative ", "", 1)
    elif s.startswith("minus "):
        is_negative = True
        s = s.replace("minus ", "", 1)

    def _strip_num(ordinal_number):
        """
        From '21st', '32nd', etc. -> integer
        """
        ordinal_match = re.match(r'^-?(\d+)(st|nd|rd|th)$', ordinal_number)
        return int(ordinal_match.group(1)) if ordinal_match else None

    def _simple_ord(tok):
        """
        Simple single-word ordinal: 'first' -> '1st', 'second' -> '2nd', etc.
        """
        # Attempt direct mapping
        if tok in _ORDINAL_MAPPING:
            base_val = _ORDINAL_MAPPING[tok]
            suffix = ordinalSuffix(base_val)  # "st", "nd", "rd", "th"
            # Return with or without numeric form
            if to_num:
                return -base_val if is_negative else base_val
            else:
                return f"{'-' if is_negative else ''}{base_val}{suffix}"
        return None

    def _complex_ord(tok):
        """
        Handle multi-word ordinals: 'twenty first' -> '21st', 'one hundred and first' -> '101st'
        """
        # We'll try removing the last word as an ordinal ending, then parse the front as cardinal
        last_word_match = _LAST_WORD_RE.search(tok)
        if not last_word_match:
            return None
        last_word = last_word_match.group()

        # Everything except the last word
        front_string = _STRIP_LAST_WORD_RE.sub('', tok).strip()

        # Convert front part to integer (cardinal)
        front_number = wordsToInt(front_string)

        if front_number is None:
            return None

        # Then interpret the last word as a single-word ordinal
        last_ordinal_num = _simple_ord(last_word)
        if last_ordinal_num is None:
            return None

        # If last_ordinal_num is integer (to_num=True) or a string with suffix
        if isinstance(last_ordinal_num, int):
            # If it is an integer, just sum
            complete = front_number + last_ordinal_num
            return complete if not is_negative else -complete
        else:
            # Otherwise it's something like "21st"
            # Extract the integer portion from "21st"
            stripped_val = _strip_num(last_ordinal_num)
            if stripped_val is None:
                return None
            complete = front_number + stripped_val
            final_suffix = ordinalSuffix(complete)
            sign = "-" if is_negative else ""
            return f"{sign}{complete}{final_suffix}"

    # Parse to check if single or multiple words
    # We'll use parseNumericToken to see if there's a direct token
    # then handle single vs multi logic
    token = __parseNumericToken(s)
    if not token:
        return None

    # If more than one word, attempt complex
    if len(token.split()) > 1:
        check_number = _complex_ord(token)
        if check_number is not None:
            if to_num and thousands_sep:
                return insertSep(check_number, sep=sep)
            else:
                return check_number    
    else:
        # single word    	
        check_number = _simple_ord(token)
        if check_number is not None:
            if to_num and thousands_sep:
                return insertSep(check_number, sep=sep)
            else:
                return check_number
    return None

# WORD-BASED NUMBER TO INTEGER: CONVERT NUMERIC STRINGS (E.G., "1,234", "42ND") TO INTEGERS
#───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def stringToInt(s: str, to_str: bool = False, thousands_sep: bool = False, sep: str = ","):
    """
    Converts a numeric string into an integer or string representation.

    This function processes numeric strings containing digits, optionally formatted 
    with commas (e.g., "1,234"), and ordinal suffixes (e.g., "2nd"). It also handles 
    negative numbers prefixed with "negative" or "minus". The function returns an 
    integer by default but can return a string representation if `to_str=True`.

    Parameters:
    ──────────────────────────       	
        s (str): A numeric string, potentially containing commas or ordinal suffixes.
        to_str (bool, optional): If True, returns the result as a string instead of an integer. 
                                 Default is False.
        thousands_sep (bool, optional): If True, formats the output with a separator (default is False).
        sep (str, optional): The character used as a thousands separator when `thousands_sep` is True (default is ',').                                 

    Returns:
    ──────────────────────────       	
        int or str or None: The parsed integer or its string representation (if `to_str=True`). 
                            Returns None if parsing fails.
    """
    if not s:
        return None

    # Detect negative at the front
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

    tokens = __parseNumericToken(number_str)
    if tokens and _PURE_DIGITS_RE.match(str(tokens)):
        val = int(tokens)
        val = -val if is_negative else val
        if thousands_sep and to_str:
            return insertSep(val, sep=sep)
        return str(val) if to_str else val    
    return None




# INTEGER TO WORD-BASED NUMBER: CONVERT INTEGER VALUES (E.G., 256) TO CARDINAL NUMBERS IN WORD FORM (E.G., "TWO HUNDRED FIFTY-SIX")
#───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def intToWords(n: Union[int, float], thousands_sep: bool = False):
    """
    Converts an integer or float into its spelled-out English words representation.

    This function transforms numerical values into their corresponding English 
    words. It supports both positive and negative numbers, including large values 
    up to quintillions. Additionally, it can handle floating-point numbers by 
    spelling out both the integer and decimal portions separately.

    If `thousands_sep=True`, large segments (e.g., thousands, millions, billions) 
    are separated by commas in the output.

    Parameters:
    ──────────────────────────       	
        n (int or float): The number to be converted to words.
        thousands_sep (bool, optional): If True, inserts commas between large segments 
                                 for better readability. Default is False.

    Returns:
    ──────────────────────────       	
        str or None: The spelled-out English representation of the number, or None 
                     if input is invalid.
    """
    def _from_int(x):
        if x == 0:
            return "zero"

        def one(num):
            switcher = {
                1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
                6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'
            }
            return switcher.get(num, '')

        def two_less_20(num):
            switcher = {
                10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen',
                15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen', 19: 'nineteen'
            }
            return switcher.get(num, '')

        def ten(num):
            switcher = {
                2: 'twenty', 3: 'thirty', 4: 'forty', 5: 'fifty',
                6: 'sixty', 7: 'seventy', 8: 'eighty', 9: 'ninety'
            }
            return switcher.get(num, '')

        def two(num):
            if not num:
                return ''
            elif num < 10:
                return one(num)
            elif num < 20:
                return two_less_20(num)
            else:
                tenner = num // 10
                rest = num % 10
                return ten(tenner) + ('-' + one(rest) if rest else '')

        def three(num):
            hundred = num // 100
            rest = num % 100
            if hundred and rest:
                return one(hundred) + ' hundred ' + two(rest)
            elif hundred and not rest:
                return one(hundred) + ' hundred'
            else:
                return two(rest)

        # Break the number into billions, millions, thousands, and the remainder
        # Extended to quintillions
        # We'll do repeated modulus and division:
        # e.g. 1,234,567,890,123 -> segments for trillions, billions, millions, thousands, rest
        # We'll store all segments in ascending order, then build from largest to smallest for readability.
        # For now, let's just go up to quintillions.
        abs_num = abs(x)

        quintillion = abs_num // 1000000000000000000
        remainder_q = abs_num % 1000000000000000000

        quadrillion = remainder_q // 1000000000000000
        remainder_quad = remainder_q % 1000000000000000

        trillion = remainder_quad // 1000000000000
        remainder_tril = remainder_quad % 1000000000000

        billion = remainder_tril // 1000000000
        remainder_bill = remainder_tril % 1000000000

        million = remainder_bill // 1000000
        remainder_mill = remainder_bill % 1000000

        thousand = remainder_mill // 1000
        remainder = remainder_mill % 1000

        segments = []
        if quintillion:
            segments.append(three(quintillion) + " quintillion")
        if quadrillion:
            segments.append(three(quadrillion) + " quadrillion")
        if trillion:
            segments.append(three(trillion) + " trillion")
        if billion:
            segments.append(three(billion) + " billion")
        if million:
            segments.append(three(million) + " million")
        if thousand:
            segments.append(three(thousand) + " thousand")
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

        # Attach negative sign if needed
        if x < 0:
            result = "negative " + result

        return result

    def _from_float(num):
        """
        Very basic approach to handle floats by splitting at the decimal.
        """
        whole_str, decimal_str = str(num).split(".")
        whole_part = _from_int(int(whole_str))
        # Convert each digit in the decimal part to words, or parse the entire decimal as an integer:
        # "45" -> "forty-five" or "four five"
        dec_int = int(decimal_str)
        decimal_words = _from_int(dec_int)

        return f"{whole_part} point {decimal_words}"

    try:
        # Clean up the input
        n_str = str(n).strip()

        # Handle float if decimal point exists
        if "." in n_str:
            return _from_float(float(n_str))
        else:
            return _from_int(int(n_str))

    except (ValueError, TypeError):
        return None
       

# INTEGER TO WORD-BASED NUMBER: CONVERT INTEGER VALUES (E.G., 21) TO ORDINAL NUMBERS IN WORD FORM (E.G., "TWENTY-FIRST")
#───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def intToOrdinalWords(n: int):
    """
    Converts an integer into its ordinal spelled-out English form.

    This function takes an integer and returns its ordinal representation in words.
    It correctly handles standard English transformations for ordinal numbers, 
    including irregular forms like "first", "second", "third", "twelfth", and 
    suffix changes for numbers ending in "-y" (e.g., "twenty" -> "twentieth").

    The function supports both positive and negative numbers.

    Parameters:
    ──────────────────────────       	
        n (int): The integer to be converted into ordinal words.

    Returns:
    ──────────────────────────       	
        str or None: The ordinal representation of the number as a string, 
                     or None if conversion fails.
    """
    try:
        n = int(str(n).strip())
    except (ValueError, TypeError):
        return None    
    
    words = intToWords(n, thousands_sep=False)
    if not words:
        return None

    # We'll split the spelled-out form, then transform the last word.
    # Note: This is a simplistic approach and might need special handling for multi-segment final words.
    word_parts = words.split()
    if not word_parts:
        return None

    # Identify the negative sign if it exists
    is_negative = False
    if word_parts[0] == "negative":
        is_negative = True
        word_parts = word_parts[1:]  # remove "negative"

    last_word = word_parts[-1]

    def _replace_end(full_word, old_end, new_end):
        return full_word[: -len(old_end)] + new_end if full_word.endswith(old_end) else full_word

    # We'll do a set of special transformations:
    # one -> first, two -> second, three -> third, etc.
    # This is a subset of patterns.
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
        word_parts[-1] = _replace_end(last_word, "y", "ieth") # e.g. "twenty" -> "twentieth", "thirty" -> "thirtieth"
    elif last_word.endswith("teen"):
        word_parts[-1] = _replace_end(last_word, "teen", "teenth") # e.g. "fourteen" -> "fourteenth"
    else:
        word_parts[-1] = word_parts[-1] + "th" # Generic

    if is_negative:
        return "negative " + " ".join(word_parts)
    else:
        return " ".join(word_parts)




# ORDINAL NUMBER UTILITIES: EXTRACT THE APPROPRIATE SUFFIX ("ST", "ND", "RD", "TH") FOR AN INTEGER
#───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def ordinalSuffix(n: Union[int, str]) -> str:
    """
    Determines the appropriate English ordinal suffix for a given integer.

    This function returns the correct ordinal suffix ("st", "nd", "rd", "th") 
    based on standard English rules. It properly accounts for special cases 
    where numbers ending in 11, 12, or 13 always take "th".

    Parameters:
    ──────────────────────────       	
        n (int): The integer for which to determine the ordinal suffix.

    Returns:
    ──────────────────────────       	
        str: The appropriate ordinal suffix ('st', 'nd', 'rd', or 'th').
    """
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


# ORDINAL NUMBER UTILITIES: REMOVE THE ORDINAL ENDING FROM A WORD-BASED NUMBER (E.G., "TWENTIETH" → "TWENTY")
#───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def stripOrdinalSuffix(s: str):
    """
    Strips the ordinal suffix from a spelled-out ordinal number, returning the base 
    cardinal form and the suffix separately.

    This function identifies and removes ordinal suffixes from spelled-out ordinal 
    numbers (e.g., "twentieth" → "twenty", "twenty-first" → "twenty-one"). It returns 
    a tuple containing the base cardinal number as a string and the ordinal suffix.

    Parameters:
    ──────────────────────────     	
        s (str): A spelled-out ordinal number (e.g., "seventh", "thirty-second").

    Returns:
    ──────────────────────────     	
        tuple or None: A tuple containing the base cardinal number (str) and its 
                       ordinal suffix (str), or None if no ordinal suffix is detected.
    """
    number_str = s
    suffix = None
    for pattern, (replacement, suffix_to_remove) in _WORD_BASED_PATTERNS_RE.items():
        if re.search(pattern, s, flags=re.IGNORECASE):
            suffix = suffix_to_remove
            number_str = re.sub(pattern, replacement, number_str, flags=re.IGNORECASE)
            break  # Stop at first match
    if suffix is None:
        return None
    return (number_str, suffix)




# GENERAL NUMBER EXTRACTION: IDENTIFY AND CONVERT ALL NUMERIC VALUES (CARDINAL OR ORDINAL) FROM A STRING
#───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def extractNumericValue(s: str, allnum: bool = True):
    """
    Extracts and converts all numeric values (cardinal or ordinal) from a string into a list of integers.
    
    This function searches for multiple numeric values, whether they are:
      - Digit-based (e.g., "42", "1,234")
      - Ordinals (e.g., "third", "42nd")
      - Spelled-out numbers (e.g., "twenty-five")

    If a negative indicator ("negative" or "minus") is present at the start of the string,
    it applies negativity only to the **first** detected number.

    Parameters:
    ──────────────────────────     	
        s (str): A string potentially containing multiple numeric values.
		    allnum (bool, optional): Determines whether to return **all** numeric matches or just the **first** one.
		        - `True` (default): Returns a list of all numbers found in the string.
		        - `False`: Returns only the first number found.
        
    Returns:
    ──────────────────────────     	
        list[int] or None:
            - A list of parsed integers if numeric values are found.
            - None if no numbers are detected.
    """
    if not s:
        return None

    # Handle negative at the start of the string
    is_negative = False
    string = s.strip().lower()
    if string.startswith("negative "):
        is_negative = True
        string = string.replace("negative ", "", 1)
    elif string.startswith("minus "):
        is_negative = True
        string = string.replace("minus ", "", 1)
    
    tokens = __parseNumericToken(s, first_only=__switch(allnum), wrap_single=True)  # Get all matches if allnum == True. The switch function swithes allnum boolen to False.    
    if not tokens:
        return None

    def _check_and_return(num):
        return num if isinstance(num, int) else None

    # Define functions to apply for conversion
    funcs_and_kwargs = [
        (ordinalWordsToInt, {'to_num': True}),
        (stringToInt, {'to_str': False}),
        (wordsToInt, {}),
    ]

    # Process all tokens
    parsed_numbers = []
    for token in tokens:
        for func, kwargs in funcs_and_kwargs:
            result = func(token, **kwargs)
            number = _check_and_return(result)
            if number is not None:
                # Apply negativity only to the first detected number
                if is_negative and not parsed_numbers:  # Only negate the **first** number found
                    number = -abs(number)
                parsed_numbers.append(number)
                break  # Stop trying other functions once parsed successfully

    # Return single integer if only one number is found, otherwise return list
    if not parsed_numbers:
        return None
    return parsed_numbers[0] if len(parsed_numbers) == 1 else parsed_numbers



# ROMAN NUMERALS: CONVERT ROMAN NUMERALS (E.G., "XIV") TO INTEGERS
#───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def romanToInt(s: str, to_str: bool = False):
    """
    Converts a Roman numeral string into its integer value.

    This function parses and converts valid Roman numeral strings into their 
    corresponding integer values while ensuring strict adherence to Roman numeral 
    rules. It handles both standard and subtractive notation (e.g., 'XIV' = 14, 
    'MCMXCIV' = 1994) and validates input to prevent incorrect sequences.

    Parameters:
    ──────────────────────────     	
    - s (*str*):  
      - A valid Roman numeral string (e.g., 'XIV', 'MCMXCIV').
    
    - to_str (*bool, optional*):  
      - If `True`, returns the result as a string instead of an integer.  
      - Default is `False`.

    Returns:
    ──────────────────────────     	
    - (*int | str | None*):  
      - The integer representation of the Roman numeral.  
      - If `to_str=True`, returns the value as a string.  
      - Returns `None` if the input is invalid.
    """
    num = __parseRomanNumeral(s)
    return str(num) if num is not None and to_str else num


# ROMAN NUMERALS: CONVERT ROMAN NUMERALS (E.G., "XIV") TO CARDINAL NUMBERS IN WORD FORM (E.G., "FOURTEEN") 
#───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def romanToWords(s: str):
    """
    Converts a Roman numeral string into its spelled-out English words representation.

    This function first converts a Roman numeral into an integer and then transforms 
    it into its full English word equivalent. It ensures strict adherence to Roman 
    numeral rules and returns a readable word-based representation.

    Parameters:
    ──────────────────────────     	
    - s (*str*):  
      - A valid Roman numeral string (e.g., 'XIV', 'MCMXCIV').

    Returns:
    ──────────────────────────     	
    - (*str | None*):  
      - The spelled-out English words for the given Roman numeral.  
      - Returns `None` if the input is invalid.
    """
    num = __parseRomanNumeral(s)
    return intToWords(num) if num is not None else None




## Low‑Level Helpers
##━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _cardinal_number_to_ordinal_number(n: int) -> str:
    """ 2 -> '2nd'  """
    return f"{n}{ordinalSuffix(n)}"

def _ensure_int(x: NumLike) -> int:
    """ Accepts int, str‑digit or str‑ordinal‑digit and returns int. """
    if isinstance(x, int):
        return x
    
    if str(x).isdigit(): # try plain digits first
        return int(x)
    
    maybe = stringToInt(str(x)) # try ordinal digits: '2nd' -> 2
    if maybe is None:
        # raise ValueError(f"Cannot coerce {x!r} to integer.")
        return None       
    return maybe


# Dispatcher
# ────────────────────────────────────────────────────────────────────────────────
def _convert_numeric_representation(
    value: NumLike,
    from_rep: Rep,
    to_rep:   Rep
) -> NumLike:
    """
    Convert *value* from one numeric representation to another.

    Parameters
    ----------
    value : int | str
        The literal to convert (e.g. "two", 2, "second", "2nd").
    from_rep : {"CardinalWord","CardinalNumber","OrdinalWord","OrdinalNumber"}
        Code for the input representation.
    to_rep   : {"CardinalWord","CardinalNumber","OrdinalWord","OrdinalNumber"}
        Code for the desired output representation.

    Returns
    -------
    int | str
        Converted value in the requested form.
    """
    if from_rep == to_rep:
        return value  # no‑op

    # ─── step 1: normalise input to an *integer* ───────────────────────────────
    if from_rep == "CardinalWord":                        # "two"  -> 2
        base_int = wordsToInt(str(value))
    elif from_rep == "CardinalNumber":                      # 2      -> 2
        base_int = _ensure_int(value)
    elif from_rep == "OrdinalWord":                      # "second" -> 2
        base_int = ordinalWordsToInt(str(value), to_num=True)
    elif from_rep == "OrdinalNumber":                      # "2nd"  -> 2
        base_int = _ensure_int(value)
    else:
        return None        

    if base_int is None:
        return None

    # ─── step 2: materialise requested representation ─────────────────────────
    if to_rep == "CardinalWord":                          # 2 -> "two"
        return intToWords(base_int)
    elif to_rep == "CardinalNumber":                        # 2 -> 2
        return base_int
    elif to_rep == "OrdinalWord":                        # 2 -> "second"
        return intToOrdinalWords(base_int)
    elif to_rep == "OrdinalNumber":                        # 2 -> "2nd"
        return _cardinal_number_to_ordinal_number(base_int)
    return None    




# FROM CARDINAL WORD: (E.G., "SEVEN")  
# ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def cardinalWordToCardinalNum(s: str):
    """
    Converts a cardinal number expressed in words into its numeric form.

    This function takes a spelled-out cardinal number (e.g., "two", "fifty") and 
    returns its corresponding integer representation (e.g., 2, 50).

    Parameters:
    ──────────────────────────
    - s (*str*):  
      - A cardinal number in word form (e.g., "three", "twenty-one").

    Returns:
    ──────────────────────────
    - (*int | None*):  
      - The equivalent integer, or `None` if the input is invalid.
    """
    return _convert_numeric_representation(s, "CardinalWord", "CardinalNumber")

def cardinalWordToOrdinalWord(s: str):
    """
    Converts a cardinal word into its ordinal word equivalent.

    This function takes a cardinal number in word form (e.g., "two") and returns 
    the corresponding ordinal word (e.g., "second").

    Parameters:
    ──────────────────────────
    - s (*str*):  
      - A valid cardinal word (e.g., "four", "eleven").

    Returns:
    ──────────────────────────
    - (*str | None*):  
      - The ordinal word form, or `None` if the input is invalid.
    """
    return _convert_numeric_representation(s, "CardinalWord", "OrdinalWord")

def cardinalWordToOrdinalNum(s: str):
    """
    Converts a cardinal word into its ordinal number form with a suffix.

    This function returns a string with the appropriate ordinal suffix 
    (e.g., "2nd", "21st") corresponding to a spelled-out cardinal number.

    Parameters:
    ──────────────────────────
    - s (*str*):  
      - A cardinal number in word form (e.g., "five", "twenty").

    Returns:
    ──────────────────────────
    - (*str | None*):  
      - The ordinal number with suffix, or `None` if parsing fails.
    """
    return _convert_numeric_representation(s, "CardinalWord", "OrdinalNumber")


# FROM CARDINAL NUMBER: (E.G., "7")  
# ────────────────────────────────────────────────────────────────────────────────
def cardinalNumToCardinalWord(n: int):
    """
    Converts a cardinal number into its spelled-out English word form.

    This function accepts either an integer or a numeric string (e.g., 2 or "2") 
    and returns the equivalent cardinal word (e.g., "two").

    Parameters:
    ──────────────────────────
    - n (*int | str*):  
      - A cardinal number as an integer or numeric string.

    Returns:
    ──────────────────────────
    - (*str | None*):  
      - The word form of the number, or `None` if input is invalid.
    """
    try:
        n = int(str(n).strip())
        return _convert_numeric_representation(n, "CardinalNumber", "CardinalWord")
    except (ValueError, TypeError):
        return None

def cardinalNumToOrdinalWord(n: int):
    """
    Converts a cardinal number into its ordinal word equivalent.

    Accepts a numeric value or string (e.g., 3 or "3") and returns 
    the corresponding ordinal word (e.g., "third").

    Parameters:
    ──────────────────────────
    - n (*int | str*):  
      - A cardinal number as an integer or string.

    Returns:
    ──────────────────────────
    - (*str | None*):  
      - The ordinal word form, or `None` if conversion fails.
    """
    try:
        n = int(str(n).strip())
        return _convert_numeric_representation(n, "CardinalNumber", "OrdinalWord")
    except (ValueError, TypeError):
        return None

def cardinalNumToOrdinalNum(n: int):
    """
    Converts a cardinal number into its ordinal numeric form with a suffix.

    Converts either a number or numeric string (e.g., 2 or "2") to its 
    ordinal string representation (e.g., "2nd").

    Parameters:
    ──────────────────────────
    - n (*int | str*):  
      - A cardinal number as integer or string.

    Returns:
    ──────────────────────────
    - (*str | None*):  
      - The formatted ordinal number, or `None` if input is invalid.
    """
    try:
        n = int(str(n).strip())
        return _convert_numeric_representation(n, "CardinalNumber", "OrdinalNumber")
    except (ValueError, TypeError):
        return None

# FROM ORDINAL WORD: (E.G., "SEVENTH")  
# ────────────────────────────────────────────────────────────────────────────────
def ordinalWordToCardinalWord(s: str):
    """
    Converts an ordinal word into its cardinal word form.

    This function transforms an ordinal descriptor (e.g., "fourth") into the 
    corresponding cardinal word (e.g., "four").

    Parameters:
    ──────────────────────────
    - s (*str*):  
      - An ordinal word (e.g., "first", "ninth", "twentieth").

    Returns:
    ──────────────────────────
    - (*str | None*):  
      - The cardinal word equivalent, or `None` if parsing fails.
    """
    return _convert_numeric_representation(s, "OrdinalWord", "CardinalWord")

def ordinalWordToCardinalNum(s: str):
    """
    Converts an ordinal word into a cardinal number.

    This function takes an ordinal word (e.g., "seventh") and returns its 
    numeric form (e.g., 7).

    Parameters:
    ──────────────────────────
    - s (*str*):  
      - An ordinal word (e.g., "second", "fourteenth").

    Returns:
    ──────────────────────────
    - (*int | None*):  
      - The cardinal number value, or `None` if conversion fails.
    """
    return _convert_numeric_representation(s, "OrdinalWord", "CardinalNumber")

def ordinalWordToOrdinalNum(s: str):
    """
    Converts an ordinal word into an ordinal number with suffix.

    This function returns the numeric ordinal representation 
    (e.g., "first" → "1st").

    Parameters:
    ──────────────────────────
    - s (*str*):  
      - An ordinal word (e.g., "eighth", "thirtieth").

    Returns:
    ──────────────────────────
    - (*str | None*):  
      - The formatted ordinal number, or `None` if invalid.
    """
    return _convert_numeric_representation(s, "OrdinalWord", "OrdinalNumber")


# FROM ORDINAL NUMBER: (E.G., "7TH")  
# ────────────────────────────────────────────────────────────────────────────────
def ordinalNumToCardinalWord(s: str):
    """
    Converts an ordinal number (with suffix) into its cardinal word equivalent.

    This function transforms an ordinal numeral (e.g., "3rd") into a cardinal 
    word (e.g., "three").

    Parameters:
    ──────────────────────────
    - s (*str*):  
      - A string with an ordinal number and suffix (e.g., "2nd", "11th").

    Returns:
    ──────────────────────────
    - (*str | None*):  
      - The cardinal word form, or `None` if parsing fails.
    """
    return _convert_numeric_representation(s, "OrdinalNumber", "CardinalWord")

def ordinalNumToCardinalNum(s: str):
    """
    Converts an ordinal number (with suffix) into its integer form.

    This function strips the suffix and returns the numeric value 
    (e.g., "5th" → 5).

    Parameters:
    ──────────────────────────
    - s (*str*):  
      - An ordinal number string (e.g., "1st", "22nd").

    Returns:
    ──────────────────────────
    - (*int | None*):  
      - The cardinal integer value, or `None` if invalid.
    """
    return _convert_numeric_representation(s, "OrdinalNumber", "CardinalNumber")

def ordinalNumToOrdinalWord(s: str):
    """
    Converts an ordinal number with suffix into its word representation.

    This function maps numeric ordinal forms (e.g., "2nd") to word-based 
    ordinals (e.g., "second").

    Parameters:
    ──────────────────────────
    - s (*str*):  
      - A formatted ordinal number string (e.g., "3rd", "10th").

    Returns:
    ──────────────────────────
    - (*str | None*):  
      - The corresponding ordinal word, or `None` if invalid.
    """
    return _convert_numeric_representation(s, "OrdinalNumber", "OrdinalWord")




# CONVERSION LOGIC 
# ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
class __NumericConverter:
    """
    Internal utility class for identifying and converting between different numeric representations.

    This class provides type detection and transformation across four canonical numeric formats:
        - Cardinal Number (e.g., 4)
        - Cardinal Word   (e.g., "four")
        - Ordinal Number  (e.g., "4th")
        - Ordinal Word    (e.g., "fourth")

    It uses the `numbr` module's conversion functions internally and supports automatic type inference,
    conversion routing, and optional string casting for numeric outputs.

    Note:
        This class is intended for internal use and is not part of the public API.
    """
    #   Alias handling for representation labels
    _LABEL_ALIASES: Dict[str, str] = {
        # Cardinal Number
        "cardinalnumber": "Cardinal Number",
        "cardnum":        "Cardinal Number",
        "card-num":       "Cardinal Number",
        "cn":             "Cardinal Number",
        "cnum":           "Cardinal Number",
        "digit":          "Cardinal Number",
        "number":         "Cardinal Number",
        "num":            "Cardinal Number",
        "int":            "Cardinal Number",

        # Cardinal Word
        "cardinalword":   "Cardinal Word",
        "cardword":       "Cardinal Word",
        "card-word":      "Cardinal Word",
        "cw":             "Cardinal Word",
        # "word":           "Cardinal Word",
        "wordnum":        "Cardinal Word",
        "wordnumber":     "Cardinal Word",
        "cword":          "Cardinal Word",

        # Ordinal Number
        "ordinalnumber":  "Ordinal Number",
        "ordnum":         "Ordinal Number",
        "ord-num":        "Ordinal Number",
        "on":             "Ordinal Number",
        "onum":           "Ordinal Number",
        "rank":           "Ordinal Number",
        "position":       "Ordinal Number",
        "place":          "Ordinal Number",

        # Ordinal Word
        "ordinalword":    "Ordinal Word",
        "ordword":        "Ordinal Word",
        "ord-word":       "Ordinal Word",
        "ow":             "Ordinal Word",
        "wordord":        "Ordinal Word",
        "wordordinal":    "Ordinal Word",
        "oword":          "Ordinal Word",
    }

    @classmethod
    def _canon(cls, label=None):
        """
        Canonicalise a user-supplied representation label.

        • lower-case → strip spaces/underscores → look up alias  
        • if not found, assume the caller already supplied a canonical string  
        • returns None unchanged
        """
        if label is None:
            return None
        norm = _SPACE_UNDERSCORE_RE.sub("", str(label).strip().lower())
        return cls._LABEL_ALIASES.get(norm, label)
    # ----------------------------------------------------------------------
    
    # Mapping between representations and conversion functions from numbr
    _CONV_MAP = {
        # --- From Cardinal Number
        ("Cardinal Number", "Cardinal Word"):   	cardinalNumToCardinalWord,
        ("Cardinal Number", "Ordinal Number"):    cardinalNumToOrdinalNum,
        ("Cardinal Number", "Ordinal Word"):      cardinalNumToOrdinalWord,
        # --- From Cardinal Word    
        ("Cardinal Word", "Cardinal Number"):     cardinalWordToCardinalNum,
        ("Cardinal Word", "Ordinal Number"):      cardinalWordToOrdinalNum,
        ("Cardinal Word", "Ordinal Word"):        cardinalWordToOrdinalWord,
        # --- From Ordinal Number     
        ("Ordinal Number", "Cardinal Number"):    ordinalNumToCardinalNum,
        ("Ordinal Number", "Cardinal Word"):      ordinalNumToCardinalWord,
        ("Ordinal Number", "Ordinal Word"):       ordinalNumToOrdinalWord,
        # --- From Ordinal Word     
        ("Ordinal Word", "Cardinal Number"):      ordinalWordToCardinalNum,
        ("Ordinal Word", "Cardinal Word"):        ordinalWordToCardinalWord,
        ("Ordinal Word", "Ordinal Number"):       ordinalWordToOrdinalNum,
    }
    
    #  Public: detect representation category
    @classmethod
    def num_type(cls, value):
        """
        Infer the numeric representation type of a given input value.

        This method classifies the input into one of four types based on its structure and content:
            - "Cardinal Number" for digit-only numbers (e.g., 42, "100")
            - "Ordinal Number" for ordinal numerals with suffixes (e.g., "1st", "22nd")
            - "Cardinal Word" for spelled-out cardinal numbers (e.g., "four", "eighteen")
            - "Ordinal Word" for spelled-out ordinal numbers (e.g., "third", "twentieth")

        Parameters:
        ──────────────────────────
            value (str | int): The input to analyze.

        Returns:
        ──────────────────────────
            str or None: The detected representation name, or None if it cannot be determined.
        """    	
        if isinstance(value, int):
            return "Cardinal Number"
        
        s = str(value).strip().lower()
        
        # 1. ordinal number (e.g. "21st")
        if cls._ORD_SUFFIX_RE.match(s):
            return "Ordinal Number"
        
        # 2. cardinal number (all digits)
        if cls._DIGIT_ONLY_RE.match(s):
            return "Cardinal Number"
        
        # 3. spelled-out ordinal word?
        if ordinalWordToCardinalNum(s) is not None:
            return "Ordinal Word"
        
        # 4. spelled-out cardinal word?
        if cardinalWordToCardinalNum(s) is not None:
            return "Cardinal Word"
        
        return None

    #  Public: convert between representations
    @classmethod
    def to_type(cls, value, target=None, *, as_str=False):
        """
        Convert a numeric value from its current representation to a target representation.

        This method routes the conversion using the internal type map and the `numbr` module's converters.
        If no conversion is needed or the target is unspecified, it either returns the detected type or the original value.

        Parameters:
        ──────────────────────────
            value (str | int): The numeric value to convert.
            target (str | None): The target representation to convert to. Must be one of:
                "Cardinal Number", "Cardinal Word", "Ordinal Number", "Ordinal Word".
            as_str (bool, optional): If True, return numeric results as strings. Default is False.

        Returns:
        ──────────────────────────
            str | int: The converted result in the requested representation.

        Raises:
        ──────────────────────────        	
            ValueError: If the type of `value` cannot be determined or conversion is not possible.
        """    	
        src = cls.num_type(value)
        if src is None:
            raise ValueError(f"Cannot determine representation of {value!r}")

        target = cls._canon(target)

        # no conversion requested or needed
        if target is None or target == src:
            return src if target is None else value

        try:
            func = cls._CONV_MAP[(src, target)]
        except KeyError as exc:
            raise ValueError(f"No conversion path from {src} to {target}") from exc
        result = func(value)
        
        # optional cast to str for numeric results        
        if as_str and isinstance(result, int):
            result = str(result)
        return result


# Internal singleton used for identifying and transforming numeric types
_numbers = __NumericConverter()


# ──────────────────────────────────────────────────────────────────────────────
# Public-facing wrappers for numeric type inspection and conversion
# These wrap internal methods on the __NumericConverter instance, while preserving
# docstrings and metadata (without overwriting their custom function names).
# ──────────────────────────────────────────────────────────────────────────────
def Type(value):
    """This will be replaced by update_wrapper."""
    # Determine the numeric representation of the given value
    return _numbers.num_type(value)

def Cast(value, target=None, *, as_str=False):
    """This will be replaced by update_wrapper."""	
    # Convert a numeric value to a target representation (with optional str cast)
    return _numbers.to_type(value, target, as_str=as_str)

# ──────────────────────────────────────────────────────────────────────────────
# Preserve docstrings and metadata from original methods,
# but keep the wrapper's own function names (Type, Cast)
# ──────────────────────────────────────────────────────────────────────────────
custom_assignments = tuple(
    attr for attr in WRAPPER_ASSIGNMENTS if attr not in ('__name__', '__qualname__')
)

update_wrapper(Cast, __NumericConverter.to_type, assigned=custom_assignments)
update_wrapper(Type, __NumericConverter.num_type, assigned=custom_assignments)




__all__ = [
    # "replaceNumericValue",    
    
    # Core Conversion Functions
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
    "insertSep",
    "formatDecimal",

    # Cross-Type Conversion Lambdas
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
    
    # Public aliases for numeric type detection and conversion
    "Type",   # Detect the representation type of a number (e.g., "Ordinal Word", "Cardinal Number")
    "Cast",   # Convert a value between numeric representations (e.g., word → digit)    
]

