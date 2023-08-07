import textwrap
from dataclasses import dataclass, field
from enum import Enum
from typing import Generator, Iterator, NamedTuple

from jpoetry.text import (
    SUPERSCRIPT_NUMBERS_TRANSLATOR,
    WordInfo,
    get_words_info,
    remove_unsupported_chars,
)
from jpoetry.textpy import LineInfo


# remove all unsuitable chars from words in the middle of lines
NON_FINAL_CHARS = ".!?"
NON_FINAL_WORDS: set[str] = {"в", "на", "из-под", "под", "или", "по", "над"}


class Genre(str, Enum):
    katauta = "Катаута"
    hokku = "Хокку"
    tanka = "Танка"
    bussokusekika = "Бусоку-сёкитаи"
    sedoka = "Сэдока"

    def __str__(self) -> str:
        return self.value


POETRY_PHRASES_SYLLABLES = {
    Genre.katauta: (5, 7, 7),
    Genre.hokku: (5, 7, 5),
    Genre.tanka: (5, 7, 5, 7, 7),
    Genre.bussokusekika: (5, 7, 5, 7, 7, 7),
    Genre.sedoka: (5, 7, 7, 5, 7, 7),
}


class PoemInfo(NamedTuple):
    genre: Genre
    syllables: tuple[int, ...]


POEMS_INFO_MAP: dict[int, list[PoemInfo]] = {}
NUMBER_OF_PHRASES_TO_POEMS_INFO: dict[int, list[PoemInfo]] = {}

# create poems info, so we can look up poems by total number of syllables or paragraphs
# sorting it here just for prettier output later
for _genre, _phrases_syllables in sorted(
    POETRY_PHRASES_SYLLABLES.items(), key=lambda x: sum(x[1])
):
    _poem_info = PoemInfo(_genre, _phrases_syllables)
    POEMS_INFO_MAP.setdefault(sum(_phrases_syllables), []).append(_poem_info)
    NUMBER_OF_PHRASES_TO_POEMS_INFO.setdefault(len(_phrases_syllables), []).append(
        _poem_info
    )

del (
    _genre,
    _phrases_syllables,
    _poem_info,
)


# need this for fast comparison between total number of words before counting syllables
MIN_WORDS = len(min(POEMS_INFO_MAP.values(), key=len))
MAX_WORDS = max(POEMS_INFO_MAP)


class BadPhraseError(ValueError):
    ...


class BadCharError(ValueError):
    ...


class Issue(str):
    ...


TOO_MANY_SYLLABLES = Issue("Too many syllables")
NOT_ENOUGH_SYLLABLES = Issue("Not enough syllables")
PHRASE_CONTAINS_UNMATCHED_QUOTE = Issue("Phrase contains unmatched quote")


@dataclass
class Phrase:
    position: tuple[int, int]
    expected_syllables: int
    words: list[WordInfo] = field(default_factory=list)
    issues: set[Issue] = field(default_factory=lambda: {NOT_ENOUGH_SYLLABLES})
    syllables: int = 0

    _open_quotes = 0
    _close_quotes = 0

    def __len__(self) -> int:
        return len(self.words)

    def add_word(self, word_info: WordInfo) -> None:
        self.syllables += word_info.syllables
        final = False
        if self.syllables >= self.expected_syllables:
            if self.syllables > self.expected_syllables:
                self.issues.add(TOO_MANY_SYLLABLES)
            self.issues.discard(NOT_ENOUGH_SYLLABLES)
            final = True

        normalized_word = self.normalize_word(word_info.word, final)
        if not normalized_word:
            return

        self.words.append(
            WordInfo(normalized_word, word_info.syllables)
        )
        if self._open_quotes != self._close_quotes and final:
            self.issues.add(PHRASE_CONTAINS_UNMATCHED_QUOTE)

    def normalize_word(self, word: str, final: bool) -> str:
        """
        Remove all unsuitable characters from a poem phrase
        Allow punctuation marks only after last words in phrase
        """
        # make text nicer by removing misused quotes
        self._open_quotes += word.startswith(("«", '"', "'"))
        self._close_quotes += word.endswith(("»", '"', "'"))

        word_without_unknown_chars = remove_unsupported_chars(word)
        if word_without_unknown_chars not in word:
            self.issues.add(
                Issue(
                    f"Word changed too much after removing unknown characters: {word}"
                )
            )

        word = word_without_unknown_chars

        # don't want any sentence ending punctuation in one phrase
        # unless, it's in quotes.
        if not final and self._open_quotes <= self._close_quotes:
            if word != word.strip(NON_FINAL_CHARS):
                self.issues.add(
                    Issue(f"Phrase contains forbidden punctuation: {word!r}")
                )
        elif word in NON_FINAL_WORDS and self.position[1] - self.position[0] != 1:
            self.issues.add(Issue(f"Phrase ends with a forbidden word: {word!r}"))
        return word.lower().strip()

    def __str__(self) -> str:
        return " ".join(map(str, self.words))

    def __repr__(self) -> str:
        return (
            f"{self.position[0] + 1}/{self.position[1] + 1}. "
            + " ".join(map(repr, self.words))
            + (
                f" ({self.syllables}/{self.expected_syllables})"
                if self.syllables != self.expected_syllables
                else f" ({self.expected_syllables})"
            ).translate(SUPERSCRIPT_NUMBERS_TRANSLATOR)
            + (
                textwrap.indent("\n^" + "\n".join(self.issues), "\t")
                if self.issues
                else ""
            )
        )


