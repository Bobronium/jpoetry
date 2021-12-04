import pytest

import jpoetry
from jpoetry import text
from jpoetry.text import (
    QUANTITATIVE_TO_NUMERALS,
    BadNumberError,
    ParseError,
    WordInfo,
    agree_with_number,
    count_word_syllables,
    get_words_info,
    morph,
    number_to_text,
    parse_word,
    quantitative_to_numeral,
)


@pytest.mark.parametrize(
    'quantitative, numeral',
    (
        *tuple(QUANTITATIVE_TO_NUMERALS.items()),
        ('миллиард', 'миллиардный'),
    ),
)
def test_quantitative_to_numeral(quantitative, numeral):
    assert quantitative_to_numeral(quantitative) == numeral


def test_quantitative_to_numeral_error(mocker):
    with pytest.raises(BadNumberError, match="Unable to get numeral from 'жопа'"):
        assert quantitative_to_numeral('жопа')


@pytest.mark.parametrize(
    'number,text',
    (
        ('1', 'один'),
        ('1-я', 'первая'),
        ('1-й', 'первый'),
        ('56', 'пятьдесят шесть'),
        ('56-й', 'пятьдесят шестой'),
        ('3.5', 'три и пять'),
        ('3.5-й', 'три и пятый'),
        ('100 000', 'сто тысяч'),
        ('100 000-й', 'стотысячный'),
        ('10 000 000-й', 'десятимиллионный'),
        (
            '10 456 269-й',
            'десять миллионов четыреста пятьдесят шесть тысяч двести шестьдесят девятый',
        ),
    ),
)
def test_number_to_text(number, text):
    assert number_to_text(number) == text


@pytest.mark.parametrize(
    'word,expected_syllables,number',
    (
        ('молоко', 3, None),
        ('яяяяяя', 6, None),  # count every vowel as syllable
        ('iiiiii', 2, None),  # first vowel always adds one syllable
        ('sponge', 1, None),  # 'e' at the end must not add syllable
        ('available', 4, None),  # however, 'le' counts
        ('в', 0, None),
        ('d', 1, None),
        ('1-ая', 3, '1-ая'),
        ('1', 2, '1'),
        ('100 000', 3, '100000'),
        ('10 000 000-й', 7, '10000000-й'),
        ('10 456 269-й раз', 25, '10456269-й'),
        ('PS4', 5, '4'),
        ('PS5', 3, '5'),
    ),
)
def test_count_word_syllables(word, expected_syllables, mocker, number):
    spy = mocker.spy(jpoetry.text, 'number_to_text')
    assert count_word_syllables(word) == expected_syllables
    assert spy.mock_calls == [] if number is None else [mocker.call(number)]


def test_get_words_info():
    info, syllables = get_words_info(['???', 'FFF', 'Ааа', 'ы'])
    assert info == [
        WordInfo(word='???', syllables=0),
        WordInfo(word='FFF', syllables=3),
        WordInfo(word='Ааа', syllables=3),
        WordInfo(word='ы', syllables=1),
    ]
    assert syllables == 7


def test_parse_word(mocker, call):
    parse_result = mocker.Mock()
    morph_parse_mock = mocker.patch.object(morph, 'parse', return_value=[parse_result])
    assert parse_word('test') == parse_result
    assert morph_parse_mock.mock_calls == [call('test')]


def test_parse_word_error(mocker, call):
    morph_parse_mock = mocker.patch.object(morph, 'parse', return_value=[])
    with pytest.raises(ParseError):
        parse_word('test')

    assert morph_parse_mock.mock_calls == [call('test')]


@pytest.mark.parametrize(
    'word,number,result',
    (
        ('жопа', 1, 'жопа'),
        ('жопа', 2, 'жопы'),
        ('жопа', 5, 'жоп'),
    ),
)
def test_agree_with_number(word, number, result):
    assert agree_with_number(word, number) == result


def test_agree_with_number_error(mocker):
    mocker.patch.object(text, 'parse_word', side_effect=ParseError)
    assert agree_with_number('ох ну и как это парсить?', 5) == 'ох ну и как это парсить?'
