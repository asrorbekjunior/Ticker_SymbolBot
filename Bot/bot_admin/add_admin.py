from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from ..models import TelegramUser  # Django modelingizni import qiling
from ..decorators import admin_required
# ConversationHandler bosqichlari
ASK_USER_ID, CONFIRM = range(2)

@admin_required
def start_add_admin(update: Update, context: CallbackContext) -> int:
    """
    Admin qo'shishni boshlaydi.
    """
    update.callback_query.edit_message_text(
        "Iltimos, admin qilishni istagan foydalanuvchi ID sini kiriting:"
    )
    return ASK_USER_ID

@admin_required
def ask_user_id(update: Update, context: CallbackContext) -> int:
    """
    Foydalanuvchi ID ni qabul qiladi va tasdiqlashni so'raydi.
    """
    user_id = update.message.text

    if not user_id.isdigit():
        update.message.reply_text("ID faqat raqamlardan iborat bo'lishi kerak. Qaytadan kiriting.")
        return ASK_USER_ID

    context.user_data['user_id'] = int(user_id)

    update.message.reply_text(
        f"Foydalanuvchi ID: {user_id}. Ushbu foydalanuvchini admin qilishni tasdiqlaysizmi? (Ha/Yo'q)",
        reply_markup=ReplyKeyboardMarkup([["Ha", "Yo'q"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return CONFIRM

@admin_required
def confirm(update: Update, context: CallbackContext) -> int:
    """
    Tasdiqlash jarayoni.
    """
    choice = update.message.text.lower()
    user_id = context.user_data.get('user_id')

    if choice == "ha":
        user = TelegramUser.make_admin(user_id=user_id)
        if user:
            update.message.reply_text(f"Foydalanuvchi {user} admin qilindi.")
            context.bot.send_message(chat_id=user_id, text="Tabriklayman siz hozirgina admin bo'ldingiz")
        else:
            update.message.reply_text("Bunday foydalanuvchi topilmadi.")
    elif choice == "yo'q":
        update.message.reply_text("Amal bekor qilindi.")
    else:
        update.message.reply_text("Iltimos, faqat 'Ha' yoki 'Yo'q' deb javob bering.")
        return CONFIRM

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """
    Muloqotni bekor qiladi.
    """
    update.message.reply_text("Admin qo'shish bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ConversationHandler ni sozlash
add_admin_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_add_admin, pattern='^add_admin$')],
    states={
        ASK_USER_ID: [MessageHandler(Filters.text & ~Filters.command, ask_user_id)],
        CONFIRM: [MessageHandler(Filters.text & ~Filters.command, confirm)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
