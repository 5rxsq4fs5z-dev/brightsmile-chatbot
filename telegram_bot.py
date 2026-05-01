import numpy as np
import pickle
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from collections import deque
import nltk
import re
import os
from cnn_image import حلل_الصورة

nltk.download('punkt_tab')
nltk.download('stopwords')

TOKEN = "8653613051:AAGStDXdd_6vL7Q1fKIdIPjy84A6MAbjEFU"

with open('model.pkl', 'rb') as f:
    نموذج, مفردات = pickle.load(f)

ذاكرة_المستخدمين = {}

class ذاكرة_المحادثة:
    def __init__(self):
        self.ذاكرة = deque(maxlen=10)
        self.اسم_المريض = None
        self.آخر_موضوع = None

    def استخرج_الاسم(self, رسالة):
        أنماط = [
            r'اسمي\s+(\w+)',
            r'أنا\s+(\w+)',
            r'انا\s+(\w+)',
            r'أسمي\s+(\w+)',
        ]
        for نمط in أنماط:
            نتيجة = re.search(نمط, رسالة)
            if نتيجة:
                self.اسم_المريض = نتيجة.group(1)
                return self.اسم_المريض
        return None

    def خصص_الرد(self, رد, نية):
        self.آخر_موضوع = نية
        if self.اسم_المريض:
            if نية == "حجز موعد":
                return f"بكل سرور {self.اسم_المريض}، وش اليوم المناسب لك؟"
            elif نية == "طوارئ":
                return f"نأسف {self.اسم_المريض}! اتصل بنا على 0501234567 فوراً."
            elif نية == "ترحيب":
                return f"هلا {self.اسم_المريض}! كيف أقدر أساعدك اليوم؟"
            elif نية == "إلغاء موعد":
                return f"حسناً {self.اسم_المريض}، سنلغي موعدك. ما رقم جوالك؟"
        return رد

def جملة_لأرقام(جملة, مفردات):
    متجه = np.zeros(len(مفردات))
    كلمات = جملة.split()
    for كلمة in كلمات:
        if كلمة in مفردات:
            متجه[مفردات[كلمة]] = 1
    return متجه

def هل_رقم_جوال(نص):
    نص_نظيف = re.sub(r'\s+', '', نص)
    return bool(re.match(r'^[0-9+]{9,13}$', نص_نظيف))

def فهم_النية(جملة):
    تحيات = ['السلام', 'عليكم', 'وعليكم', 'مرحبا', 'هلا', 'اهلا',
              'صباح', 'مساء', 'هاي', 'هلو', 'اهلين', 'يهلا', 'حياك']
    كلمات_جملة = جملة.split()
    if any(ك in تحيات for ك in كلمات_جملة):
        return "ترحيب"
    متجه = جملة_لأرقام(جملة, مفردات)
    تصنيف = نموذج.predict([متجه])[0]
    ثقة = نموذج.predict_proba([متجه]).max()
    if ثقة < 0.4:
        return "غير معروف"
    return تصنيف

def رد_البوت(نية):
    ردود = {
        "ترحيب": "هلا وسهلا! كيف أقدر أساعدك اليوم؟",
        "حجز موعد": "بكل سرور، وش اليوم المناسب لك؟",
        "إلغاء موعد": "حسناً، سنلغي موعدك. ما رقم جوالك؟",
        "طوارئ": "نأسف لسماع ذلك. اتصل بنا على 0501234567 فوراً.",
        "تأكيد_إلغاء": "تم إلغاء موعدك بنجاح ✅ نتمنى نشوفك قريب!",
        "تأكيد_حجز": "تم تسجيل رقمك ✅ سنتواصل معك لتأكيد الموعد!",
        "سؤال عن السعر": "أسعارنا:\nكشف: 150 ريال\nتنظيف: 200 ريال\nحشو: 300 ريال\nخلع: 250 ريال\nتبييض: 800 ريال\nتقويم: يحدد بعد الكشف\nابتسامة هوليود: يحدد بعد الكشف",
        "سؤال عن طبيب": "عندنا د. سارة و د. خالد متخصصين في طب الأسنان\nوعندنا قسم خاص لأسنان الأطفال.",
        "سؤال عن الدوام": "دوامنا:\nالسبت - الأربعاء: 9 صباحاً - 9 مساءً\nالخميس: 9 صباحاً - 5 مساءً\nالجمعة: إجازة",
        "سؤال عن الموقع": "موقعنا: حي النزهة، شارع الأمير سلطان\nللتواصل: 0501234567",
        "سؤال عن التواصل": "تواصلي معنا:\nجوال/واتساب: 0501234567\nانستقرام: @brightsmile_clinic\nسناب: @brightsmile_snap\nتيك توك: @brightsmile_tiktok\nيوتيوب: BrightSmile Clinic",
        "سؤال عن العروض": "عروضنا الحالية:\nكشف مجاني مع أي علاج\nخصم 20% على تبييض الأسنان\nقسط بدون فوائد على التقويم",
        "غير معروف": "عذراً، ما فهمت.\nأقدر أساعدك في:\nحجز موعد / إلغاء موعد\nمعلومات الأطباء / الأسعار\nأوقات الدوام / الموقع"
    }
    return ردود.get(نية, ردود["غير معروف"])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رسالة = update.message.text
    معرف = update.message.from_user.id

    if معرف not in ذاكرة_المستخدمين:
        ذاكرة_المستخدمين[معرف] = ذاكرة_المحادثة()

    ذاكرة = ذاكرة_المستخدمين[معرف]
    ذاكرة.استخرج_الاسم(رسالة)

    if هل_رقم_جوال(رسالة):
        if ذاكرة.آخر_موضوع == "إلغاء موعد":
            نية = "تأكيد_إلغاء"
        else:
            نية = "تأكيد_حجز"
    else:
        نية = فهم_النية(رسالة)

    رد = رد_البوت(نية)
    رد_مخصص = ذاكرة.خصص_الرد(رد, نية)
    ذاكرة.ذاكرة.append({'رسالة': رسالة, 'نية': نية, 'رد': رد_مخصص})
    await update.message.reply_text(رد_مخصص)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    معرف = update.message.from_user.id
    if معرف not in ذاكرة_المستخدمين:
        ذاكرة_المستخدمين[معرف] = ذاكرة_المحادثة()
    ذاكرة = ذاكرة_المستخدمين[معرف]
    await update.message.reply_text("جاري تحليل الصورة... ⏳")
    صورة = await update.message.photo[-1].get_file()
    await صورة.download_to_drive('temp_image.jpg')
    نتيجة = حلل_الصورة('temp_image.jpg')
    if ذاكرة.اسم_المريض:
        await update.message.reply_text(f"{ذاكرة.اسم_المريض}، {نتيجة}")
    else:
        await update.message.reply_text(نتيجة)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    معرف = update.message.from_user.id
    ذاكرة_المستخدمين[معرف] = ذاكرة_المحادثة()
    await update.message.reply_text(
        "مرحبا في عيادة برايت سمايل\n"
        "كيف أقدر أساعدك اليوم؟\n\n"
        "يمكنك سؤالي عن:\n"
        "حجز موعد\n"
        "الأسعار\n"
        "الأطباء\n"
        "الدوام\n"
        "الموقع\n"
        "أو أرسل صورة أسنانك للتحليل"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("البوت شغال! NLP + ANN + RNN + CNN")
    app.run_polling()

if __name__ == "__main__":
    main()