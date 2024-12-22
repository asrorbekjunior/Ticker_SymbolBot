from telegram import Update
from Config.settings import BOT_TOKEN
from telegram.ext import Updater, CommandHandler, CallbackContext
from Bot.botcommands.start_commands import start_command
from Bot.handlers.get_doji import get_doji
import threading
from datetime import time
import pytz


# Toshkent vaqti (UTC+5)
tz = pytz.timezone('Asia/Tashkent')


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Bu yordam komandasi!")

def run_doji_thread(update: Update, context: CallbackContext):
    while True:
        # Har kuni soat 23:05da ishga tushirish uchun vaqtni hisoblash
        current_time = time.localtime()
        if current_time.tm_hour == 4 and current_time.tm_min == 20:
            # Bu yerda callback contextni uzatib get_doji funksi O'zingizning chat_id ni qo'ying
            # update = Update
            get_doji(update, context)  # get_doji funktsiyasini chaqiramiz
        time.sleep(60)  # Har 1 minutda tekshirib boradi

def start_doji_func(update: Update, context: CallbackContext):
    # Foydalanuvchiga xabar yuborish
    update.message.reply_text("Bot ishga tushdi va har kuni soat 4:20da get_doji funksiyasi ishga tushadi.")
    
    # Thread ishga tushurish
    threading.Thread(target=run_doji_thread, args=(update, context,), daemon=True).start()


# Botni ishga tushirish funksiyasi
def run_bot():
    updater = Updater(BOT_TOKEN)
    # Komandalarni ro'yxatdan o'tkazish
    updater.dispatcher.add_handler(CommandHandler("start", start_command))
    updater.dispatcher.add_handler(CommandHandler("help", help_command))
    updater.dispatcher.add_handler(CommandHandler('start_doji', start_doji_func))
    updater.dispatcher.add_handler(CommandHandler('run_doji', get_doji))

    # Botni ishga tushirish
    updater.start_polling()
    # updater.idle()
