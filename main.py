import asyncio
from googletrans import Translator

async def translator_func(text):
    translator = Translator()

    translated = await translator.translate(text, dest="uz")
    return translated.text

# Async funktsiyani ishga tushirish
asyncio.run(translator_func())


# Natijani chop etish
# print("Asl matn:", text_to_translate)
# print("Tarjima qilingan matn:", translated.text)
# print("Asl til:", translated.src)
# print("Maqsadli til:", translated.dest)

