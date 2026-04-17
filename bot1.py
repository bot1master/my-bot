import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator

TOKEN = os.getenv("TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ✅ أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 البوت جاهز!\n\nاكتب:\nترجم ...\nذكاء ...")

# ✅ الذكاء الاصطناعي
async def ai_reply(update, text):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": text}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        res = response.json()

        reply = res["choices"][0]["message"]["content"]

        await update.message.reply_text(reply)

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ خطأ في الذكاء")

# ✅ معالجة الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ترجمة
    if text.startswith("ترجم"):
        msg = text.replace("ترجم", "").strip()
        translated = GoogleTranslator(source='auto', target='en').translate(msg)
        await update.message.reply_text(translated)

    # ذكاء
    elif text.startswith("ذكاء"):
        msg = text.replace("ذكاء", "").strip()
        await ai_reply(update, msg)

    else:
        await update.message.reply_text("❗ استخدم:\nترجم ...\nذكاء ...")

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print ("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
