from collections.abc import Sequence

from PIL import Image

from jpoetry.config import ACCENT_COLOR, BASE_COLOR, RESOURCES
from jpoetry.image import Color, Coords, ImageInfo, TextConfig
from jpoetry.poetry import POETRY_PHRASES_SYLLABLES, Genre


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
    for genre, syllables in POETRY_PHRASES_SYLLABLES.items()
}
