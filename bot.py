import os
import tempfile
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

# حفظ الروابط لكل مستخدم
pending_links = {}

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 ارسل رابط تيك توك")

# استقبال الرابط + عرض الإعلان
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    pending_links[user_id] = update.message.text.strip()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 مشاهدة الإعلان", url="https://shrinkme.click/o5Jbre8")],
        [InlineKeyboardButton("✅ متابعة التحميل", callback_data="go")]
    ])
await update.message.reply_text(
"📢 لازم تكمل الإعلان 👇\n\n"
"1- حل الكابتشا\n"
"2- اضغط Continue\n"
"3- ارجع واضغط متابعة التحميل",
reply_markup=keyboard
)
    
# بعد الضغط على متابعة
async def continue_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    url = pending_links.get(user_id)
    if not url:
        await query.message.reply_text("❌ ارسل الرابط من جديد")
        return

    await query.message.reply_text("⏳ جاري التحميل...")

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
            await query.message.reply_text("❌ صار خطأ")

# تشغيل البوت
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.add_handler(CallbackQueryHandler(continue_download, pattern="go"))

    app.run_polling()

if __name__ == "__main__":
    main()
