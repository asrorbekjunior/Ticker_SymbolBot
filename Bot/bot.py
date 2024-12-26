from telegram import Update
from Config.settings import BOT_TOKEN
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, MessageHandler, ConversationHandler, CallbackQueryHandler, JobQueue
from Bot.botcommands.start_commands import start_command
from Bot.handlers.get_doji import run_dojii, start_doji_func
from Bot.handlers.send_message import send_msg_handler
from Bot.handlers.botstats import bot_stats
from Bot.bot_admin.admin_menyu import admin_menu
from Bot.bot_admin.add_admin import start_make_admin
import pytz


# Toshkent vaqti (UTC+5)
tz = pytz.timezone('Asia/Tashkent')


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Bu yordam komandasi!")
    return ConversationHandler.END

# Botni ishga tushirish funksiyasi
def run_bot():
    """
    Telegram botni ishga tushiruvchi funksiya
    """
    updater = Updater(BOT_TOKEN)
    job_queue = updater.job_queue

    updater.dispatcher.add_handler(CommandHandler("start", start_command))
    updater.dispatcher.add_handler(CommandHandler('start_doji', start_doji_func))
    updater.dispatcher.add_handler(CommandHandler('run_doji', run_dojii))
    updater.dispatcher.add_handler(send_msg_handler)
    updater.dispatcher.add_handler(CommandHandler('Admin', admin_menu))
    updater.dispatcher.add_handler(CallbackQueryHandler(bot_stats, pattern=r'^botstats$'))
    updater.dispatcher.add_handler(CallbackQueryHandler(start_make_admin, pattern="^add_admin$"))

    updater.dispatcher.add_handler(MessageHandler(Filters.all, help_command))
    # Botni ishga tushirish
    updater.start_polling()
    # updater.idle()
