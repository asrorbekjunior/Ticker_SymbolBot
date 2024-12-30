import yfinance as yf
import time
SYMBOL_FILE = "Symbol.xlsx"
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CallbackContext
from telegram.error import TelegramError
import pandas as pd
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, Updater
import openpyxl

def analyze_stock(ticker, date):
    """
    Aksiyaning kiritilgan sanadan bir oy oldingi tarixidan eng yuqori va past qiymatlar orasidagi o'rtachani hisoblaydi.
    """
    try:
        # Kiritilgan sanadan 1 oy oldingi sanani hisoblash
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=30)

        # Aksiyaning tarixiy ma'lumotlarini olish
        data = yf.Ticker(ticker).history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

        # High va Low qiymatlarni alohida listlarga yig'ish
        high_values = data['High'].tolist()
        low_values = data['Low'].tolist()

        result_list = []  # Chiqqan natijalarni yig'ish uchun

        while len(high_values) >= 5 and len(low_values) >= 5:
            # High va Low listlardan dastlabki 5 ta elementni olish
            top_5_high = high_values[:5]
            top_5_low = low_values[:5]

            # 5 ta High dan eng kattasini topish
            max_high = max(top_5_high)
            
            # 5 ta Low dan eng kichigini topish
            min_low = min(top_5_low)

            # Farqni hisoblash
            difference = max_high - min_low

            # Natijani result_list ga qo'shish
            result_list.append(difference)

            # Dastlabki 5 ta qiymatni o'chirish
            high_values = high_values[1:]
            low_values = low_values[1:]

        # O'rtacha qiymatni hisoblash
        return sum(result_list) / len(result_list) if result_list else 0

    except Exception as e:
        print(f"Ma'lumotlarni olishda xatolik yuz berdi: {e}")
        return None



def get_average_abs_difference_with_percentage(ticker_symbol, date, percentage=3):
    try:
        # Kiritilgan sanadan 1 oy oldingi sanani hisoblash
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=30)

        # Aksiyaning tarixiy ma'lumotlarini olish
        ticker = yf.Ticker(ticker_symbol)
        hist_data = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
        # print(hist_data)
        # Kerakli ustunlarni tanlash va mutlaq farqni hisoblash
        required_data = hist_data.loc[:, ['Open', 'Close']].copy()
        required_data['Abs_Difference'] = abs(required_data['Close'] - required_data['Open'])

        # O'rtacha mutlaq farqni hisoblash
        average_difference = required_data['Abs_Difference'].mean()

        # Foizni hisoblash
        percentage_value = (average_difference * percentage) / 100

        return average_difference, percentage_value

    except Exception as e:
        print(f"Ma'lumotlarni olishda xatolik yuz berdi: {e}")
        return None, None



def check_if_difference_is_smaller_than_percentage(ticker_symbol, date, percentage=3):
    try:
        # Kiritilgan sanadan 1 kun oldingi sanani hisoblash
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=1)

        # O'rtacha mutlaq farq va foizni olish
        average_difference, percentage_value = get_average_abs_difference_with_percentage(ticker_symbol, date, percentage)
        print(average_difference)
        print(percentage_value)
        if average_difference is None or percentage_value is None:
            return None

        # Aksiyaning tarixiy ma'lumotlarini olish
        ticker = yf.Ticker(ticker_symbol)
        hist_data = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
        # print(hist_data)
        # Ma'lumotlardan so'nggi kunning ochilish va yopilish narxlarini olish
        close_price = hist_data['Close'].iloc[0]
        open_price = hist_data['Open'].iloc[0]

        today_abs_difference = abs(close_price - open_price)
        # print(today_abs_difference)
        # Agar mutlaq farq foizdan kichik yoki teng bo'lsa, uni qaytarish
        if today_abs_difference <= percentage_value:
            return today_abs_difference

        return None

    except Exception as e:
        print(f"Ma'lumotlarni olishda xatolik yuz berdi: {e}")
        return None


# print(check_if_difference_is_smaller_than_percentage("ASML", '2024-12-13', 3))



def get_average_volume_with_percentage(ticker_symbol, date):
    try:
        # Kiritilgan sanadan 1 oy oldingi sanani hisoblash
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=30)

        # Aksiyaning tarixiy ma'lumotlarini olish
        ticker = yf.Ticker(ticker_symbol)
        hist_data = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
        
        # Kerakli ustunlarni tanlash (Volume) va o'rtacha hajmni hisoblash
        required_data = hist_data.loc[:, ['Volume']].copy()

        # O'rtacha volume qiymatini hisoblash
        average_volume = required_data['Volume'].mean()


        return average_volume

    except Exception as e:
        print(f"Ma'lumotlarni olishda xatolik yuz berdi: {e}")
        return None, None


