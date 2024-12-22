from telegram import Update
from telegram.ext import CallbackContext
from Bot.utils import save_telegram_user

def start_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    save_telegram_user(user)
    update.message.reply_text("Assalomu alaykum")