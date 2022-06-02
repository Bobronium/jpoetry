from pathlib import Path
import pytest

import jpoetry
from jpoetry import text
from jpoetry.text import (
    QUANTITATIVE_TO_NUMERAL,
    BadNumberError,
    ParseError,
    WordInfo,
    agree_with_number,
    count_word_syllables,
    get_words_info,
    morph,
    spell_number,
    parse_word,
    quantitative_to_numeral,
)


@pytest.mark.parametrize(
    'quantitative, numeral',
    (
        *tuple(QUANTITATIVE_TO_NUMERAL.items()),
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
        ('1 000', 'тысяча'),
        ('1 000-й', 'тысячный'),
        ('100 000', 'сто тысяч'),
        ('1 000 000', 'миллион'),
        ('100 000-й', 'стотысячный'),
        ('10 000 000-й', 'десятимиллионный'),
        (
            '10 456 269-й',
            'десять миллионов четыреста пятьдесят шесть тысяч двести шестьдесят девятый',
        ),
        ('10/10', 'десять из десяти'),
        ('1/1000', 'один из тысячи'),
        ('1/10000', 'один из десяти тысяч'),
        ('1/100 000', 'один из ста тысяч'),
        ('1:1', 'один к одному'),
        ('10:10', 'десять к десяти'),
        ('1:1000', 'один к тысяче'),
        ('1:10000', 'один к десяти тысячам'),
        ('1:100 000', 'один к ста тысячам'),
        ('1:1 100 000', 'один к миллиону ста тысячам'),
    ),
)
def test_spell_number(number, text):
    assert spell_number(number) == text


@pytest.mark.parametrize(
    'word,expected_syllables,number',
    (
        ('молоко', 3, None),
        ('яяяяяя', 6, None),  # count every vowel as syllable
        ('sponge', 1, None),  # 'e' at the end must not add syllable
        ('the', 1, None),
        ('the', 1, None),
        ('ape', 1, None),
        ('die', 1, None),
        ("escapes", 2, None),
        pytest.param("creates", 2, None, marks=pytest.mark.xfail),
        ("yeah", 1, None),
        ('announcement', 3, None),
        ("pronouncement", 3, None),
        ("pronounceable", 4, None),
        ("renouncements", 3, None),
        ("denouncements", 3, None),
        ("announcements", 3, None),
        ("mispronounced", 4, None),
        ('course', 1, None),
        ('bounce', 1, None),
        ("announced", 3, None),
        ('columbia', 4, None),
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
    spy = mocker.spy(jpoetry.text, 'spell_number')
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
    assert (
        agree_with_number('ох ну и как это парсить?', 5) == 'ох ну и как это парсить?'
    )
