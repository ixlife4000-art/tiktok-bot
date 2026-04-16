import os
import tempfile
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ارسل رابط تيك توك")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("جاري التحميل...")

    with tempfile.TemporaryDirectory() as tmp:
        ydl_opts = {
            'outtmpl': f'{tmp}/%(title)s.%(ext)s',
            'format': 'mp4'
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file = ydl.prepare_filename(info)

            with open(file, 'rb') as f:
                await update.message.reply_video(f)

        except:
            await update.message.reply_text("صار خطأ")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))
    app.run_polling()

main()
