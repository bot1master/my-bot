import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,MessageHandler,filters,ContextTypes
from deep_translator import GoogleTranslator
TOKEN = os.getenv("TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
async def start(update: Update, context):
    await update.message.reply_text("مرحباً! أنابوت تجريبي!")
async def handle_message(update: Update,context):
    text = update.message.text
    if text.startswith("ترجم"):
        try:
            msg = text.replace("ترجم", "").strip()
            translated = GoogleTranslator(source='auto', target='en').translate(msg)
            await update.message.reply_text(translated)
        except:
            await update.message.reply_text("خطأ في الترجمة")
    elif "http" in text:
        try:
            import yt_dlp
            import os
            url = text.strip()
            for f in os.listdir():
                if f.startswith("video"):
                    os.remove(f)
            ydl_opts = {'format': 'best', 'outtmpl': 'video.%(ext)s', 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            file = None
            for f in os.listdir():
                if f.startswith("video"):
                    file = f
                    break
            if file:
                with open(file, "rb") as v:
                    await update.message.reply_video(v)
            else:
                await update.message.reply_text("فشل تحميل الفيديو")
        except Exception as e:
            await update.message.reply_text("الرابط غير صالح او الانترنت ضعيف")
    else:
        await ai_reply(update, text)
async def voice_to_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        import speech_recognition as sr
        file = await update.message.voice.get_file()
        await file.download_to_drive("voice.ogg")
        r = sr.Recognizer()
        with sr.AudioFile("voice.ogg") as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language="ar")
        await update.message.reply_text("📝 النص:\n" + text)
    except Exception as e:
        await update.message.reply_text("خطأ في تحويل الصوت")
async def news(update, context):
    try:
        import feedparser
        url = "http://feeds.reuters.com/reuters/worldNews"
        feed = feedparser.parse(url)
        articles = feed.entries[:5]
        if not articles:
            await update.message.reply_text("لا توجد اخبار الان")
            return
        msg = ""
        for art in articles:
            title = art.title
            translated = GoogleTranslator(source='auto', target='ar').translate(title)
            msg += translated + "\n\n"
        await update.message.reply_text(msg)
    except:
        await update.message.reply_text("خطأ في الاخبار")
async def ai_reply(update, text):
    try:
        url = "https://router.huggingface.co/hf-inference/models/facebook/blenderbot-400M-distill"
        headers = {"Authorization": f"Bearer{HF_API_KEY}", "Content-Type": "application/json"}
        payload = {"inputs": text}
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        print (data)
        if isinstance(data, list) and len(data) > 0:
            reply = data[0].get("generated_text", "مافي رد")
        elif isinstance(data, dict) and "error" in data:
            reply = "❌ خطأ من السيرفر: " + data["error"]
        else:
            reply = "⚠️ الذكاء لم يرجع رد مفهوم"
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(str(e))
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start",start))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(MessageHandler(filters.TEXT,
    handle_message))
    application.run_polling(timeout=30)
if __name__ == "__main__":
    main()