def get_volume(symbol, date):
    """
    Berilgan aksiyaning kiritilgan sananing volume ma'lumotini qaytaradi.

    Args:
        symbol (str): Aksiya belgisi (ticker symbol).
        date (str): Kiritilgan sana (format: 'YYYY-MM-DD').

    Returns:
        int: Aksiya volume ma'lumoti o'sha sanada.
    """
    try:
        # Kiritilgan sanani datetime formatiga o'zgartirish
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date  # Bitta sana uchun start va end sana bir xil bo'ladi

        # Aksiyaning tarixiy ma'lumotlarini olish
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date.strftime("%Y-%m-%d"), end=start_date.strftime("%Y-%m-%d"))

        # Agar ma'lumot mavjud bo'lsa, volume qaytariladi
        if not data.empty:
            volume = data['Volume'].iloc[0]  # Kiritilgan sanadagi volume qiymati
            return int(volume)
        else:
            return 0  # Agar ma'lumot bo'lmasa 0 qaytarish
    except Exception as e:
        print(f"Xato yuz berdi: {e}")
        return None



def get_high_low_3_month(stock_symbol, date):
    """
    Kiritilgan sanadan 3 oylik (90 kunlik) ma'lumotni olib, eng yuqori va eng past qiymatlarni hisoblaydi.

    Args:
        stock_symbol (str): Aksiya belgisi (ticker symbol).
        date (str): Sana (format: 'YYYY-MM-DD').

    Returns:
        tuple: Eng yuqori (High) va eng past (Low) qiymatlar
    """
    try:
        # Kiritilgan sanani datetime obyektiga aylantirish
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=90)  # 3 oy oldingi sanani hisoblash

        # Aksiyaning tarixiy ma'lumotlarini olish
        stock = yf.Ticker(stock_symbol)
        data = stock.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

        # 3 oy ichidagi eng yuqori (High) va eng past (Low) qiymatlarni olish
        highest_high = data['High'].max()
        lowest_low = data['Low'].min()

        return highest_high, lowest_low
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None, None



def TakeProfit(symbol, average, date):
    """
    Kiritilgan sanadagi yopilish narxini olish va unga average ni qo'shish funksiyasi.

    :param symbol: str - Aksiya nomi (masalan, 'AAPL', 'GOOG')
    :param average: float - Qo'shiladigan qiymat
    :param date: str - Sana (format: 'YYYY-MM-DD')
    :return: float - Sana bo'yicha yopilish narxi va average yig'indisi
    """
    try:
        # Kiritilgan sanani datetime obyektiga aylantirish
        target_date = datetime.strptime(date, "%Y-%m-%d")

        # Aksiya ma'lumotlarini yuklash
        stock = yf.Ticker(symbol)
        hist = stock.history(start=target_date.strftime("%Y-%m-%d"), end=target_date.strftime("%Y-%m-%d"))

        if hist.empty:
            print(f"{date} sanasida ma'lumot topilmadi.")
            return None

        # Kiritilgan sanadagi yopilish narxini olish
        last_close_price = hist["Close"].iloc[0]

        # Qo'shilgan qiymat bilan natijani qaytarish
        return last_close_price + average

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None



def get_current_price(ticker_symbol, date=None):
    """
    Aksiyaning hozirgi narxini yoki kiritilgan sanadagi yopilish narxini qaytaradi.
    
    Args:
        ticker_symbol (str): Aksiyaning belgilanishi (masalan, 'AAPL').
        date (str, optional): Sana (format: 'YYYY-MM-DD'). Agar berilsa, o'sha sana bo'yicha yopilish narxini oladi.
        
    Returns:
        float: Aksiyaning hozirgi yoki kiritilgan sanadagi yopilish narxi.
    """
    try:
        stock = yf.Ticker(ticker_symbol)

        if date:
            # Kiritilgan sanani datetime obyektiga aylantirish
            target_date = datetime.strptime(date, "%Y-%m-%d")

            # Aksiyaning ma'lumotlarini olish
            hist = stock.history(start=target_date.strftime("%Y-%m-%d"), end=target_date.strftime("%Y-%m-%d"))
            if hist.empty:
                print(f"{date} sanasida ma'lumot topilmadi.")
                return None
            return hist['Close'].iloc[0]  # Kiritilgan sanadagi yopilish narxini qaytarish
        else:
            # Hozirgi kunning yopilish narxini olish
            current_price = stock.history(period="1d")['Close'].iloc[-1]
            return current_price

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None

