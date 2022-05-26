from itertools import islice

from aiogram.utils.markdown import bold, escape_md

from jpoetry.poetry import POEMS_INFO_MAP, POETRY_SYLLABLES
from jpoetry.text import agree_with_number


def get_known_poem_types() -> str:
    poem_types = (bold(p) for p in POETRY_SYLLABLES)
    poem_types_str = ', '.join(islice(poem_types, len(POETRY_SYLLABLES) - 1))
    poem_types_str += f' и {next(poem_types)}'
    return poem_types_str


def get_poem_types_cheat_sheet() -> str:
    text = ''
    for total_syllables, infos in POEMS_INFO_MAP.items():
        syllables_word = agree_with_number('слог', total_syllables)
        for info in infos:
            syllables_info = r'\+'.join(map(str, info.syllables))
            text += (
                rf'\- *{escape_md(info.genre)}*: '
                f'{syllables_info} — *{total_syllables}* {syllables_word}\n'
            )
    print(text)
    return text


POEM_TYPES_CHEAT_SHEET = get_poem_types_cheat_sheet()
POEM_TYPES = get_known_poem_types()
WELCOME_TEXT = f'Добавь меня в группу и я буду генерировать {POEM_TYPES} из подходящих сообщений'
HELP_TEXT = (
    rf'Я здесь чтобы генерировать {POEM_TYPES} из подходящих сообщений\.'
    f'\n\nХарактеристика жанров:\n\n{POEM_TYPES_CHEAT_SHEET}'
)
