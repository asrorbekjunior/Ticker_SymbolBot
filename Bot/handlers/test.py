import yfinance as yf

import yfinance as yf

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


def calculate_close_minus_half_average(ticker):
    """
    Oxirgi kun closening narxidan o'rtachaning yarmisini ayiradi.
    
    Args:
        ticker (str): Aksiyaning belgilanishi (masalan, 'AAPL').
        
    Returns:
        float: Hisoblangan natija.
    """
    # Oxirgi kunning Close narxini olish
    stock_data = yf.Ticker(ticker).history(period="1d")
    last_close = stock_data['Close'].iloc[-1] if not stock_data.empty else 0

    # O'rtachani hisoblash
    average = analyze_stock(ticker)
    half_average = average / 2

    # Hisoblash
    result = last_close - half_average
    return result



def get_high_low_3_month(stock_symbol):
    # Stockni olish
    stock = yf.Ticker(stock_symbol)
    
    # 3 oy (90 kun) davomida ma'lumot olish
    data = stock.history(period="3mo")
    # 3 oy ichidagi eng yuqori (High) va eng past (Low) qiymatlarni olish
    highest_high = data['High'].max()
    lowest_low = data['Low'].min()
    
    return highest_high, lowest_low

# import yfinance as yf

def get_vix_info():
    # ^VIX - CBOE Volatility Index
    vix = yf.Ticker('^VIX')
    
    # CBOE Volatility Index nomi va joriy narxini olish
    vix_name = vix.info['shortName']
    vix_current_price = vix.history(period="1d")['Close'].iloc[0]
    
    return vix_name, vix_current_price


