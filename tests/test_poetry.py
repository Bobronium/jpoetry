from dataclasses import asdict

import pytest

from jpoetry.poetry import Genre, detect_poem, normalize_phrase


@pytest.mark.parametrize(
    'inp,out',
    (
        ('Hey! How are you?', 'hey how are you?'),
        ("I'm great!", "i'm great!"),
        ("'WOW!' — said the guy,", "'wow' — said the guy,"),
        ('"This is a quote"', "this is a quote"),
        ("∂ßƒ∂", "ßƒ"),
        pytest.param("ß∂∂ƒ", "ßƒ", marks=pytest.mark.xfail),
    ),
)
def test_normalize_phrase(inp, out):
    assert list(normalize_phrase(inp.split())) == out.split()


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
    poem = detect_poem(text)
    assert poem.genre is genre
    assert str(poem.genre) == genre == genre.value
    assert poem.phrases == expected_phrases
    assert str(poem) == '\n'.join(poem.phrases)
    assert repr(poem) == repr(asdict(poem))


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
    assert detect_poem(text) is None
