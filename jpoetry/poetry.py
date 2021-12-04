from dataclasses import asdict, dataclass
from enum import Enum
from typing import Generator, NamedTuple, Optional

from loguru import logger

from jpoetry.text import UNKNOWN_CHAR_TRANSLATOR, WordInfo, get_words_info


# remove all unsuitable chars from words in the middle of lines
NON_FINAL_WORD_TRANSLATE_MAP = dict.fromkeys(map(ord, '.!?'), '')
NON_FINAL_WORDS: set[str] = {'в', 'на', 'из-под', 'под', 'или', 'по', 'над'}


class Genre(str, Enum):
    katauta = 'Катаута'
    hokku = 'Хокку'
    tanka = 'Танка'
    bussokusekika = 'Бусоку-сёкитаи'
    sedoka = 'Сэдока'

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


@dataclass(frozen=True)
class Poem:
    genre: Genre
    phrases: list[str]

    def __str__(self) -> str:
        return '\n'.join(self.phrases)

    def __repr__(self) -> str:
        return repr(asdict(self))


def detect_poem(text: str) -> Optional[Poem]:
    """
    Check if text might be a poem and return one if it is
    """
    words = text.split()
    if not MIN_WORDS <= len(words) <= MAX_WORDS:
        return None

    try:
        words_info, total_syllables = get_words_info(words)
    except ValueError:
        return None
    for poem_info in POEMS_INFO_MAP.get(total_syllables, []):
        phrases = compose_phrases(words_info.copy(), poem_info.syllables)
        if phrases is not None:
            return Poem(poem_info.genre, phrases)

    return None


def compose_phrases(
    words_info: list[WordInfo], poem_syllables: tuple[int, ...]
) -> Optional[list[str]]:
    """
    Compose phrases from list of words, and their syllables to a poem figure
    """
    phrases: list[str] = []
    pre_final_line = len(poem_syllables) - 2
    for i, needed_syllables in enumerate(poem_syllables):
        phrase: list[str] = []
        phrase_syllables = 0
        while phrase_syllables < needed_syllables:
            word, word_syllables = words_info.pop(0)
            phrase_syllables += word_syllables
            phrase.append(word)

        if phrase_syllables != needed_syllables:
            return None
        try:
            phrases.append(' '.join(normalize_phrase(phrase, pre_final=i == pre_final_line)))
        except BadPhraseError as e:
            logger.info(repr(e))
            return None

    return phrases


def normalize_phrase(phrase: list[str], pre_final: bool = False) -> Generator[str, None, None]:
    """
    Remove all unsuitable characters from a poem phrase
    Allow punctuation marks only after last words in phrase
    """
    final_word = len(phrase) - 1
    for i, word in enumerate(phrase):
        # make text nicer by removing misused quotes
        if word.startswith(('«', '"', "'")) != word.endswith(("'", '"', '»')):
            word = word.strip('«»"' + "'")

        word_without_unknown_chars = word.translate(UNKNOWN_CHAR_TRANSLATOR)
        if word_without_unknown_chars not in word:
            raise BadCharError(f'Word changed too much after removing unknown characters')
        word = word_without_unknown_chars

        if i != final_word:
            word = word.translate(NON_FINAL_WORD_TRANSLATE_MAP)
        elif word in NON_FINAL_WORDS and not pre_final:
            raise BadPhraseError(f'Encounter bad word in the end of non-pre-final line: {word}')

        yield word.lower()
