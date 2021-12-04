"""
TODO: think about upscaling images to apply antialiasing: https://habr.com/ru/post/247219/
"""

from io import BytesIO
from typing import Optional, Sequence

from PIL import ImageDraw, ImageFont
from PIL.ImageDraw import ImageDraw as ImageDrawType
from PIL.ImageFont import FreeTypeFont
from PIL.PngImagePlugin import PngImageFile

from jpoetry.config import FONT
from jpoetry.utils import DataModel


FontSize = int
Pixel = int
Coords = tuple[int, int]
Color = tuple[int, int, int]
Anchor = Optional[str]


class TextConfig(DataModel):
    coords: Coords
    colors: Sequence[Color]
    max_line_width: Pixel
    min_font_size: FontSize
    max_font_size: FontSize
    anchor: Anchor = None


class ImageInfo(DataModel):
    template_picture: PngImageFile
    text_fields: dict[str, TextConfig]


class TooLongTextError(ValueError):
    ...


def get_font(
    draw: ImageDrawType,
    lines: list[str],
    font: str,
    max_size: FontSize,
    min_size: FontSize,
    max_width: Pixel,
    avg_pixels_difference: Pixel = 62,
) -> tuple[FreeTypeFont, int, int]:
    """
    Finds the longest line and picks the biggest font to fit in max_width

    NOTE: longest line is not necessarily the one that has more chars: .. will be shorter than ——
    FIXME: now it's kind of doing bruteforce to find suitable size
    """
    line_height = 0
    longest_line_width = 0
    longest_line = ""
    font_ = None
    result_size = max_size

    for line in lines:  # find the longest line
        font_ = ImageFont.truetype(font, result_size)
        line_width, line_height = draw.textsize(line, font_)
        if line_width > longest_line_width:
            longest_line = line
            longest_line_width = line_width

    while longest_line_width > max_width:
        result_size -= max(1, (longest_line_width - max_width) // avg_pixels_difference)
        if result_size < min_size:
            raise TooLongTextError(
                f"Unable to fit text within min font size {min_size}"
            )

        font_ = ImageFont.truetype(font, result_size)
        longest_line_width, line_height = draw.textsize(longest_line, font_)

    if font_ is None:
        font_ = ImageFont.truetype(font, result_size)

    return font_, longest_line_width, line_height


def draw_text(
    img_info: ImageInfo, line_space_multiplier: float = 1.1, **text_lines: list[str]
) -> BytesIO:
    """
    Create image with given ImageInfo and text
    """
    img: PngImageFile = img_info.template_picture.copy()
    draw: ImageDrawType = ImageDraw.Draw(img)
    for name, text_info in img_info.text_fields.items():
        lines = text_lines.pop(name)
        number_of_lines = len(text_info.colors)
        if lines is None:
            raise TypeError(f"{img_info} requires {name} text")
        elif len(lines) != number_of_lines:
            raise ValueError(f"{img_info} requires {name} text with {number_of_lines=}")

        text_x, text_y = text_info.coords

        # treat negative values as offsets from down right corner of the image
        if text_x < 0:
            text_x = img.width + text_x
        if text_y < 0:
            text_y = img.height + text_y

        font, width, height = get_font(
            draw,
            lines=lines,
            font=FONT,
            max_size=text_info.max_font_size,
            min_size=text_info.min_font_size,
            max_width=text_info.max_line_width,
        )
        for phrase, color in zip(lines, text_info.colors):
            draw.text(
                (text_x, text_y), phrase, fill=color, font=font, anchor=text_info.anchor
            )
            text_y += int(height * line_space_multiplier)

    if text_lines:
        raise ValueError(
            f"Unknown line(s) {tuple(text_lines)} not found in {tuple(img_info.text_fields)}"
        )

    image_bytes = BytesIO()
    img.save(image_bytes, format="png")
    image_bytes.seek(0)
    # DEBUG
    img.show()
    return image_bytes
