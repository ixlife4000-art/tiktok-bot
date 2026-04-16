import os
import time
import tempfile
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

pending_links = {}
ad_clicked = {}
ad_time = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a TikTok link")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    pending_links[user_id] = update.message.text.strip()
    ad_clicked[user_id] = False
    ad_time[user_id] = 0

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Watch Ad", callback_data="ad")],
        [InlineKeyboardButton("✅ Continue Download", callback_data="go")]
    ])

    await update.message.reply_text(
        "Before downloading:\n\n"
        "1. Tap Watch Ad\n"
        "2. Solve the captcha\n"
        "3. Click Continue on the ad page\n"
        "4. Come back here\n"
        "5. Tap Continue Download",
        reply_markup=keyboard
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "ad":
        ad_clicked[user_id] = True
        ad_time[user_id] = time.time()

        await query.message.reply_text(
            "Open this ad link and complete the steps:\n"
            "https://shrinkme.click/o5Jbre8\n\n"
            "After that, come back and tap Continue Download."
        )
        return

    if query.data == "go":
        if not ad_clicked.get(user_id, False):
            await query.message.reply_text("❌ You must tap Watch Ad first.")
            return

        if time.time() - ad_time.get(user_id, 0) < 10:
            await query.message.reply_text("⏳ Please complete the ad first, then try again in a few seconds.")
            return

        url = pending_links.get(user_id)
        if not url:
            await query.message.reply_text("❌ Send the TikTok link again.")
            return

        await query.message.reply_text("⏳ Downloading...")

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
                await query.message.reply_text("❌ An error occurred while downloading.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
