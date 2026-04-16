import os
import tempfile
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
pending_links = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ارسل رابط تيك توك")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        async def continue_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    url = pending_links.get(user_id)
    if not url:
        await query.message.reply_text("ارسل الرابط من جديد")
        return

    await query.message.reply_text("جاري التحميل...")

    with tempfile.TemporaryDirectory() as tmp:
        ydl_opts = {
            "outtmpl": f"{tmp}/%(title)s.%(ext)s",
            "format": "mp4/best",
            "quiet": True,
            "noplaylist": True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            with open(file_path, "rb") as f:
                await query.message.reply_video(video=f)

        except Exception:
            await query.message.reply_text("صار خطأ")

    user_id = update.effective_user.id
    url = update.message.text.strip()

    pending_links[user_id] = url

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 زيارة الإعلان", url="https://t.me/tiktoknowatermarkbot")],
        [InlineKeyboardButton("✅ متابعة التحميل", callback_data="go")]
    ])

    await update.message.reply_text(
        "📢 شوف الإعلان ثم اضغط متابعة 👇",
        reply_markup=keyboard
    )

    url = update.message.text.strip()
    await update.message.reply_text("جاري التحميل...")

    with tempfile.TemporaryDirectory() as tmp:
        ydl_opts = {
            "outtmpl": f"{tmp}/%(title)s.%(ext)s",
            "format": "mp4/best",
            "quiet": True,
            "noplaylist": True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            with open(file_path, "rb") as f:
                await update.message.reply_video(video=f)

        except Exception as e:
            await update.message.reply_text(f"صار خطأ: {e}")

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()
    app.add_handler(CallbackQueryHandler(continue_download, pattern="go"))

if __name__ == "__main__":
    main()
