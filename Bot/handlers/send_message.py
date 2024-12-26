from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext
from telegram.error import TelegramError
from Bot.models import TelegramUser
from Bot.utils import is_user_admin

# Bosqichlarni belgilash
ASK_TYPE, GET_MESSAGE = range(2)

def get_user_ids():
    """
    Barcha foydalanuvchilarning `user_id` maydonlarini ro'yxat sifatida qaytaradi.
    """
    try:
        # Barcha user_id-larni olish
        user_ids = list(TelegramUser.objects.values_list('user_id', flat=True))
        return user_ids
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return []

# Admin uchun /send_message buyrug'i
def send_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if is_user_admin(chat_id) is False:  # Adminni tekshirish
        update.callback_query.edit_message_text("Sizni tushunmaadim")
        return ConversationHandler.END

    # Xabar turini tanlash uchun variantlar ['oddiy', 'photo', 'video', 'audio', 'file']
    inline_keyboard = [
        [InlineKeyboardButton("💬Text xabar💬", callback_data='text'), InlineKeyboardButton('🖼Rasmli xabar🖼', callback_data='photo')],
        [InlineKeyboardButton('🎞Video xabar🎞', callback_data='video'), InlineKeyboardButton('🔈Audio xabar🔈', callback_data='audio')],
        [InlineKeyboardButton('📁Fayl xabar📂', callback_data='file'), InlineKeyboardButton('🎙Ovozli xabar🎙', callback_data='voice')]
    ]

    update.callback_query.edit_message_text(
        "Xabar turini tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard)
    )
    return ASK_TYPE

# Xabar turini qabul qilish
def ask_type(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()  # Callback tugmalarini ishlatishda javob berish
    context.user_data['message_type'] = query.data
    query.edit_message_text("Endi xabarni yuboring:")
    return GET_MESSAGE

# Admin xabarni yuborganidan so'ng
def get_message(update: Update, context: CallbackContext):
    try:
        message_type = context.user_data.get('message_type')
        message_caption = update.message.caption_html if update.message.caption else ""
    except IndexError as e:
        print(e)
        return ConversationHandler.END

    # Userlarni olish
    user_ids = get_user_ids()
    total_users = 0

    # Xabarni barcha foydalanuvchilarga yuborish
    for user_id in user_ids:
        try:
            if message_type == 'text':
                context.bot.send_message(chat_id=user_id, text=update.message.text_html, parse_mode=ParseMode.HTML)
            elif message_type == 'photo':
                context.bot.send_photo(chat_id=user_id, photo=update.message.photo[-1].file_id, caption=message_caption, parse_mode=ParseMode.HTML)
            elif message_type == 'video':
                context.bot.send_video(chat_id=user_id, video=update.message.video.file_id, caption=message_caption, parse_mode=ParseMode.HTML)
            elif message_type == 'audio':
                context.bot.send_audio(chat_id=user_id, audio=update.message.audio.file_id, caption=message_caption, parse_mode=ParseMode.HTML)
            elif message_type == 'file':
                context.bot.send_document(chat_id=user_id, document=update.message.document.file_id, caption=message_caption, parse_mode=ParseMode.HTML)
            elif message_type == 'voice':
                context.bot.send_voice(chat_id=user_id, voice=update.message.voice.file_id, caption=message_caption, parse_mode=ParseMode.HTML)

            total_users += 1
        except TelegramError as e:
            print(f"Xatolik yuz berdi: {e}")

    # Adminga nechta foydalanuvchiga yuborilganini ko'rsatish
    update.message.reply_text(f"{total_users} ta foydalanuvchiga xabar yuborildi.")
    return ConversationHandler.END

# Bekor qilish funksiyasi
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Xabar yuborish bekor qilindi.")
    return ConversationHandler.END


send_msg_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(send_message, pattern='^send_messages$')],
    states={
        ASK_TYPE: [CallbackQueryHandler(ask_type)],  # CallbackQueryHandler qo'llaniladi
        GET_MESSAGE: [
            MessageHandler(Filters.text, get_message),
            MessageHandler(Filters.photo, get_message),
            MessageHandler(Filters.video, get_message),
            MessageHandler(Filters.audio, get_message),
            MessageHandler(Filters.voice, get_message),
            MessageHandler(Filters.document, get_message),
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
