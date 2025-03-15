# -*- coding: utf-8 -*-


from . import engine as __engine

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
    "formatDecimal", 
    "insertSep",     
]

# Reference functions using __engine alias
# replaceNumericValue = __engine.replaceNumericValue
wordsToInt = __engine.wordsToInt
ordinalSuffix = __engine.ordinalSuffix
intToWords = __engine.intToWords
intToOrdinalWords = __engine.intToOrdinalWords
stripOrdinalSuffix = __engine.stripOrdinalSuffix
ordinalWordsToInt = __engine.ordinalWordsToInt
stringToInt = __engine.stringToInt
extractNumericValue = __engine.extractNumericValue
romanToWords = __engine.romanToWords
romanToInt = __engine.romanToInt
formatDecimal = __engine.formatDecimal
insertSep = __engine.insertSep

del engine
