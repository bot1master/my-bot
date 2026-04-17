import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from groq import Groq

# 🔑 مفاتيحك
TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# 🧠 ذاكرة المستخدمين (Multi-user memory)
memory = {}  # user_id -> messages list

# 📦 إعداد الذاكرة
MAX_MEMORY = 10  # عدد الرسائل المحفوظة لكل مستخدم


# ===================== 🧠 AI FUNCTION =====================
def ask_ai(user_id, message):
    if user_id not in memory:
        memory[user_id] = []

    # إضافة رسالة المستخدم
    memory[user_id].append({"role": "user", "content": message})

    # تقليل الذاكرة إذا زادت
    if len(memory[user_id]) > MAX_MEMORY:
        memory[user_id] = memory[user_id][-MAX_MEMORY:]

    # إرسال إلى Groq
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "أنت مساعد ذكي احترافي، مختصر ودقيق."},
            *memory[user_id]
        ]
    )

    reply = response.choices[0].message.content

    # حفظ رد الذكاء
    memory[user_id].append({"role": "assistant", "content": reply})

    return reply


# ===================== 💬 MESSAGE HANDLER =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        reply = ask_ai(user_id, text)
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ: {str(e)}")


# ===================== 📌 COMMANDS =====================

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 أهلاً! أنا بوت ذكاء اصطناعي متطور.\n\n"
        "💡 اكتب أي شيء وسأرد عليك\n"
        "📌 أوامر:\n"
        "/reset - مسح الذاكرة\n"
        "/info - معلومات البوت"
    )


# /reset (مسح ذاكرة المستخدم)
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    memory[user_id] = []
    await update.message.reply_text("♻️ تم مسح الذاكرة بنجاح!")


# /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 بوت احترافي باستخدام Groq\n"
        "🧠 ذاكرة لكل مستخدم\n"
        "⚡ سرعة عالية\n"
        "👥 يدعم عدة مستخدمين"
    )


# ===================== 🚀 تشغيل البوت =====================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(CommandHandler("info", info))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print ("🤖 Bot is running...")
if __name__ == "__main__":
    app.run_polling()
