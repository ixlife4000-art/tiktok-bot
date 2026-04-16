import os
import tempfile
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

pending_links = {}
ad_clicked = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send TikTok link")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    pending_links[user_id] = update.message.text.strip()
    ad_clicked[user_id] = False

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Watch Ad", callback_data="ad")],
        [InlineKeyboardButton("✅ Continue Download", callback_data="go")]
    ])

    await update.message.reply_text("Watch the ad first", reply_markup=keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    if query.data == "ad":
        ad_clicked[user_id] = True

        # يفتح الرابط بعد الضغط
        await query.message.reply_text("Open this link and complete it:\nhttps://shrinkme.click/o5Jbre8")

    elif query.data == "go":
        if not ad_clicked.get(user_id, False):
            await query.message.reply_text("❌ You must watch the ad first")
            return

        url = pending_links.get(user_id)
        if not url:
            await query.message.reply_text("Send link again")
            return

        await query.message.reply_text("Downloading...")

        with tempfile.TemporaryDirectory() as tmp:
            ydl_opts = {
                "outtmpl": f"{tmp}/%(title)s.%(ext)s",
                "format": "mp4/best",
            }

            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info)

                with open(file_path, "rb") as f:
                    await query.message.reply_video(video=f)

            except:
                await query.message.reply_text("Error")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
