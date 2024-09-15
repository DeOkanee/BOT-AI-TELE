import asyncio
from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
import os
from telebot.async_telebot import AsyncTeleBot

# Muat variabel lingkungan dari file .env
load_dotenv()

# Ambil API KEY dari variabel lingkungan
gemini_api_key = os.getenv("gemini_api_key")
telegram_bot_token = os.getenv("bot_token")

# Masukkan API KEY GEMINI & BOT TELEGRAM
bot = AsyncTeleBot(telegram_bot_token)

# Inisialisasi aplikasi Flask
app = Flask(__name__)

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

@app.route('/', methods=['GET'])
def home():
    return "Homepage"

@app.route('/contact', methods=['GET'])
def contact():
    return "Contact page"

@app.route('/status', methods=['GET'])
def status():
    # Cek status webhook Telegram
    webhook_url = f"https://api.telegram.org/bot{telegram_bot_token}/getWebhookInfo"
    try:
        response = requests.get(webhook_url)
        if response.status_code == 200:
            webhook_info = response.json()
            if webhook_info['result']['url']:
                return jsonify({"status": "Bot is online and webhook is set."})
            else:
                return jsonify({"status": "Bot is online but webhook is not set."})
        else:
            return jsonify({"status": f"Failed to get webhook info: {response.status_code} - {response.text}"})
    except Exception as e:
        return jsonify({"status": f"Error occurred: {str(e)}"})

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    webhook_url = f"https://bot-ai-tele.vercel.app/{telegram_bot_token}"
    url = f"https://api.telegram.org/bot{telegram_bot_token}/setWebhook?url={webhook_url}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify({"status": "Webhook set successfully"})
        else:
            return jsonify({"status": f"Failed to set webhook: {response.status_code} - {response.text}"})
    except Exception as e:
        return jsonify({"status": f"Error occurred: {str(e)}"})

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
    # Kirim pesan "Sedang mengetik"
    await bot.send_chat_action(message.chat.id, 'typing')
    
    # Dapatkan jawaban dari Gemini API
    response_text = await get_gemini_response(message.text)
    
    # Kirim jawaban ke user
    await bot.send_message(message.chat.id, response_text)

# Fungsi utama untuk menjalankan bot
def start_bot():
    asyncio.run(bot.polling())

if __name__ == "__main__":
    # Jalankan webhook set
    # Buat endpoint set webhook jika belum diatur
    asyncio.get_event_loop().run_until_complete(asyncio.gather(
        set_webhook()
    ))

    # Jalankan bot di background
    asyncio.get_event_loop().create_task(start_bot())
    # Jalankan server Flask
    app.run(debug=True)