@dataclass(frozen=True)
class Poem:
    genre: Genre
    phrases: list[Phrase]
    total_issues: int

    def __str__(self) -> str:
        return "\n".join(map(str, self.phrases))

    def __repr__(self) -> str:
        return f"{self.genre}\n\n" + "\n".join(map(repr, self.phrases))


def iter_poems(text: str) -> Generator[Poem, None, None]:
    for poem in detect_poems(text, strict=True)[0]:
        if not poem.total_issues:
            yield poem


def detect_poems(text: str, strict: bool = True) -> tuple[list[Poem], list[LineInfo]]:
    """
    Check if text might be a poem and return one if it is
    """
    poems = []
    lines_infos = []
    for paragraph in text.split("\n\n"):
        lines = paragraph.split("\n")

        if len(lines) > 1:
            poems_info = NUMBER_OF_PHRASES_TO_POEMS_INFO.get(len(lines), [])
            lines_info = [get_words_info(line.split()) for line in lines]
            lines_infos.extend(lines_info)
            poems.extend(generate_poems_from_lines(lines_info, poems_info))
        else:
            words = paragraph.split()
            # quick check
            if not MIN_WORDS <= len(words) <= MAX_WORDS:
                if strict:
                    continue
            line_info = get_words_info(words)
            lines_infos.append(line_info)
            poems_info = POEMS_INFO_MAP.get(line_info.total_syllables, [])
            poems.extend(generate_poems_from_words(line_info.words_info, poems_info))

    return poems, lines_infos


def generate_poems_from_lines(
    lines_info: list[LineInfo], poems_info: list[PoemInfo], strict: bool = True
):
    """Try to match existing lines to poem figure"""
    for poem_info in poems_info:
        try:
            yield compose_poem_from_lines(lines_info, poem_info, strict=strict)
        except BadPhraseError:
            continue


def generate_poems_from_words(
    words_info: list[WordInfo], poems_info: list[PoemInfo], strict: bool = True
) -> Generator[Poem, None, None]:
    """Assemble words into phrases trying to match poem figure"""
    for poem_info in poems_info:
        try:
            yield compose_poem_from_words(iter(words_info), poem_info, strict=strict)
        except BadPhraseError:
            continue


def compose_poem_from_words(
    words_info: Iterator[WordInfo], poem_info: PoemInfo, strict: bool = True
) -> Poem:
    """
    Compose phrases from list of words, and their syllables to a poem figure
    """
    phrases: list[Phrase] = []
    final_line = len(poem_info.syllables) - 1
    issues_count: int = 0
    total_phrases = len(poem_info.syllables)
    for phrase_number, needed_syllables in enumerate(poem_info.syllables):
        phrase = Phrase(
            position=(phrase_number, final_line), expected_syllables=needed_syllables
        )

        while (
            phrase.syllables < needed_syllables
            # get greedy on last phrase
            or phrase_number == total_phrases
        ) and (word_info := next(words_info, None)):
            phrase.add_word(word_info)

        if phrase.issues:   
            if strict:
                raise BadPhraseError(repr(phrase))
            issues_count += len(phrase.issues)

        phrases.append(phrase)

    return Poem(poem_info.genre, phrases, total_issues=issues_count)


def compose_poem_from_lines(
    raw_phrases: list[LineInfo], poem_info: PoemInfo, strict: bool = True
) -> Poem:
    """
    Compose phrases from list of words, and their syllables to a poem figure
    """
    phrases: list[Phrase] = []
    final_line = len(poem_info.syllables) - 1
    issues_count: int = 0
    for phrase_number, (raw_phrase, needed_syllables) in enumerate(zip(raw_phrases, poem_info.syllables)):
        phrase = Phrase(position=(phrase_number, final_line), expected_syllables=needed_syllables)
        
        for word_info in raw_phrase.words_info:
            phrase.add_word(word_info)

        if phrase.issues:
            if strict:
                raise BadPhraseError(repr(phrase))
            issues_count += len(phrase.issues)

        phrases.append(phrase)

    return Poem(poem_info.genre, phrases, total_issues=issues_count)
