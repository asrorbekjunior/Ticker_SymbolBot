from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, CallbackQueryHandler
from ..models import TelegramUser  # Django modelingizni import qiling
from ..decorators import admin_required
# Conversation bosqichlari
SELECT_ADMIN, CONFIRM_REMOVE = range(2)

@admin_required
def start_remove_admin(update: Update, context: CallbackContext) -> int:
    """
    Adminlikdan o'chirish jarayonini boshlaydi.
    """
    admins = TelegramUser.objects.filter(is_admin=True)

    if not admins.exists():
        update.message.reply_text("Hozircha hech qanday admin yo'q.")
        return ConversationHandler.END

    # Inline tugmalarni yaratish
    keyboard = [
        [InlineKeyboardButton(f"{admin.first_name} @{admin.username}" if admin.username else admin.first_name, 
                              callback_data=f"remove_admin_{admin.user_id}")]
        for admin in admins
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Iltimos, adminlikdan o'chirmoqchi bo'lgan foydalanuvchini tanlang:", reply_markup=reply_markup)
    return SELECT_ADMIN

@admin_required
def select_admin(update: Update, context: CallbackContext) -> int:
    """
    Tanlangan adminni qayta ishlash.
    """
    query = update.callback_query
    query.answer()

    # Admin user_id ni olish
    user_id = int(query.data.split("_")[-1])
    context.user_data['remove_user_id'] = user_id

    user = TelegramUser.objects.get(user_id=user_id)

    query.edit_message_text(
        f"Siz {user.first_name} @{user.username} (ID: {user_id}) ni adminlikdan o'chirmoqchisiz. Tasdiqlaysizmi? (Ha/Yo'q)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Ha", callback_data="confirm_remove"), 
             InlineKeyboardButton("Yo'q", callback_data="cancel_remove")]
        ])
    )
    return CONFIRM_REMOVE

@admin_required
def confirm_remove(update: Update, context: CallbackContext) -> int:
    """
    Adminni o'chirishni tasdiqlash.
    """
    query = update.callback_query
    query.answer()

    user_id = context.user_data.get('remove_user_id')
    user = TelegramUser.remove_admin(user_id=user_id)

    if user:
        query.edit_message_text(f"{user.first_name} @{user.username} adminlikdan muvaffaqiyatli o'chirildi.")

        # Foydalanuvchiga xabar yuborish
        try:
            context.bot.send_message(
                chat_id=user.user_id,
                text="Siz adminlikdan o'chirildingiz."
            )
        except Exception as e:
            print(f"Xabar yuborishda xatolik yuz berdi: {e}")
    else:
        query.edit_message_text("Bunday foydalanuvchi topilmadi yoki admin emas.")

    return ConversationHandler.END

def cancel_remove(update: Update, context: CallbackContext) -> int:
    """
    Jarayonni bekor qilish.
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text("Adminlikdan o'chirish bekor qilindi.")
    return ConversationHandler.END

# ConversationHandler ni sozlash
remove_admin_handler = ConversationHandler(
    entry_points=[CommandHandler('remove_admin', start_remove_admin)],
    states={
        SELECT_ADMIN: [CallbackQueryHandler(select_admin, pattern="^remove_admin_")],
        CONFIRM_REMOVE: [
            CallbackQueryHandler(confirm_remove, pattern="^confirm_remove$"),
            CallbackQueryHandler(cancel_remove, pattern="^cancel_remove$"),
        ],
    },
    fallbacks=[],
)
