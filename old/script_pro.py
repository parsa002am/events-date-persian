import requests
from bs4 import BeautifulSoup
import sqlite3

# اتصال به دیتابیس SQLite
conn = sqlite3.connect('eventspro.db')
cursor = conn.cursor()

# ایجاد جدول در دیتابیس
cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        is_holiday BOOLEAN,
        month TEXT,
        month_order INTEGER,
        day INTEGER,
        dateType TEXT
    )
''')

# فانکشن برای تشخیص نوع تاریخ و تبدیل ماه به عدد
def detect_date_type_and_convert_month(date_text):
    jalali_months = {
        'فروردین': 1, 'اردیبهشت': 2, 'خرداد': 3, 'تیر': 4,
        'مرداد': 5, 'شهریور': 6, 'مهر': 7, 'آبان': 8,
        'آذر': 9, 'دی': 10, 'بهمن': 11, 'اسفند': 12
    }
    gregorian_months = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    islamic_months = {
        'محرم': 1, 'صفر': 2, 'ربیع‌الاول': 3, 'ربیع‌الثانی': 4,
        'جمادی‌الاول': 5, 'جمادی‌الثانی': 6, 'رجب': 7, 'شعبان': 8,
        'رمضان': 9, 'شوال': 10, 'ذی‌القعده': 11, 'ذی‌الحجه': 12
    }
    
    if any(month in date_text for month in jalali_months):
        date_type = 'Jalali'
        month_order = next(jalali_months[month] for month in jalali_months if month in date_text)
    elif any(month in date_text for month in gregorian_months):
        date_type = 'Gregorian'
        month_order = next(gregorian_months[month] for month in gregorian_months if month in date_text)
    elif any(month in date_text for month in islamic_months):
        date_type = 'Islamic'
        month_order = next(islamic_months[month] for month in islamic_months if month in date_text)
    else:
        date_type = 'Jalali'
        month_order = 1  # پیش فرض، اگر ماه مشخص نشود

    return date_type, month_order

# فانکشن برای تبدیل اعداد فارسی به انگلیسی
def convert_persian_to_english_number(persian_number):
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    return ''.join(persian_to_english.get(c, c) for c in persian_number)

# تنظیمات درخواست
headers = {
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.9,fa-IR;q=0.8,fa;q=0.7,en-US;q=0.6',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'cookie': 'Province=8; City=95; ASP.NET_SessionId=g0arcu5yfcivmkfivwexs03c; __AntiXsrfToken=83e56a02a20546e5b8ead07085b6da3b',
    'origin': 'https://www.time.ir',
    'priority': 'u=1, i',
    'referer': 'https://www.time.ir/',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

# ارسال درخواست‌ها و پردازش داده‌ها
for month in range(1, 13):
    data = {
        'Year': 1403,
        'Month': month,
        'Base1': 0,
        'Base2': 1,
        'Base3': 2,
        'Responsive': 'true'
    }
    
    response = requests.post('https://www.time.ir/', headers=headers, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')

    # استخراج داده‌ها
    events = soup.select('ul.list-unstyled > li')
    for event in events:
        event_date_element = event.select_one('span[id^="ctl00_cphTop_Sampa_Web_View_EventUI_EventCalendarSimple"]')
        event_date = event_date_element.text.strip()
        event_name = event_date_element.find_next_sibling(text=True).strip()
        is_holiday = 'eventHoliday' in event.get('class', [])

        # تبدیل روز به عدد
        day = int(convert_persian_to_english_number(event_date.split()[0]))

        # تشخیص نوع تاریخ و تبدیل ماه به عدد
        date_type, month_order = detect_date_type_and_convert_month(event_date)

        # درج داده در دیتابیس
        cursor.execute('''
            INSERT INTO events (name, is_holiday, month, month_order, day, dateType)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_name, is_holiday, event_date.split()[1], month_order, day, date_type))

    conn.commit()

# بستن اتصال به دیتابیس
conn.close()
