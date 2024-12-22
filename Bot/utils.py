import openpyxl
from Bot.models import TelegramUser
from datetime import datetime
import yfinance as yf
import time

def save_telegram_user(user_data):
    user, created = TelegramUser.objects.update_or_create(
        user_id=user_data.id,
        defaults={
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
            'username': user_data.username,
            'last_active': datetime.now(),
            'status': 'active'
        }
    )
    return user

def is_avtive(user_id):
    user = TelegramUser.objects.get(user_id=user_id)
    if user.status in "active":
        return True
    else:
        return False
    

import yfinance as yf
import time
import pandas as pd



def remove_symbol_from_excel(ticker_symbol):
    try:
        # Excel faylini o'qish (fayl nomini moslashtiring)
        file_path = "Symbol.xlsx"
        df = pd.read_excel(file_path)

        # Aksiya simvolini o'chirish
        df = df[df['Symbol'] != ticker_symbol]

        # Yangilangan faylni saqlash
        df.to_excel(file_path, index=False)
        print(f"{ticker_symbol} aksiya Excel faylidan o'chirildi.")
    except Exception as e:
        print(f"Excel faylini yangilashda xatolik yuz berdi: {e}")



def get_average_abs_difference_with_percentage(ticker_symbol, percentage=3):
    try:

        ticker = yf.Ticker(ticker_symbol)
        hist_data = ticker.history(period="1mo")

        required_data = hist_data.loc[:, ['Open', 'Close']].copy()
        required_data.loc[:, 'Abs_Difference'] = abs(required_data['Close'] - required_data['Open'])

        average_difference = required_data['Abs_Difference'].mean()
        percentage_value = (average_difference * percentage) / 100

        end_time = time.time()

        return average_difference, percentage_value
    except Exception as e:
        print(f"Ma'lumotlarni olishda xatolik yuz berdi: {e}")
        # Excel faylidan aksiyani o'chirish
        remove_symbol_from_excel(ticker_symbol)
        return None, None



def check_if_difference_is_smaller_than_percentage(ticker_symbol, percentage=3):
    try:
        average_difference, percentage_value = get_average_abs_difference_with_percentage(ticker_symbol, percentage)

        if average_difference is None or percentage_value is None:
            return None

        ticker = yf.Ticker(ticker_symbol)
        hist_data = ticker.history(period="1d")

        close_price = hist_data['Close'].iloc[0]
        open_price = hist_data['Open'].iloc[0]

        today_abs_difference = abs(close_price - open_price)

        if today_abs_difference <= percentage_value:
            return today_abs_difference

        return None
    except Exception as e:
        print(f"Ma'lumotlarni olishda xatolik yuz berdi: {e}")
        # Excel faylidan aksiyani o'chirish
        remove_symbol_from_excel(ticker_symbol)
        return None


def get_stock_symbol(file_path):
    # Faylni ochish
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active 

    data = []
    for row in sheet.iter_rows(min_row=2, min_col=1, max_col=1, values_only=True):
        data.append(row[0])
    return data


