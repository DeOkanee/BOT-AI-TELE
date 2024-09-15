import telebot
from telebot.async_telebot import AsyncTeleBot
import requests
from dotenv import load_dotenv
from flask import Flask, request
import os

# Muat variabel lingkungan dari file .env
load_dotenv()

# Ambil API KEY dari variabel lingkungan
gemini_api_key = os.getenv("gemini_api_key")
telegram_bot_token = os.getenv("bot_token")

# Masukkan API KEY GEMINI & BOT TELEGRAM
bot = AsyncTeleBot(telegram_bot_token)

# Fungsi untuk mendapatkan respons dari Gemini API
async def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemini_api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    # Tampilkan respons API untuk debugging
    print("Respons API:", response.json())  # Tambahkan ini untuk melihat respons yang dikembalikan oleh API

    if response.status_code == 200:
        try:
            # Mendapatkan teks dari respons API dengan struktur yang benar
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "Maaf, tidak ada jawaban yang tersedia saat ini."
    else:
        return f"Maaf, terjadi kesalahan: {response.status_code} - {response.text}"

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Endpoint status untuk memeriksa apakah bot online
@app.route("/status", methods=["GET"])
def status():
    return "Bot is online", 200

# Fungsi untuk mengatur webhook
@app.route("/setwebhook", methods=["GET", "POST"])
def set_webhook():
    url = f"https://api.telegram.org/bot{telegram_bot_token}/setWebhook?url=https://bot-ai-tele.vercel.app/{telegram_bot_token}"
    r = requests.get(url)
    return f"Webhook status: {r.json()}"

# Fungsi utama untuk menerima update dari Telegram (via Webhook)
@app.route(f"/{telegram_bot_token}", methods=["POST"])
def receive_update():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Set up handlers untuk bot Telegram
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hallo, Saya versi kedua Google, Silakan tanya apa saja....
Waktu DEBOT menjawab akan menyesuaikan dari pertanyaan anda 😃🤔

# /menu
# /about
\
""")

@bot.message_handler(commands=['menu'])
async def send_menu(message):
    await bot.reply_to(message, """\
Jangan lupa mampir kak ⬇️
"https://profil-deoka.vercel.app/"
\
""")

@bot.message_handler(commands=['about'])
async def send_about(message):
    await bot.reply_to(message, """\
Ayo manfaatkan aplikasi telegram untuk kepentingan positif,
dan jadikan "TANYADEBOT" sebagai jawaban dari pertanyaanmu"
\
""")

@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.send_chat_action(message.chat.id, 'typing')
    
    # Dapatkan jawaban dari Gemini API
    response_text = await get_gemini_response(message.text)
    
    # Kirim jawaban ke user
    await bot.send_message(message.chat.id, response_text)

# Jalankan aplikasi Flask
if __name__ == "__main__":
    app.run(debug=True)