def get_stock_symbol(file_path):
    # Faylni ochish
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active 

    data = []
    for row in sheet.iter_rows(min_row=2, min_col=1, max_col=1, values_only=True):
        data.append(row[0])
    return data


def calculate_close_minus_half_average(ticker, date=None):
    """
    Oxirgi kun closening narxidan o'rtachaning yarmisini ayiradi.
    
    Args:
        ticker (str): Aksiyaning belgilanishi (masalan, 'AAPL').
        date (str, optional): Sana (format: 'YYYY-MM-DD'). Agar berilsa, o'sha sana bo'yicha hisoblashni amalga oshiradi.
        
    Returns:
        float: Hisoblangan natija.
    """
    try:
        # Aksiyaning ma'lumotlarini olish
        stock = yf.Ticker(ticker)

        if date:
            # Kiritilgan sanani datetime obyektiga aylantirish
            target_date = datetime.strptime(date, "%Y-%m-%d")

            # Aksiyaning ma'lumotlarini olish
            hist = stock.history(start=target_date.strftime("%Y-%m-%d"), end=target_date.strftime("%Y-%m-%d"))
            if hist.empty:
                print(f"{date} sanasida ma'lumot topilmadi.")
                return None
            last_close = hist['Close'].iloc[0]  # Kiritilgan sanadagi yopilish narxini olish
        else:
            # Oxirgi kunning Close narxini olish
            stock_data = stock.history(period="1d")
            last_close = stock_data['Close'].iloc[-1] if not stock_data.empty else 0

        # O'rtachani hisoblash
        average = analyze_stock(ticker, date)
        half_average = average / 2

        # Hisoblash
        result = last_close - half_average
        return result

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None


def calculate_avg_volume_close_multiplier(ticker_symbol, date=None):
    """
    Aksiyaning bir oylik volume o'rtachasini oladi va uni oxirgi close qiymatiga ko'paytirib natijani qaytaradi.
    
    Args:
        ticker_symbol (str): Aksiyaning belgilanishi (masalan, 'AAPL').
        date (str, optional): Sana (format: 'YYYY-MM-DD'). Agar berilsa, o'sha sana bo'yicha hisoblashni amalga oshiradi.
        
    Returns:
        float: Bir oylik volume o'rtachasining oxirgi close qiymatiga ko'paytmasi.
    """
    try:
        # Bugungi sana va o'tgan bir oy
        if date:
            # Kiritilgan sanani datetime obyektiga aylantirish
            end_date = datetime.strptime(date, "%Y-%m-%d")
            start_date = end_date - timedelta(days=30)
        else:
            # Agar sana berilmasa, hozirgi sana va bir oylik davr
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

        # Ma'lumotlarni yuklab olish
        stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)

        if stock_data.empty:
            print("Ma'lumotlar topilmadi.")
            return None

        # Volume o'rtachasi va oxirgi Close qiymatini olish
        avg_volume = stock_data['Volume'].mean()  # Bir oylik volume o'rtachasi
        last_close = stock_data['Close'].iloc[-1]  # Oxirgi close qiymati

        # Hisoblash
        result = avg_volume * last_close
        return result

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None


# Sana olish uchun ConversationHandler bosqichlarini aniqlaymiz
DATE = 1

def start(update: Update, context: CallbackContext):
    """Foydalanuvchi /start komandasini yuborganida, sana olishni boshlash."""
    update.message.reply_text("Iltimos, sana kiriting (YYYY-MM-DD formatida):")
    return DATE


def get_date_from_user(update: Update, context: CallbackContext):
    """Foydalanuvchidan sana olish va jarayonni davom ettirish."""
    date_str = update.message.text.strip()

    try:
        # Agar sana datetime obyekti bo'lsa, uni stringga o'tkazish
        if isinstance(date_str, datetime):
            date_str = date_str.strftime("%Y-%m-%d")

        # Sana formatini tekshirish va datetime obyektiga aylantirish
        date = date_str
        
        # Endi sana obyekti to'g'ri formatda
        symbols = get_stock_symbol(SYMBOL_FILE)  # Aksiyalar ro'yxatini yangilash
        process_stocks(symbols, date, update, context)  # Sana parametrini o'tkazish
        update.message.reply_text("Jarayon tugadi!")
        return ConversationHandler.END  # Jarayon tugadi
    except ValueError:
        update.message.reply_text("Noto'g'ri sana formati. Iltimos, YYYY-MM-DD formatida kiriting.")
        return DATE  # Sana formatini qayta so'rash

