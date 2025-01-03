import yfinance as yf
from datetime import datetime

# Aksiyaning tickerini tanlang
ticker = yf.Ticker("AAPL")  # Apple Inc. misol

# Yangiliklar va sanoat ma'lumotlarini oling
news = ticker.news
industry = ticker.info.get('industry', 'Sanoat maʼlum emas')

# Natijani chop eting
print(f"Aksiya Sanoati: {industry}")
print("=" * 40)

for item in news:
    # Sana formatini o'zgartirish
    readable_date = datetime.utcfromtimestamp(item['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Sarlavha: {item['title']}")
    print(f"Havola: {item['link']}")
    print(f"Sana: {readable_date}")
    print("-" * 40)
