from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import CallbackContext, ConversationHandler
from Bot.utils import is_user_admin
from Config.settings import SITE_URL

admin_keyboard_list = [
    [
        InlineKeyboardButton(text="📨 Xabar yuborish", callback_data='send_messages'),
        InlineKeyboardButton(text="📊 Bot statistikasi", callback_data='botstats')
    ],
    [
        InlineKeyboardButton(text="👮‍♂️ Admin qo'shish", callback_data='add_admin'),
        InlineKeyboardButton(text="🙅‍♂️ Admin o'chirish", callback_data='delete_admin')
    ],
    [
        InlineKeyboardButton(text="🌐 Web Admin site", url=SITE_URL),
        InlineKeyboardButton(text="📱 Web Admin app", web_app=WebAppInfo(url=SITE_URL))
    ]
]
Admin_keyboard = InlineKeyboardMarkup(admin_keyboard_list)

def admin_menu(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    is_admin = is_user_admin(user_id)
    if is_admin is True:
        context.bot.send_message(
            chat_id=user_id, 
            text="<b>Salom Admin\nNima qilamiz bugun</b>", 
            parse_mode="HTML",
            reply_markup=Admin_keyboard
            )
        return ConversationHandler.END