def process_stocks(symbols, date, update, context):
    index = 0
    user_ids = [6743781488, 6194484795]  # Userlarning IDlarini olish

    for symbol in symbols:
        start_time = time.time()
        tana = check_if_difference_is_smaller_than_percentage(symbol, date)

        index += 1
        
        if tana:
            # Volume-ni olish
            volume = get_volume(symbol, date)  # Sana parametrini qo'shish
            average = analyze_stock(symbol, date)  # Sana parametrini qo'shish
            high_value, low_value = get_high_low_3_month(symbol, date)  # Sana parametrini qo'shish
            take_profit = TakeProfit(symbol, average, date)
            stock_data = yf.download(symbol, start=date, end=date, period="1d", interval="1m")
            
            if stock_data.empty:
                continue

            close_price = stock_data['Close'].iloc[-1]
            if isinstance(high_value, pd.Series):
                high_value = high_value.iloc[0]  # Birinchi qiymatni olish
            if isinstance(average, pd.Series):
                average = average.iloc[0]  # Birinchi qiymatni olish

            # Agar close_price Series bo'lsa, faqat bitta qiymatini olish
            if isinstance(close_price, pd.Series):
                close_price = close_price.iloc[0]
            pricee = get_current_price(symbol, date)
            stop_loss = calculate_close_minus_half_average(symbol, date)
            formula = int(calculate_avg_volume_close_multiplier(symbol, date))
            
            if pricee > 1 and formula > 1000000:
                message = f"""
<b>Wal-Mart ({symbol}) Doji</b> ✅  
- <b>Hozirgi narx:</b> ${pricee:.2f}  
- <b>Savdo hajmi (Volume):</b> {volume}
- <b>1 oylik o'rtacha ko'rsatkich:</b> {average:.2f} 

---

<b>CBOE Volatility Index (VIX)</b>  
- <b>Hozirgi narx:</b> 15.95  

---

<b>Savdo Tavsiyalari</b>  
- <b>Stop Loss:</b> $199.56  
- <b>Take Profit:</b> $212.93  



<blockquote>{symbol} Doji ✅</blockquote>
<b>Current price: {pricee:.2f}
Volume: {volume}
Average: {average:.2f}
——————————
Stop Loss: {stop_loss:.2f}
Take Profit: {take_profit:.2f}
</b>
"""
            else:
                message = f"""
<blockquote>{symbol} Doji ❌</blockquote>
<b>Current price: {pricee:.2f}
Volume: {volume}
Average: {average:.2f}
——————————
Stop Loss: {stop_loss:.2f}
Take Profit: {take_profit:.2f}
</b>
"""

            # Foydalanuvchilarga xabar yuborish
            for user_id in user_ids:
                try:
                    context.bot.send_message(
                        chat_id=6743781488,
                        text=message,
                        parse_mode="HTML"
                    )
                except TelegramError as e:
                    print(f"{user_id} - topilmadi>>> {e}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{index}. Funksiya ishlash vaqti: {elapsed_time:.2f} soniya")
    
    update.message.reply_text("Barcha aksiyalar tekshirib chiqildi!")

def cancel(update: Update, context: CallbackContext):
    """Foydalanuvchi /cancel komandasini yuborganida, jarayonni to'xtatish."""
    update.message.reply_text("Jarayon to'xtatildi.")
    return ConversationHandler.END

def main():
    updater = Updater(token="7723160549:AAF_X5F3Ec0tWct2_vZkGLXnv5730YIGMUo")
    dp = updater.dispatcher

    # ConversationHandlerni yaratamiz
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],  # /start komandasini kutamiz
        states={
            DATE: [MessageHandler(Filters.text & ~Filters.command, get_date_from_user)]  # Sana olish
        },
        fallbacks=[CommandHandler('cancel', cancel)]  # /cancel komandasini kutamiz
    )
    dp.add_handler(conversation_handler)

    updater.start_polling()
    updater.idle()

if __name__=="__main__":
    main()