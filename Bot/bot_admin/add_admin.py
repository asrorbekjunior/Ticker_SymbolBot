from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from Bot.models import TelegramUser
from Config.settings import SITE_URL
from Bot.utils import is_user_admin

def start_make_admin(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    is_admin = is_user_admin(user_id)
    inline = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="Web Admin Sayt", url=f"{SITE_URL}/admin/Bot/telegramuser/")
        ]
    ])
    if is_admin is True:
        update.callback_query.edit_message_text("Kimni admin qilmoqchisiz foydalanuvchining telegram ID sini kiritng\nYoki quyidagi tugma orqali web admin paneldan userni admin qiling", parse_mode="HTML", reply_markup=inline)