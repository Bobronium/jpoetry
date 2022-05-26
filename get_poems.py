import asyncio
import json

from jpoetry.text import spell_number


with open('result.json') as r:
    results = json.load(r)


print(spell_number('1000000'))


async def main():
    print(len(results["messages"]))
    # for r in [] or results["messages"]:
    # try:
    #     text = r['text']
    #     if not text:
    #         continue
    #
    #     if isinstance(text, list):
    #         text = ' '.join(i['text'] if isinstance(i, dict) else i for i in text)
    #
    #     author = r.get('forwarded_from')
    #     if author is None:
    #         author = r["from"]
    #     poem = detect_poem(text)
    #     if poem is not None:
    #         print(poem)
    #         # poem = get_poem_image(poem, author)
    #         # await bot.send_photo(93212972, poem)
    #         # await asyncio.sleep(0.5)
    # except Exception as e:
    #     print(locals().get('text'), r, e)
    #     raise


asyncio.run(main())
