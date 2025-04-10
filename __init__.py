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
cardinalWordToCardinalNum = __engine.cardinalWordToCardinalNum
cardinalWordToOrdinalWord    = __engine.cardinalWordToOrdinalWord
cardinalWordToOrdinalNum  = __engine.cardinalWordToOrdinalNum
cardinalNumToCardinalWord   = __engine.cardinalNumToCardinalWord
cardinalNumToOrdinalWord    = __engine.cardinalNumToOrdinalWord
cardinalNumToOrdinalNum  = __engine.cardinalNumToOrdinalNum
ordinalWordToCardinalWord   = __engine.ordinalWordToCardinalWord
ordinalWordToCardinalNum = __engine.ordinalWordToCardinalNum
ordinalWordToOrdinalNum  = __engine.ordinalWordToOrdinalNum
ordinalNumToCardinalWord   = __engine.ordinalNumToCardinalWord
ordinalNumToCardinalNum = __engine.ordinalNumToCardinalNum
ordinalNumToOrdinalWord    = __engine.ordinalNumToOrdinalWord

del engine
