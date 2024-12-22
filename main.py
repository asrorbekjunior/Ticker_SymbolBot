import logging
from datetime import time
import pytz
from telegram import Update
from telegram.ext import Updater, CommandHandler, JobQueue, CallbackContext
import asyncio

# Toshkent vaqti (UTC+5) 
tz = pytz.timezone('Asia/Tashkent')

# Asinxron get_doji funksiyasi
async def get_doji(context: CallbackContext):
    chat_id = context.job.context['chat_id']
    await context.bot.send_message(chat_id=chat_id, text="Get Doji is working!")

# Asinxron start funksiyasi
def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.job_queue.run_daily(
        get_doji, 
        time=time(4, 20),  # Toshkent vaqti bilan 4:20
        context={'chat_id': chat_id},  # Chat IDni yuboramiz
        days=(0, 1, 2, 3, 4, 5, 6),  # Har kuni
        tz=tz  # Toshkent vaqt zonasini belgilash
    )
    update.message.reply_text('Bot har kuni soat 4:20da get_doji funksiyasini ishga tushiradi.')

# Logging sozlash
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Botni ishga tushuradigan funksiya
def main():
    # Updater obyekti yaratish
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)

    # JobQueue uchun sozlash
    job_queue = updater.job_queue

    # /start komandasi uchun handler
    updater.dispatcher.add_handler(CommandHandler("start", start))

    # Botni boshlash
    updater.start_polling()

    # Botni orqa fonda ishlatish
    updater.idle()

if __name__ == '__main__':
    main()
