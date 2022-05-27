from cmath import inf
from logging import raiseExceptions
import string
from contextlib import suppress
from typing import NamedTuple

import pytils
from pymorphy2 import MorphAnalyzer
from pymorphy2.analyzer import Parse

from jpoetry.config import KNOWN_GLYPHS
from jpoetry.utils import InverseMapping


morph = MorphAnalyzer()

LATIN_VOWELS: set[str] = {"a", "e", "i", "o", "u", "y"}
CYRILLIC_VOWELS: set[str] = {"а", "е", "ё", "и", "о", "у", "ы", "э", "ю", "я"}
# remove unknown characters
UNKNOWN_CHAR_TRANSLATOR: InverseMapping[int, str] = InverseMapping(KNOWN_GLYPHS, "")
ASCII = set(string.ascii_letters)
SUPERSCRIPT_NUMBERS_TRANSLATOR = {
    ord(number): superscript for number, superscript in zip("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
}


def remove_unsupported_chars(text: str) -> str:
    return text.translate(UNKNOWN_CHAR_TRANSLATOR).strip()


def parse_word(word: str) -> Parse:
    try:
        return morph.parse(word)[0]
    except IndexError:
        raise ParseError("Unable to parse word")


QUANTITATIVE_TO_NUMERALS: dict[str, Parse] = {
    k: parse_word(v)
    for k, v in {
        "один": "первый",
        "два": "второй",
        "три": "третий",
        "четыре": "четвёртый",
        "пять": "пятый",
        "шесть": "шестой",
        "семь": "седьмой",
        "восемь": "восьмой",
        "девять": "девятый",
        "десять": "десятый",
        "одиннадцать": "одиннадцатый",
        "двенадцать": "двенадцатый",
        "тринадцать": "тринадцатый",
        "четырнадцать": "четырнадцатый",
        "пятнадцать": "пятнадцатый",
        "шестнадцать": "шестнадцатый",
        "семнадцать": "семнадцатый",
        "восемнадцать": "восемнадцатый",
        "девятнадцать": "девятнадцатый",
        "двадцать": "двадцатый",
        "тридцать": "тридцатый",
        "сорок": "сороковой",
        "пятьдесят": "пятидесятый",
        "шестьдесят": "шестидесятый",
        "семьдесят": "семидесятый",
        "восемьдесят": "восьмидесятый",
        "девяносто": "девяностый",
        "сто": "сотый",
        "двести": "двухсотый",
        "триста": "трёхсотый",
        "четыреста": "четырёхсотый",
        "пятьсот": "пятисотый",
        "шестьсот": "шестисотый",
        "семьсот": "семисотый",
        "восемьсот": "восьмисотый",
        "девятьсот": "девятисотый",
        "тысяча": "тысячный",
        "миллион": "миллионный",
        # AFAIK any numeral starting from here is just num + 'ный'
    }.items()
}


class WordInfo(NamedTuple):
    word: str
    syllables: int

    def __str__(self) -> str:
        return self.word

    def __repr__(self) -> str:
        return f"{self.word}{str(self.syllables).translate(SUPERSCRIPT_NUMBERS_TRANSLATOR)}"


class BadNumberError(ValueError):
    ...


class ParseError(ValueError):
    ...


def quantitative_to_numeral(number: str) -> Parse:
    if number in QUANTITATIVE_TO_NUMERALS:
        return QUANTITATIVE_TO_NUMERALS[number]

    with suppress(ParseError):
        parsed_number = parse_word(number + "ный")
        if "Anum" in parsed_number.tag:
            return parsed_number.word

    raise BadNumberError(f"Unable to get numeral from {number!r}")


def spell_number(decimal: str, inflect: str = None) -> str:
    """
    Convert number to cyrillic text, keeping its original form
    """
    first_decimal_part = ""
    second_part = ""
    decimal = "".join(decimal.split())
    ending = None
    for i, char in enumerate(decimal):
        if char.isdecimal():
            first_decimal_part += char
        elif char == ".":
            second_part = f" и {spell_number(decimal[i + 1:])}"
            break
        elif char == "/":
            second_part = f' из {spell_number(decimal[i + 1:], inflect="gent")}'
            break
        elif char == ":":
            second_part = f' к {spell_number(decimal[i + 1:], inflect="datv")}'
            break
        elif any(char.isdecimal() for char in decimal[i:]):
            raise BadNumberError(f"Unable to parse number {decimal}")
        elif (ending := decimal[i:]).startswith(
            "-"
        ):  # is this readable? Do you find it confusing?
            ending = ending[1:]
            break
    try:
        first_decimal = int(first_decimal_part)
    except ValueError:
        raise BadNumberError("Value is not a number")
    if first_decimal > 10**11:
        raise BadNumberError("Number is too big")

    number_in_words = pytils.numeral.in_words(first_decimal)
    words = number_in_words.split()

    if len(words) > 1 and words[0] in {"один", "одна"}:
        words.pop(0)
        number_in_words = " ".join(words)

    if inflect:
        inflected: list[str] = []

        for word in words:
            if word == "сто" and inflect in {"gent", "datv"}:
                # special case
                inflected.append("ста")
            else:
                inflected.append(parse_word(word).inflect({inflect}).word)

        return " ".join(inflected) + second_part

    if not ending:
        # Can't inflect the word without ending and main word.
        # We might be able to search the main word in the future.
        # This will require having entire sentence context when counting syllables,
        # not just the current word. Sounds very complicated.
        return number_in_words + second_part

    try:
        parsed_original_number = parse_word(decimal)
    except IndexError:
        raise BadNumberError(f"Unable to parse {decimal} with pymorphy2")

    # assume we always can parse output of num2text and values of QUANTITATIVE_TO_NUMERALS
    parsed_last_number = parse_word(words[-1])
    lexemes: list[Parse]
    if is_numeral := "Anum" in parsed_original_number.tag:
        lexemes = quantitative_to_numeral(parsed_last_number.normalized.word).lexeme
    else:
        lexemes = parsed_last_number.lexeme

    for lexeme in lexemes:
        if lexeme.word.endswith(ending):
            words[-1] = lexeme.word
            break
    else:
        raise BadNumberError(
            f"Unable to find suitable lexeme for {number_in_words=} with {ending=}"
        )
    if is_numeral and not first_decimal % 10 and len(words) > 1:
        return (
            "".join(parse_word(number).inflect({"gent"}).word for number in words[:-1])
            + words[-1]
            + second_part
        )
    return " ".join(words) + second_part


def count_word_syllables(word: str) -> int:
    """
    Count syllables in the word
    For cyrillic words just count syllables
    For latin words use some additional logic taken from sillapy library
    Numbers are converted to russian words
    """
    word = word.lower()
    syllables = 0
    word_length = len(word)
    last_char_index = word_length - 1

    current_number = ""
    number_syllables = 0
    for i, char in enumerate(word):
        if char.isdecimal() or current_number and char != " ":
            current_number += char
            continue
        elif current_number:
            # allow numbers separated by space like 100 000
            if word[min(i + 1, last_char_index)].isdecimal():
                continue
            number_syllables += count_word_syllables(spell_number(current_number))
            current_number = ""
            continue

        if char in CYRILLIC_VOWELS:
            syllables += 1
        elif char in LATIN_VOWELS:
            if i == 0:
                syllables += 1
            elif i == last_char_index or word[i + 1] not in LATIN_VOWELS:
                syllables += 1

    if current_number:
        number_syllables += count_word_syllables(spell_number(current_number))

    if word.endswith("e") and (len(word) > 3 or word[0] in LATIN_VOWELS):
        syllables -= 1
    if word.endswith("ia") and word_length > 2:
        syllables += 1
    if word.endswith("le") and word_length > 2 and word[-3] not in LATIN_VOWELS:
        syllables += 1
    if (ounce := word.find("ounce")) != -1:
        try:
            letter_after_ounce = word[ounce + 5]
            next_letter_after_ounce = word[ounce + 6]
        except IndexError:
            pass
        else:
            if letter_after_ounce not in LATIN_VOWELS and next_letter_after_ounce in LATIN_VOWELS:
                syllables -= 1

    if not syllables and set(word) & ASCII:
        # TODO: check abbr tag in parsed word
        syllables = len(
            word.replace(current_number, "")
        )  # likely abbreviation or single letter

    return syllables + number_syllables


def get_words_info(words: list[str]) -> tuple[list[WordInfo], int]:
    total_syllables = 0
    words_info: list[WordInfo] = []
    for word in words:
        syllables = count_word_syllables(word)
        total_syllables += syllables
        words_info.append(WordInfo(word, syllables))

    return words_info, total_syllables


def agree_with_number(word: str, number: int) -> str:
    try:
        return parse_word(word).make_agree_with_number(number).word
    except (ParseError, AttributeError):
        return word

count_word_syllables("die")