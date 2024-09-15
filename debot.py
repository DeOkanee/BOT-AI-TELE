import asyncio
from telebot.async_telebot import AsyncTeleBot
import requests
from dotenv import load_dotenv
import os

# Muat variabel lingkungan dari file .env
load_dotenv()

# Ambil API KEY dari variabel lingkungan
gemini_api_key = os.getenv("GEMINI_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

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

# Jalankan polling
asyncio.run(bot.polling())
