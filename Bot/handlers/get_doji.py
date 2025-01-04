from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from Bot.utils import get_stock_symbol, check_if_difference_is_smaller_than_percentage
import time
from Config.settings import SYMBOL_FILE
import threading
from telegram.error import TelegramError
from Bot.models import TelegramUser
from .test import analyze_stock, get_high_low_3_month, calculate_close_minus_half_average
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import asyncio
from googletrans import Translator





def calculate_avg_volume_close_multiplier(ticker_symbol):
    """
    Aksiyaning bir oylik volume o'rtachasini oladi va uni oxirgi close qiymatiga ko'paytirib natijani qaytaradi.
    
    Args:
        ticker_symbol (str): Aksiyaning belgilanishi (masalan, 'AAPL').
        
    Returns:
        float: Bir oylik volume o'rtachasining oxirgi close qiymatiga ko'paytmasi.
    """
    # Bugungi sana va o'tgan bir oy
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Ma'lumotlarni yuklab olish
    stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
    
    if stock_data.empty:
        return None
    
    # Volume o'rtachasi va oxirgi Close qiymatini olish
    avg_volume = stock_data['Volume'].mean()  # Bir oylik volume o'rtachasi
    last_close = stock_data['Close'].iloc[-1]  # Oxirgi close qiymati
    
    # Hisoblash
    result = avg_volume * last_close
    return result

def get_current_price(ticker_symbol):
    """
    Aksiyaning hozirgi narxini qaytaradi.
    
    Args:
        ticker_symbol (str): Aksiyaning belgilanishi (masalan, 'AAPL').
        
    Returns:
        float: Aksiyaning hozirgi narxi.
    """
    # Aksiyaning ma'lumotlarini olish
    stock = yf.Ticker(ticker_symbol)
    current_price = stock.history(period="1d")['Close'].iloc[-1]
    
    return current_price

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



def TakeProfit(symbol, average):
    """
    Aksiyaning oxirgi kundagi narxini olish va unga average ni qo'shish funksiyasi.

    :param symbol: str - Aksiya nomi (masalan, 'AAPL', 'GOOG')
    :param average: float - Qo'shiladigan qiymat
    :return: float - Oxirgi narx va average yig'indisi
    """
    try:
        # Aksiya ma'lumotlarini yuklash
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")

        # Oxirgi kundagi yopilish narxini olish
        last_close_price = hist["Close"].iloc[-1]

        # Qo'shilgan qiymat bilan natijani qaytarish
        return last_close_price + average

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None



