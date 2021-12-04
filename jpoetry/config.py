import os
from pathlib import Path
from typing import Sequence

from PIL import Image
from fontTools.ttLib import TTFont

from jpoetry.image import ImageInfo, TextConfig, Coords, Color
from jpoetry.poetry import Genre, POETRY_SYLLABLES


DEFAULT_AUTHOR = "ниндзя, затаившийся за нечитаемым ником"
TOO_LONG_MESSAGE_FILE = (
    "AgACAgIAAxkBAANQYC0nNv64ProPLl7GykCCKLmOyCEAAvKxM"
    "Rsc-WhJ4jMWbH8J40VWUw-eLgADAQADAgADeQADbyQCAAEeBA"
)

RESOURCES = Path(__file__).parent.parent / "resources"
FONT = str(RESOURCES / "HanZi.ttf")
KNOWN_GLYPHS = {char for table in TTFont(FONT)["cmap"].tables for char in table.cmap}
BASE_COLOR = (94, 8, 8)  # dark
ACCENT_COLOR = (135, 15, 15)  # dark with red tint

BOT_TOKEN = os.environ["BOT_TOKEN"]


class AuthorConfig(TextConfig):
    coords: Coords = (-73, -59)
    colors: Sequence[Color] = [BASE_COLOR]
    max_font_size = 50
    min_font_size = 20
    max_line_width = 730
    anchor = "rs"


class PhrasesConfig(TextConfig):
    coords: Coords = (76, 215)
    max_line_width = 1140
    min_font_size = 40
    max_font_size = 65


PHRASES_INFO_BY_SYLLABLES: dict[int, PhrasesConfig] = {
    3: PhrasesConfig(colors=[BASE_COLOR] * 2 + [ACCENT_COLOR], max_font_size=65),
    5: PhrasesConfig(colors=[BASE_COLOR] * 4 + [ACCENT_COLOR], max_font_size=60),
    6: PhrasesConfig(colors=[BASE_COLOR] * 5 + [ACCENT_COLOR], max_font_size=55),
}

_AUTHOR_INFO = AuthorConfig()
POETRY_IMAGES_INFO: dict[Genre, ImageInfo] = {
    genre: ImageInfo(
        template_picture=Image.open(RESOURCES / f"{genre.name}.png"),
        text_fields={
            "phrases": PHRASES_INFO_BY_SYLLABLES[len(syllables)],
            "author": _AUTHOR_INFO,
        },
    )
    for genre, syllables in POETRY_SYLLABLES.items()
}
