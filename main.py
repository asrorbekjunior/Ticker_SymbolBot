import yfinance as yf
import pandas as pd

def save_vix_data_to_excel(file_name="VIX_10_years.xlsx"):
    # VIX indeksining ticker kodi
    ticker = "^VIX"
    
    # 10 yillik vaqt oralig'ini aniqlash
    end_date = pd.Timestamp.today()
    start_date = end_date - pd.DateOffset(years=10)
    
    # Ma'lumotlarni yuklash
    vix_data = yf.download(ticker, start=start_date, end=end_date)
    
    # Agar ma'lumotlar mavjud bo'lsa, ularni Excel faylga saqlash
    if not vix_data.empty:
        vix_data.to_excel(file_name, engine="openpyxl")
        print(f"Ma'lumotlar muvaffaqiyatli saqlandi: {file_name}")
    else:
        print("Ma'lumotlarni yuklashda xatolik yuz berdi.")


def analyze_stock(ticker):
    """
    Aksiyaning 1 oylik tarixidan eng yuqori va past qiymatlar orasidagi o'rtachani hisoblaydi.
    """
    # Aksiyaning 1 oylik tarixini olish
    data = yf.Ticker(ticker).history(period="1mo")
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

    return sum(result_list) / len(result_list) if result_list else 0




def compare_stock_high_close_max(ticker, subtract_value):
    """
    3 oylik eng katta High qiymatdan ayirmani hisoblab, shartni tekshiradi.
    Agar shart bajarilmasa, average bilan ishlov berilgan qiymatni qaytaradi.

    :param ticker: Aksiya ticker kodi (masalan, AAPL, TSLA)
    :param subtract_value: High qiymatdan ayiriladigan qiymat
    :return: Shart bajarilmasa qaytadigan qiymat
    """
    # 3 oylik vaqt oralig'i
    end_date = pd.Timestamp.today()
    start_date = end_date - pd.DateOffset(months=3)
    
    # Ma'lumotlarni yuklash
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    
    if stock_data.empty:
        print("Ma'lumotlar topilmadi!")
        return None
    
    # 3 oy ichidagi eng katta High qiymat
    max_high = stock_data["High"].max()
    print(f"3 oy ichidagi eng katta High qiymati: {max_high}")
    
    # Modifikatsiyalangan High qiymat
    modified_high = max_high - subtract_value
    print(f"Modified High (ayirgandan keyin): {modified_high}")
    
    # Oxirgi Close qiymat
    last_close = stock_data["Close"].iloc[-1]
    print(f"Oxirgi Close qiymati: {last_close}")

    avg_high_if = stock_data["High"].max() - stock_data["Close"].iloc[-1]
    avg_value = (avg_high_if / 2) * 3 + last_close
    print(f"O'rtacha qiymat: {avg_value}")

    # Agar shart bajarilsa
    if float(modified_high) > float(last_close):
        if (float(avg_value) - float(subtract_value)) > float(last_close):
            print("O'rtacha qiymat: ", avg_value)
            return avg_value
        else:
            print(f"Shart bajarilmadi. 3 oylik eng katta High qiymat: {max_high}")
            return max_high
    else:
        result = (subtract_value / 2) * 3 + last_close
        print(f"Shart bajarilmadi. Hisoblangan natija: {result}")
        return result

# Funksiyani chaqirish
a = analyze_stock('AAPl')
print(a)
result = compare_stock_high_close_max(ticker="AAPL", subtract_value=a)
if result is not None:
    print(f"Qaytarilgan qiymat: {result}")
