from telegram import Update
from telegram.ext import CallbackContext
from Bot.models import TelegramUser
from Config.settings import BOT_TOKEN
from ..decorators import admin_required

def today_new_users():
    today_new_users = TelegramUser.get_today_new_users()
    return today_new_users.count()

@admin_required
def bot_stats(update: Update, context: CallbackContext):
    msg = update.callback_query
    msg.answer("Malumotlar yuklanmoqda...")
    bot_token = BOT_TOKEN
    blocked_count = TelegramUser.find_and_block_inactive_users(bot_token)
    bot = context.bot.get_me().username
    total_users = TelegramUser.get_total_users()
    active_users_count = TelegramUser.count_active_users()
    admin_users_count = TelegramUser.count_admin_users()


    msg.edit_message_text(text=f"""
<b>@{bot} ning statistikasi:

👥 <i>Bot foydalanuvchilar soni:</i> {total_users} ta
——————————
🆕 <i>Yangi qo'shilgan foydalanuvchilar soni:</i> {today_new_users()} ta
——————————
👮‍♂️ <i>Adminlar soni:</i> {admin_users_count} ta
——————————
🔥 <i>Faol foydalanuvchilar:</i> {active_users_count} ta
——————————
🚫 <i>Nofaol foydalanuvchilar:</i> {blocked_count} ta
</b>""", parse_mode="HTML")