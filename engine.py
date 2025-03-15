# -*- coding: utf-8 -*-

#
# Understanding Number Terminology
# ─────────────────────────────────
# ┍━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┑
# │ Example │              Type             │                             Description                              │
# ┝━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┥
# │   four  │  Cardinal number (word form)  │           This is the written-out version of the number 4.           │
# │    4    │ Cardinal numeral (digit form) │           This is the numeric symbol representing "four."            │
# │  fourth │   Ordinal number (word form)  │ This is the written-out version of "4th," used to describe position. │
# │   4th   │  Ordinal numeral (digit form) │        This is the numeric way of writing an ordinal number.         │
# │    IV   │         Roman numeral         │     This represents the number "4" in the Roman numeral system.      │
# ┕━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┙
# 
# This module is designed to help developers work with numbers in natural language processing (NLP), data extraction, 
# and automated text conversion.



import re
import inspect
from typing import Literal, Union, Optional
from functools import reduce



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
        Finds digit-based tokens in a string, including optional decimals, and commas.
        """
        pattern = r'-?\d+(?:,\d{3})*(?:\.\d+)?'        

        matches = list(re.finditer(pattern, text))
        if not matches:
            return None if first_only else []

        # Convert each match to a string, removing commas
        found = [re.sub(r',', '', m.group(0)) for m in matches]

        if first_only:
            # Return a single-element list
            return [found[0]]
        else:
            return found
       
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
    match = re.match(r"(^\D*)(?:[\d,.]+)?(\D*$)", num_str)
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
    words_list = re.split(r"[\s-]+", s)
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
    # Define lists of spelled-out cardinal and ordinal numbers and combine both lists
    cardinal_numbers = ['zero', *_UNIT_DIGITS_WORDS, *_TEEN_NUMERALS_WORDS, *_TENS_MULTIPLES_WORDS]
    ordinal_numbers = list(_ORDINAL_MAPPING.keys())
    number_words = cardinal_numbers + ordinal_numbers

    # Build a regex pattern that matches a hyphen only if it is between two valid number words
    pattern = r'\b(' + '|'.join(number_words) + r')-(' + '|'.join(number_words) + r')\b'

    # s = re.sub(r'(\w)-(\w)', r'\1 \2', s)
    
    # Replaces hyphens only if they are between spelled-out cardinal or ordinal number words.    
    s = re.sub(pattern, r'\1 \2', s, flags=re.IGNORECASE)

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
        last_word_match = re.search(r'\b(\w+)\b$', tok)
        if not last_word_match:
            return None
        last_word = last_word_match.group()

        # Everything except the last word
        front_string = re.sub(r'\s*\b\w+\b$', '', tok).strip()

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
    # if tokens and re.match(r'^-?\d+$', str(tokens)):
    #     val = int(tokens)
    #     val = -val if is_negative else val
    #     return str(val) if to_str else val
    if tokens and re.match(r'^-?\d+$', str(tokens)):
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

    n_str = str(n)
    if "." in n_str:
        try:
            float_val = float(n_str)
            return _from_float(float_val)
        except ValueError:
            return None
    else:
        try:
            int_val = int(n_str)
            return _from_int(int_val)
        except ValueError:
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
def ordinalSuffix(n: int):
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
    
    # tokens = __parseNumericToken(s, first_only=False)  # Get all matches
    tokens = __parseNumericToken(s, first_only=__switch(allnum), wrap_single=True)  # Get all matches if allnum == True. The switch function swithes allnum boolen to False.    
    if not tokens:
        return None

    # if not isinstance(tokens, list):
    #     tokens=[tokens]

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




__all__ = [
    # "replaceNumericValue",      
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
]






















