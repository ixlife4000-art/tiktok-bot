import os
import tempfile
from yt_dlp import YoutubeDL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

pending_links = {}

def ad_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 زيارة الإعلان", url="https://t.me/tiktoknowatermarkbot")],
        [InlineKeyboardButton("✅ متابعة التحميل", callback_data="continue_download")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 أرسل رابط تيك توك")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    url = update.message.text.strip()

    pending_links[user_id] = url

    await update.message.reply_text(
        "📢 إعلان\n\nاضغط زيارة الإعلان ثم ارجع واضغط متابعة التحميل 🔥",
        reply_markup=ad_keyboard()
    )

async def continue_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    url = pending_links.get(user_id)
    if not url:
        await query.message.reply_text("أرسل الرابط مرة ثانية.")
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
           
