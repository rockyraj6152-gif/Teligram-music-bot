import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Yahan quotes (' ') ke andar apna BotFather wala token dalein
TOKEN = '8972026456:AAFlTa2LjNGFiowBcJfmJ0f9WWcyenTz8eA'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Namaste! Gaane ka naam ya YouTube link bhejo, main audio bhej dunga.")

def download_audio(query: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'default_search': 'ytsearch1:',
        'quiet': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        return f"{base}.mp3"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    status_msg = await update.message.reply_text("Gaana search aur download ho raha hai...")

    loop = asyncio.get_running_loop()
    try:
        file_path = await loop.run_in_executor(None, download_audio, query)
        await status_msg.edit_text("Audio upload ho raha hai...")
        with open(file_path, 'rb') as audio:
            await update.message.reply_audio(audio=audio)
            
        if os.path.exists(file_path):
            os.remove(file_path)
            
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"Error: {str(e)}")

def main():
    os.makedirs('downloads', exist_ok=True)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot chalu ho gaya hai!")
    app.run_polling()

if __name__ == '__main__':
    main()
