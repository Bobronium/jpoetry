import os
from pathlib import Path

from fontTools.ttLib import TTFont


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

BOT_TOKEN = os.environ.get("BOT_TOKEN")
