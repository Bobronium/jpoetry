import asyncio
import logging
from io import BytesIO
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.utils.markdown import escape_md
from aiogram.types import ContentType, InputFile, Message, ParseMode
from loguru import logger

from jpoetry.answers import HELP_TEXT, WELCOME_TEXT
from jpoetry.config import BOT_TOKEN, DEFAULT_AUTHOR, TOO_LONG_MESSAGE_FILE
from jpoetry.image import TooLongTextError, draw_text
from jpoetry.poetry import (
    POEMS_INFO_MAP,
    BadPhraseError,
    Poem,
    compose_phrases,
    detect_poem,
)
from jpoetry.templates import POETRY_IMAGES_INFO
from jpoetry.text import remove_unsupported_chars
from jpoetry.utils import Timer


# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN_V2, validate_token=False)
dp = Dispatcher(bot)


def get_author(message: Message, max_len: int = 40) -> str:
    """
    Find most suitable author name
    """
    if (not message.is_forward() and (user := message.from_user)) or (
        user := message.forward_from
    ):
        author = remove_unsupported_chars(user.full_name)

        if user.username and (
            len(author) > max_len or len(author) < len(user.full_name) / 2
        ):
            author = "@" + user.username
    else:  # it's forward, but user info is hidden
        author = remove_unsupported_chars(message.forward_sender_name)

    if not author or len(author) > max_len:
        return DEFAULT_AUTHOR
    return author


@dp.message_handler(
    lambda message: message.from_user.id == message.chat.id, commands=["start"]
)
async def welcome_user(message: Message) -> None:
    await message.reply(WELCOME_TEXT)


@dp.message_handler(commands=["help"])
async def send_cheat_sheet(message: Message) -> None:
    await message.reply(HELP_TEXT)


@dp.message_handler(commands=["info"])
async def print_info(message: Message) -> None:

    if not (message_to_reply := message.reply_to_message):
        message = await message.reply(escape_md("Пошёл нахуй)"))
        await asyncio.sleep(0.5)
        await message.delete()
        return

    poem, words_info, total_syllables = detect_poem(message_to_reply.text, strict=False)
    if poem is not None:
        await message_to_reply.reply(escape_md(repr(poem)))
    elif words_info is None or total_syllables is None:
        await message_to_reply.reply(escape_md("Ну хуй знает..."))
    else:
        await message_to_reply.reply(
            escape_md(
                " ".join(map(repr, words_info)) + f"\n\nИтого: {total_syllables}"
            )
        )


M = Path(__file__).parent / "messages.json"


# @dp.channel_post_handler(content_types=ContentType.ANY)
# @dp.edited_channel_post_handler(content_types=ContentType.ANY)
@dp.message_handler(content_types=ContentType.ANY)
@dp.edited_message_handler(content_types=ContentType.ANY)
async def detect_and_send_poem(message: Message) -> None:
    if message.text is None:
        return
    poem, _, _ = detect_poem(message.text)
    if poem is None:
        return

    author = get_author(message)
    try:
        with Timer("get_poem_image") as timer:
            image_data = await asyncio.get_event_loop().run_in_executor(
                None, get_poem_image, poem, author
            )
        logger.info(f"{poem.genre.name} image is created in {timer.elapsed:.4} seconds")
    except TooLongTextError:
        image = TOO_LONG_MESSAGE_FILE
        logger.error(f"Too many chars in {poem.genre.name}, sending default image")
    else:
        image = InputFile(image_data, filename=f"{author} — {poem.genre}.png")

    await bot.send_photo(message.chat.id, image, reply_to_message_id=message.message_id)


def get_poem_image(poem: Poem, author: str) -> BytesIO:
    return draw_text(
        POETRY_IMAGES_INFO[poem.genre], phrases=list(map(str, poem.phrases)), author=[f"— {author}"]
    )
