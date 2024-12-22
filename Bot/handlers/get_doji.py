from telegram import Update
from telegram.ext import CallbackContext
from Bot.utils import get_stock_symbol, check_if_difference_is_smaller_than_percentage
import time
from telegram.error import TelegramError
from Bot.models import TelegramUser
import yfinance as yf

def get_price_difference(stock_symbol):
    # Bugungi kunning aksiyalari haqida ma'lumotni olish
    stock_data = yf.download(stock_symbol, period="1d", interval="1m")
    
    # Agar stock_data bo'sh bo'lsa, xatolikni oldini olish
    if stock_data.empty:
        return "No data available for this stock symbol."

    # Open va Close narxlarini olish
    try:
        open_price = stock_data['Open'][0]  # Kun boshidagi narx
        close_price = stock_data['Close'][-1]  # Kun oxiridagi narx
    except KeyError:
        return "Error in fetching stock data."
    
    # Close va Open narxlari farqining mutlaq qiymatini hisoblash
    price_difference = abs(close_price - open_price)
    print(price_difference)
    return price_difference


def get_doji(update: Update, context: CallbackContext):
    # chat_id = context.job.context['chat_id']
    # Ushbu chat_id bo'yicha xabar yuborish
    index = 0
    context.bot.send_message(chat_id=6743781488, text="Jarayon boshlandi...")
    symbols = get_stock_symbol("Symbol.xlsx")
    for symbol in symbols:
        start_time = time.time()
        # time.sleep(3.5)
        # is_doji = get_average_abs_difference_with_percentage(symbol)
        tana =  check_if_difference_is_smaller_than_percentage(symbol)
        index += 1
        user_ids = TelegramUser.get_active_user_ids()
        
        if tana:
            for user_id in user_ids:
                try:
                    context.bot.send_message(chat_id=user_id ,text=f"<b>{symbol} Doji</b>", parse_mode="HTML")
                except TelegramError as e:
                    print(f"{user_id} - topilmadi>>> " + e)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{index}. Funksiya ishlash vaqti: {elapsed_time:.3f} soniya")
    update.message.reply_text("Barcha aksiyalar tekshirib chiqildi!")


