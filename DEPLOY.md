# 🚀 راهنمای استقرار روی alwaysdata (پلن رایگان)

## قدم ۱: آماده‌سازی فایل‌ها

فایل‌های زیر باید در پروژه باشند (قبلاً آماده شده‌اند):
```
ainewseveryday/
├── .env              ← تنظیمات تلگرام (این فایل Git نیست)
├── .env.example      ← نمونه فایل تنظیمات
├── run.py            ← اسکریپت اصلی اجرا
├── config.py
├── requirements.txt
├── collectors/
├── services/
└── utils/
```

## قدم ۲: ساخت فایل `.env` در ریشه پروژه

یک فایل به نام `.env` بسازید و این محتوا رو توش بذارید:

```
TELEGRAM_TOKEN=توکن_بات_تلگرام_خودتان
CHAT_ID=آیدی_چنل_یا_گروه_تلگرام
```

> **نکته:** توکن رو از @BotFather و Chat ID رو از @userinfobot بگیرید.

## قدم ۳: آپلود کد روی alwaysdata

### روش ۱: از طریق SSH (توصیه شده)

1. اول پروژه رو روی سیستم خودتون کامپرس کنید:
   ```bash
   cd Desktop
   tar -czf ainewseveryday.tar.gz ainewseveryday/
   ```

2. به سرور وصل بشید:
   ```bash
   ssh <نام_کاربری>@ssh.<دامنه>.alwaysdata.com
   ```

3. فایل رو آپلود و خالج کنید:
   ```bash
   scp ainewseveryday.tar.gz <نام_کاربری>@ssh.<دامنه>.alwaysdata.com:~/
   ```

4. وارد سرور بشید و خالج کنید:
   ```bash
   ssh <نام_کاربری>@ssh.<دامنه>.alwaysdata.com
   tar -xzf ainewseveryday.tar.gz
   ```

### روش ۲: از طریق File Manager (ساده‌تر)

1. وارد پنل alwaysdata بشید
2. به بخش **File Manager** برید
3. فایل‌ها رو یکی‌یکی آپلود کنید
4. یا کل پوشه رو Zip کنید و آپلود کنید

## قدم ۴: نصب وابستگی‌ها

از ترمینال alwaysdata:
```bash
cd ainewseveryday
pip install --user -r requirements.txt
```

> اگر `pip` کار نکرد:
> ```bash
> python3 -m pip install --user -r requirements.txt
> ```

## قدم ۵: تست اجرا

```bash
cd ainewseveryday
python run.py
```

اگر خطا گرفتید، لاگ‌ها رو ببینید:
```bash
cat bot.log
```

## قدم ۶: تنظیم Cron Job (اجرای خودکار روزانه)

1. وارد پنل alwaysdata بشید
2. به بخش **Cron Jobs** برید
3. یک Cron Job جدید بسازید:
   - **Schedule:** `0 12 * * *` (هر روز ساعت 12:00)
   - **Command:**
     ```bash
     cd /home/<نام_کاربری>/ainewseveryday && /usr/local/bin/python3 run.py >> bot.log 2>&1
     ```
   
   > **نکته:** مسیر `python3` ممکنه متفاوت باشه. برای پیدا کردنش:
   > ```bash
   > which python3
   > ```

4. ذخیره کنید

## قدم ۷: بررسی عملکرد

- بعد از اجرای Cron، فایل `bot.log` رو چک کنید
- اگر پیام "AI Tools digest sent successfully." دیدید، همه‌چیز درسته!
- اگر خطا دیدید، اول `TELEGRAM_TOKEN` و `CHAT_ID` رو بررسی کنید

---

## ❓ سوالات رایج

### سرور alwaysdata پایتون داره؟
بله! پلن رایگان alwaysdata از پایتون 3 پشتیبانی می‌کنه.

### Cloudflare Worker چی؟
برای این پروژه نیازی به Cloudflare Worker نیست. Cron Job خود alwaysdata کافیه. اگر روزی خواستید وب‌هوک (مثلاً Webhook تلگرام) اضافه کنید، اون‌وقت Cloudflare Worker می‌تونه مفید باشه.

### بات بدون Webhook کار می‌کنه؟
بله! این بات از **Cron Job** استفاده می‌کنه — هر روز خودش اجرا می‌شه و اخبار رو جمع‌آوری و ارسال می‌کنه. نیازی به Webhook یا سرور دائمی نیست.

### چطور پیام تلگرام رو تست کنم؟
می‌تونید مستقیماً `python run.py` رو اجرا کنید. اگر ایرادی باشه، توکن یا Chat ID اشتباهه.