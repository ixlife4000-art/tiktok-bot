import os
import time
import tempfile
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Store each user's link
pending_links = {}

# Store first time user received ad screen
user_time = {}

def get_text(lang, key):
    texts = {
        "ar": {
            "start": "📥 ارسل رابط تيك توك",
            "ad_message": "📢 لازم تشوف الإعلان قبل التحميل:\n\n1- اضغط مشاهدة الإعلان\n2- أكمل الخطوات في الصفحة\n3- ارجع واضغط متابعة التحميل",
            "watch_ad": "📢 مشاهدة الإعلان",
            "continue": "✅ متابعة التحميل",
            "send_again": "❌ ارسل الرابط من جديد",
            "downloading": "⏳ جاري التحميل...",
            "error": "❌ صار خطأ",
            "wait": "⏳ لازم تشوف الإعلان أول ثم انتظر شوي قبل التحميل"
        },
        "en": {
            "start": "📥 Send a TikTok link",
            "ad_message": "📢 You must watch the ad before downloading:\n\n1- Tap Watch Ad\n2- Complete the steps on the page\n3- Come back and press Continue Download",
            "watch_ad": "📢 Watch Ad",
            "continue": "✅ Continue Download",
            "send_again": "❌ Send the link again",
            "downloading": "⏳ Downloading...",
            "error": "❌ Error occurred",
            "wait": "⏳ Please watch the ad first and wait a few seconds before downloading"
        }
    }

    if lang and lang.startswith("ar"):
        return texts["ar"][key]
    return texts["en"][key]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code or "en"
    await update.message.reply_text(get_text(lang, "start"))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    lang = update.effective_user.language_code or "en"

    pending_links[user_id] = update.message.text.strip()
    user_time[user_id] = time.time()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(lang, "watch_ad"), url="https://shrinkme.click/o5Jbre8")],
        [InlineKeyboardButton(get_text(lang, "continue"), callback_data="go")]
    ])

    await update.message.reply_text(
        get_text(lang, "ad_message"),
        reply_markup=keyboard
    )

async def continue_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = query.from_user.language_code or "en"

    await query.answer()

    # Prevent instant skip
    if time.time() - user_time.get(user_id, 0) < 8:
        await query.message.reply_text(get_text(lang, "wait"))
        return

    url = pending_links.get(user_id)
    if not url:
        await query.message.reply_text(get_text(lang, "send_again"))
        return

    await query.message.reply_text(get_text(lang, "downloading"))

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
            await query.message.reply_text(get_text(lang, "error"))

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.add_handler(CallbackQueryHandler(continue_download, pattern="go"))

    app.run_polling()

if __name__ == "__main__":
    main()
