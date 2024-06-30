import requests
import sqlite3

# تابع برای ارسال درخواست و دریافت داده‌ها
def fetch_events(month):
    url = f'https://taghvim.com/get_events/?action=get_events&month={month}'
    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9,fa-IR;q=0.8,fa;q=0.7,en-US;q=0.6',
        'cookie': 'csrftoken=Pj66QMeOvPIpp61pLQAJM8Gmo088bDWuFiGimMMr2UtejYP8L9AK24MkFbAyOpLo; sessionid=tof9rslfm840djwrb44lp413t8tef3xu',
        'priority': 'u=1, i',
        'referer': 'https://taghvim.com/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # برای چک کردن موفقیت درخواست
    return response.json()

# اتصال به دیتابیس SQLite و ساخت جدول
conn = sqlite3.connect('events.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        is_holiday BOOLEAN,
        month TEXT,
        month_order INTEGER,
        day INTEGER
    )
''')
conn.commit()

# دریافت داده‌ها برای ماه‌های 1 تا 12 و ذخیره در دیتابیس
for month in range(1, 13):
    events = fetch_events(month)
    for event in events:
        c.execute('''
            INSERT INTO events (name, is_holiday, month, month_order, day) 
            VALUES (?, ?, ?, ?, ?)
        ''', (event['name'], event['is_holiday'], event['month'], event['month_order'], event['day']))
    conn.commit()

# بستن اتصال به دیتابیس
conn.close()

print("داده‌ها با موفقیت دریافت و در دیتابیس ذخیره شدند.")