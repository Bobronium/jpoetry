from dataclasses import asdict

import pytest

from jpoetry.poetry import Genre, Issue, Phrase, detect_poem
from jpoetry.textpy import WordInfo


@pytest.mark.parametrize(
    'inp,changed',
    (
        ('Hey! How are you?', 'hey! how are you?'),
        ("I'm great!", "i'm great!"),
        ("'WOW!' — said the guy,", "'wow!' — said the guy,"),
        ('"This is a quote"', '"this is a quote"'),
        ("∂ßƒ∂", "ßƒ"),
        ("🤷🏻‍♀ не уверена что это оптимально по ряду причин.", "не уверена что это оптимально по ряду причин."),
        pytest.param("ß∂∂ƒ", "ßƒ"),
    ),
)
def test_normalize_phrase(inp, changed):
    phrase = Phrase([0, 0], 0)
    for word in inp.split():
        phrase.add_word(WordInfo(word, 0))
    assert str(phrase) == changed


@pytest.mark.parametrize(
    'genre,text,expected_phrases',
    (
        (
            Genre.hokku,
            "Я вспомнил видос, где у мужика банка в жепе лопнула..",
            ['я вспомнил видос,', 'где у мужика банка', 'в жепе лопнула..'],
        ),
    ),
)
def test_detect_poem_positive(genre, text, expected_phrases):
    poem, _, _ = detect_poem(text)
    assert poem.genre is genre
    assert str(poem.genre) == genre == genre.value
    assert list(map(str, poem.phrases)) == list(map(str, expected_phrases))
    assert str(poem) == '\n'.join(map(str, poem.phrases))
    print(repr(poem))
    assert (
        repr(poem)
        == """\
Хокку

1/3. я¹ вспомнил² видос,² (⁵)
2/3. где¹ у¹ мужика³ банка² (⁷)
3/3. в⁰ жепе² лопнула..³ (⁵)\
"""
    )


@pytest.mark.parametrize(
    'text',
    (
        # different number of syllables
        'Я вспомнил видос, где у мужика банка в жепе не лопнула..',
        # same number of syllables, but don't fit in 5-7-5 phrases
        'Я вспомнил видос, где банка в жепе у мужика лопнула..',
        # a bad word on non-pre-final-line
        "Ну тут много не выжмешь а вот суды над Навальным будут думаю настоящим мемным генератором",
        # single word
        'a',
        # > max syllables words
        'a ' * 99,
    ),
)
def test_detect_poem_negative(text):
    assert detect_poem(text)[0] is None
