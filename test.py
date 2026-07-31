import os
from dotenv import load_dotenv
import requests

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("CHAT_ID")

print(f"Token loaded: {bool(token)}")
print(f"Chat ID loaded: {bool(chat_id)}")

if token and chat_id:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": "سلام! ربات تستی با موفقیت متصل شد. 🚀"})
    print("Telegram Response:", response.json())
else:
    print("Error: Token or Chat ID is missing in .env file.")
