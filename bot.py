import os
import asyncio
import yt_dlp
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# إعداد السجلات للمراقبة
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- بيانات البوت الخاصة بك ---
TOKEN = "8358331866:AAGTt_BDM7wCrc2yqXWzi-CTYAoA1n0LKww"
CHANNEL_ID = "@Younessrgh_bot" # يمكنك تغييره لمعرف قناتك إذا كنت تريد اشتراك إجباري
# ----------------------------

def download_media(url, mode):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    opts = {
        'format': 'bestaudio/best' if mode == "audio" else 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        fname = ydl.prepare_filename(info)
        
        if mode == "audio":
            base, _ = os.path.splitext(fname)
            new_name = base + ".mp3"
            if os.path.exists(new_name): os.remove(new_name)
            os.rename(fname, new_name)
            return new_name
        return fname

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"مرحباً بك في بوت التحميل الخاص بي!\nأرسل رابط الفيديو (YouTube, TikTok, Instagram) وسأقوم بتحميله لك.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url:
        await update.message.reply_text("من فضلك أرسل رابطاً صحيحاً.")
        return

    keyboard = [
        [InlineKeyboardButton("🎵 تحميل MP3", callback_data=f"audio|{url}"),
         InlineKeyboardButton("🎬 تحميل MP4", callback_data=f"video|{url}")]
    ]
    await update.message.reply_text("اختر الصيغة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mode, url = query.data.split("|")
    status = await query.edit_message_text("⏳ جاري المعالجة... انتظر قليلاً")

    file_path = None
    try:
        file_path = await asyncio.to_thread(download_media, url, mode)
        with open(file_path, 'rb') as f:
            if mode == "audio":
                await context.bot.send_audio(chat_id=query.message.chat_id, audio=f)
            else:
                await context.bot.send_video(chat_id=query.message.chat_id, video=f)
        await status.delete()
    except Exception as e:
        await query.message.reply_text(f"حدث خطأ: {str(e)}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("البوت يعمل الآن بنجاح!")
    app.run_polling()
    