def get_volume(symbol):
    """
    Berilgan aksiyaning oxirgi kunlik volume ma'lumotini qaytaradi.
    
    Args:
        symbol (str): Aksiya belgisi (ticker symbol).
    
    Returns:
        int: Aksiya volume ma'lumoti.
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")  # Oxirgi 1 kunlik ma'lumotni olish
        if not data.empty:
            volume = data['Volume'].iloc[-1]  # Oxirgi kunning volume qiymati
            return int(volume)
        else:
            return 0  # Agar ma'lumot bo'lmasa 0 qaytarish
    except Exception as e:
        print(f"Xato yuz berdi: {e}")
        return None


import yfinance as yf

def get_stock_name(ticker):
    """
    Aksiyaning ticker kodiga asoslangan holda uning to'liq nomini qaytaradi.

    Args:
        ticker (str): Aksiyaning ticker kodi (masalan, "AAPL").

    Returns:
        str: Aksiyaning to'liq nomi yoki xato xabari.
    """
    try:
        stock = yf.Ticker(ticker)
        name = stock.info.get('longName', 'Nom topilmadi')
        return name
    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"



def run_dojii(update: Update, context: CallbackContext):
    threading.Thread(target=get_doji, args=(update, context,), daemon=True).start()


async def translator_func(text):
    translator = Translator()

    translated = await translator.translate(text, dest="uz")
    return translated.text

def get_doji(update: Update, context: CallbackContext):
    user_ids = TelegramUser.get_active_user_ids()
    index = 0
    update.message.reply_text(text="Jarayon boshlandi...")
    symbols = get_stock_symbol(SYMBOL_FILE)

    for symbol in symbols:
        start_time = time.time()
        time.sleep(1.5)
        tana = check_if_difference_is_smaller_than_percentage(symbol)
        index += 1

        if tana:
            volume = get_volume(symbol)
            average = analyze_stock(symbol)
            high_value, low_value = get_high_low_3_month(symbol)
            take_profit = TakeProfit(symbol, average)
            stock_data = yf.download(symbol, period="1d", interval="1m")
            if stock_data.empty:
                continue
            close_price = stock_data['Close'].iloc[-1]

            if isinstance(high_value, pd.Series):
                high_value = high_value.iloc[0]
            if isinstance(average, pd.Series):
                average = average.iloc[0]
            ticker_name = get_stock_name(symbol)
            if isinstance(close_price, pd.Series):
                close_price = close_price.iloc[0]
            pricee = get_current_price(symbol)
            stop_loss = calculate_close_minus_half_average(symbol)
            formula = int(calculate_avg_volume_close_multiplier(symbol))

            # Sector va Industry ma'lumotlarini olish
            ticker = yf.Ticker(symbol)
            sector = ticker.info.get('sector', 'Maʼlum emas')
            industry = ticker.info.get('industry', 'Maʼlum emas')
            description = ticker.info.get('longBusinessSummary', 'Tavsif mavjud emas.')
            uz_description = asyncio.run(translator_func(description))
            # URL yaratish
            if sector != 'Maʼlum emas' and industry != 'Maʼlum emas':
                sector_safe = sector.lower().replace(' ', '-').replace('&', 'and')
                industry_safe = industry.lower().replace(' ', '-').replace('&', 'and')
                industry_url = f"https://finance.yahoo.com/sectors/{sector_safe}/{industry_safe}"
                sector_url = f"https://finance.yahoo.com/sectors/{sector_safe}"
            else:
                industry_url = "#"
                sector_url = "#"

            # Yangiliklarni olish
            news = ticker.news[:3]
            news_buttons = [
                InlineKeyboardButton(
                    text=item['title'][:50],
                    url=item['link']
                ) for item in news
            ]
            keyboard = InlineKeyboardMarkup([[button] for button in news_buttons])

            if pricee > 1 and formula > 1000000:
                message = f"""
<blockquote><b>{ticker_name} ({symbol}) Doji</b> ✅ </blockquote> 
- <b>Current price:</b> ${pricee:.2f}  
- <b>Volume:</b> {volume}  
- <b>Sector:</b> <a href="{sector_url}">{sector}</a>   
- <b>Industry:</b> <a href="{industry_url}">{industry}</a>  

---

<b>Savdo Tavsiyalari</b>  
- <b>Stop Loss:</b> ${stop_loss:.2f}  
- <b>Take Profit:</b> ${take_profit:.2f}  

---
<blockquote expandable>
<b>Company Description:</b>  
{uz_description}
</blockquote>  
"""
            else:
                message = f"""
<blockquote><b>{ticker_name} ({symbol}) Doji</b> ❌ </blockquote> 
- <b>Current price:</b> ${pricee:.2f}  
- <b>Volume:</b> {volume}  
- <b>Sector:</b> <a href="{sector_url}">{sector}</a>   
- <b>Industry:</b> <a href="{industry_url}">{industry}</a>

---

<b>Savdo Tavsiyalari</b>  
- <b>Stop Loss:</b> ${stop_loss:.2f}  
- <b>Take Profit:</b> ${take_profit:.2f}  

---
<blockquote expandable>
<b>Company Description:</b>  
{uz_description}  
</blockquote>
"""

            # Foydalanuvchilarga xabar yuborish
            for user_id in user_ids:
                try:
                    context.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode="HTML",
                        reply_markup=keyboard,
                        disable_web_page_preview=True
                    )
                except TelegramError as e:
                    print(f"{user_id} - topilmadi>>> {e}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{index}. Funksiya ishlash vaqti: {elapsed_time:.2f} soniya")
    for user_id in user_ids:
        try:
            context.bot.send_message(chat_id=user_id, text="Aksiyalarni tekshirish nihoyasiga yetdi!")
        except TelegramError as e:
            print(f"{user_id} ga yuborilmadi>>> {e}")



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


