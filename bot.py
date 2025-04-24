import telebot
import requests
from bs4 import BeautifulSoup
import json

# توكين البوت
API_TOKEN = '7756130100:AAEZAgI4mVZyjV2HulvNtBBZurKhVIDFd-8'
bot = telebot.TeleBot(API_TOKEN)

# ----------------------------
# البحث من emobiletracker
# ----------------------------
def search_emobiletracker(number):
    try:
        url = f"https://www.emobiletracker.com/track/?phone={number}&submit=Track"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", class_="tracking-table")

        if not table:
            return "لا توجد بيانات من emobiletracker."

        rows = table.find_all("tr")
        results = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].text.strip()
                value = cols[1].text.strip()
                results.append(f"{key}: {value}")
        return "\n".join(results)
    except Exception as e:
        return f"خطأ emobiletracker: {e}"

# ----------------------------
# البحث من freecarrierlookup
# ----------------------------
def search_freecarrierlookup(number):
    try:
        url = f"https://freecarrierlookup.com/getcarrier.php?phonenumber={number}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.text.startswith("{"):
            data = json.loads(response.text)
            return f"مزود الخدمة: {data.get('carrier', 'غير معروف')}\nالنوع: {data.get('type', 'غير معروف')}"
        else:
            return "لا توجد نتائج من freecarrierlookup."
    except Exception as e:
        return f"خطأ freecarrierlookup: {e}"

# ----------------------------
# الاستجابة للرسائل
# ----------------------------
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.text.startswith("+") or message.text.isdigit():
        number = message.text.strip()
        bot.send_message(message.chat.id, "جارٍ فحص الرقم من مصادر متعددة...")

        result1 = search_emobiletracker(number)
        result2 = search_freecarrierlookup(number)

        final_msg = f"**نتائج البحث**\n\n[emobiletracker]\n{result1}\n\n[freecarrierlookup]\n{result2}"
        bot.send_message(message.chat.id, final_msg)
    else:
        bot.send_message(message.chat.id, "أرسل رقمًا يبدأ بـ + أو رقمًا فقط، بدون رموز أو حروف.")

# ----------------------------
# تشغيل البوت
# ----------------------------
bot.infinity_polling()