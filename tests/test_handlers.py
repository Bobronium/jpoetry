from unittest.mock import Mock

import pytest
from aiogram.types import Message, User

from jpoetry import bot
from jpoetry.answers import HELP_TEXT, WELCOME_TEXT
from jpoetry.config import DEFAULT_AUTHOR, TOO_LONG_MESSAGE_FILE
from jpoetry.bot import bot, detect_and_send_poem, get_author, send_cheat_sheet, welcome_user
from jpoetry.image import TooLongTextError
from jpoetry.poetry import detect_poem


@pytest.fixture
def get_message(mocker):
    def get_message(
        text='test',
        username='test',
        full_name='test',
        private=True,
        forward_username=None,
        forward_sender_name=None,
        forward_full_name=None,
    ):
        message = mocker.Mock(
            spec=Message,
            text=text,
            message_id=123,
            chat_id=123,
            from_user=mocker.Mock(
                spec=User,
                id=123 if private else 321,
                full_name=full_name,
                username=username,
            ),
        )

        message.forward_sender_name = forward_sender_name
        if forward_username or forward_full_name:
            message.forward_from = mocker.Mock(
                spec=User, username=forward_username, full_name=forward_full_name
            )
        else:
            message.forward_from = None
        message.is_forward = lambda: bool(message.forward_from or message.forward_sender_name)

        return message

    return get_message


@pytest.mark.parametrize(
    'full_name,username,result',
    (
        ('Test Testov', 'test', 'Test Testov'),
        ('test' * 11, 'test_username', '@test_username'),
        ('𝔓𝔢𝔫𝔤𝔲𝔦𝔫', 'test_username', '@test_username'),
        ('test' * 11, None, DEFAULT_AUTHOR),
        ('𝔓𝔢𝔫𝔤𝔲𝔦𝔫', None, DEFAULT_AUTHOR),
    ),
)
def test_get_author_ordinal(full_name, username, result, get_message):
    message = get_message(
        username=username,
        full_name=full_name,
    )
    assert get_author(message) == result


@pytest.mark.parametrize(
    'fwd_full_name,fwd_username,fwd_sender_name,result',
    (
        ('Test Testov', 'test', None, 'Test Testov'),
        ('test' * 11, 'test_username', None, '@test_username'),
        ('𝔓𝔢𝔫𝔤𝔲𝔦𝔫', 'test_username', None, '@test_username'),
        ('test' * 11, None, None, DEFAULT_AUTHOR),
        (None, None, 'Anonimus', 'Anonimus'),
        (None, None, 'Anonimus' * 11, DEFAULT_AUTHOR),
        (None, None, '𝔓𝔢𝔫𝔤𝔲𝔦𝔫', DEFAULT_AUTHOR),
    ),
)
def test_get_author_forward(fwd_full_name, fwd_username, fwd_sender_name, result, get_message):
    message = get_message(
        username='test_username',
        full_name='test_full_name',
        forward_full_name=fwd_full_name,
        forward_username=fwd_username,
        forward_sender_name=fwd_sender_name,
    )
    assert get_author(message) == result


async def test_welcome_user(get_message, call):
    message = get_message()
    await welcome_user(message)
    assert message.reply.mock_calls == [call(WELCOME_TEXT)]


async def test_send_cheat_sheet(get_message, call):
    message = get_message()
    await send_cheat_sheet(message)
    assert message.reply.mock_calls == [call(HELP_TEXT)]


async def test_detect_and_send_poem_positive(get_message, mocker, call, hokku_text):
    message = get_message(hokku_text)
    detect_poem_mock = mocker.patch('jpoetry.bot', 'detect_poem', Mock(return_value=detect_poem(hokku_text)))
    create_poem_image_mock = mocker.patch('jpoetry.bot', 'get_poem_image')
    input_file_mock = mocker.patch.object(bot, 'InputFile')
    send_message_mock = mocker.patch.object(bot, 'send_photo')

    await detect_and_send_poem(message)
    assert message.reply.mock_calls == []
    assert detect_poem_mock.mock_calls == [call(hokku_text)]
    assert create_poem_image_mock.mock_calls == [call(detect_poem_mock.return_value, 'test')]
    assert input_file_mock.mock_calls == [
        call(create_poem_image_mock.return_value, filename='test — Хокку.png')
    ]
    assert send_message_mock.mock_calls == [
        call(message.chat.id, input_file_mock.return_value, reply_to_message_id=message.message_id)
    ]


async def test_detect_and_send_poem_too_long(get_message, mocker, call, hokku_text):
    message = get_message(hokku_text)
    detect_poem_mock = mocker.patch.object(
        bot, 'detect_poem', return_value=detect_poem(hokku_text)
    )
    create_poem_image_mock = mocker.patch.object(
        bot, 'get_poem_image', side_effect=TooLongTextError
    )
    send_message_mock = mocker.patch.object(bot, 'send_photo')

    await detect_and_send_poem(message)
    assert message.reply.mock_calls == []
    assert detect_poem_mock.mock_calls == [call(hokku_text)]
    assert create_poem_image_mock.mock_calls == [call(detect_poem_mock.return_value, 'test')]
    assert send_message_mock.mock_calls == [
        call(message.chat.id, TOO_LONG_MESSAGE_FILE, reply_to_message_id=message.message_id)
    ]


async def test_detect_and_send_poem_negative(get_message, call, mocker):
    message = get_message('Not a poem')

    detect_poem_mock = mocker.patch.object(
        bot, 'detect_poem', return_value=detect_poem(message.text)
    )
    await detect_and_send_poem(message)
    assert detect_poem_mock.mock_calls == [call(message.text)]
    assert message.reply.mock_calls == []
