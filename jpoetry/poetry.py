import textwrap
from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple


from jpoetry.text import (
    SUPERSCRIPT_NUMBERS_TRANSLATOR,
    UNKNOWN_CHAR_TRANSLATOR,
    WordInfo,
    get_words_info,
)


# remove all unsuitable chars from words in the middle of lines
NON_FINAL_WORD_TRANSLATE_MAP = dict.fromkeys(map(ord, ".!?"), "")
NON_FINAL_WORDS: set[str] = {"в", "на", "из-под", "под", "или", "по", "над"}


class Genre(str, Enum):
    katauta = "Катаута"
    hokku = "Хокку"
    tanka = "Танка"
    bussokusekika = "Бусоку-сёкитаи"
    sedoka = "Сэдока"

    def __str__(self) -> str:
        return self.value


POETRY_SYLLABLES = {
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

# create poems info, so we can look up poems by total number of syllables
# sorting it here just for prettier output later
for _genre, _syllables in sorted(POETRY_SYLLABLES.items(), key=lambda x: sum(x[1])):
    POEMS_INFO_MAP.setdefault(sum(_syllables), []).append(PoemInfo(_genre, _syllables))
del _genre, _syllables

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


@dataclass
class Phrase:
    position: tuple[int, int]
    expected_syllables: int
    words: list[WordInfo] = field(default_factory=list)
    issues: set[Issue] = field(default_factory=lambda: {NOT_ENOUGH_SYLLABLES})
    syllables: int = 0

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

        self.words.append(
            WordInfo(self.normalize_word(word_info.word, final), word_info.syllables)
        )

    def normalize_word(self, word: str, final: bool) -> str:
        """
        Remove all unsuitable characters from a poem phrase
        Allow punctuation marks only after last words in phrase
        """
        # make text nicer by removing misused quotes
        if word.startswith(("«", '"', "'")) != word.endswith(("'", '"', "»")):
            word = word.strip('«»"' + "'")

        word_without_unknown_chars = word.translate(UNKNOWN_CHAR_TRANSLATOR)
        if word_without_unknown_chars not in word:
            self.issues.add(
                Issue(
                    f"Word changed too much after removing unknown characters: {word}"
                )
            )

        word = word_without_unknown_chars

        if not final:
            word = word.translate(NON_FINAL_WORD_TRANSLATE_MAP)
        elif word in NON_FINAL_WORDS and self.position[1] - self.position[0] != 1:
            self.issues.add(Issue(f"Phrase ends with a forbidden word: {word}"))

        return word.lower()

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
    issues: list[Issue]

    def __str__(self) -> str:
        return "\n".join(map(str, self.phrases))

    def __repr__(self) -> str:
        return f"{self.genre}\n\n" + "\n".join(map(repr, self.phrases))


def detect_poem(
    text: str, strict: bool = True
) -> tuple[Poem | None, list[WordInfo] | None, int | None]:
    """
    Check if text might be a poem and return one if it is
    """
    words = text.split()
    if not MIN_WORDS <= len(words) <= MAX_WORDS:
        return None, None, None

    words_info, total_syllables = get_words_info(words)

    detected_poem: Poem | None = None
    for poem_info in POEMS_INFO_MAP.get(total_syllables, []):
        try:
            phrases, issues = compose_phrases(
                words_info.copy(), poem_info.syllables, strict=strict
            )
        except BadPhraseError:
            continue

        if not issues:
            return (
                Poem(poem_info.genre, phrases, issues=issues),
                words_info,
                total_syllables,
            )
        elif strict:
            return None, words_info, total_syllables
        else:
            if detected_poem is None or len(detected_poem.issues) > len(issues):
                detected_poem = Poem(poem_info.genre, phrases, issues=issues)

    return detected_poem, words_info, total_syllables


def compose_phrases(
    words_info: list[WordInfo], poem_syllables: tuple[int, ...], strict: bool = True
) -> tuple[list[Phrase], list[Issue]]:
    """
    Compose phrases from list of words, and their syllables to a poem figure
    """
    phrases: list[Phrase] = []
    final_line = len(poem_syllables) - 1
    issues = []
    for i, needed_syllables in enumerate(poem_syllables):
        phrase = Phrase(position=(i, final_line), expected_syllables=needed_syllables)
        while words_info and phrase.syllables < needed_syllables:
            phrase.add_word(words_info.pop(0))

        if phrase.issues:
            if strict:
                raise BadPhraseError(repr(phrase))
            issues.extend(phrase.issues)
        phrases.append(phrase)

    return phrases, issues
