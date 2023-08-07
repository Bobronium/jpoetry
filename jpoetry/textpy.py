from typing import NamedTuple


SUPERSCRIPT_NUMBERS_TRANSLATOR = {
    ord(number): superscript for number, superscript in zip("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
}


class WordInfo(NamedTuple):
    word: str
    syllables: int

    def __str__(self) -> str:
        return self.word

    def __repr__(self) -> str:
        return f"{self.word}{str(self.syllables).translate(SUPERSCRIPT_NUMBERS_TRANSLATOR)}"


class LineInfo(NamedTuple):
    words_info: list[WordInfo]
    total_syllables: int


class BadNumberError(ValueError):
    ...


class ParseError(ValueError):
    ...
