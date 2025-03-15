# numbr

**numbr** is a Python library designed for parsing and converting numbers written in English. It simplifies working with numbers by converting between spelled-out forms, ordinal forms, and numeric representations.

---

## Key Features

- Convert spelled-out cardinal numbers into integers (e.g., `"one hundred twenty-three"` → `123`).
- Convert integers into their spelled-out English words (e.g., `123` → `"one hundred twenty-three"`).
- Convert ordinal words to numeric ordinals (e.g., `"twenty-first"` → `"21st"` or `21`).
- Extract numeric values from text strings.
- Handle negative numbers, hyphenated numbers, and large numbers (up to quintillions).

---

## Installation

Install `numbr` using `pip`:

```bash
pip install numbr
```

---

## Usage Examples

### Convert Words to Integer

```python
import numbr

print(numbr.wordsToInt("one thousand two hundred thirty-four"))
# Output: 1234
```

### Convert Integer to Words

```python
print(numbr.intToWords(5678))
# Output: "five thousand six hundred seventy-eight"
```

### Convert Ordinal Words to Numeric Form

```python
print(numbr.ordinalWordsToInt("forty-second"))
# Output: "42nd"

print(numbr.ordinalWordsToInt("forty-second", to_num=True))
# Output: 42
```

### Extract Numeric Values from Strings

```python
print(numbr.extractNumericValue("I have twenty apples and 13 oranges."))
# Output: 20
```

---

## Terminology

- **Cardinal Numbers**: Represent quantity (e.g., "one", "twenty-five", "1,234").
- **Ordinal Numbers**: Represent position or order (e.g., "first", "twenty-first", "3rd").
- **Ordinal Suffix**: Letters added to numbers indicating position ("st", "nd", "rd", "th").

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve `numbr`.

---

## Contact

For questions or feedback, please open an issue on the project's GitHub repository.

