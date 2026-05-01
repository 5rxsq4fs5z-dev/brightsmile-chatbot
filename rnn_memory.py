import numpy as np
import pickle
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from collections import deque
import nltk

nltk.download('punkt_tab')
nltk.download('stopwords')

TOKEN = "8653613051:AAEVBnCv9B0mYDI4LNAGs6R"

with open('model.pkl', 'rb') as f:
    نموذج, مفردات = pickle.load(f)

# ذاكرة لكل مستخدم
ذاكرة_المستخدمين = {}

class ذاكرة_المحادثة:
    def __init__(self):
        self.ذاكرة = deque(maxlen=5)
        self.اسم_المريض = None
        self.آخر_موضوع = None

    def استخرج_الاسم(self, رسالة):
        كلمات = رسالة.split()
        for i, كلمة in enumerate(كلمات):
            if كلمة in ['اسمي', 'انا', 'أنا']:
                if i + 1 < len(كلمات):
                    self.اسم_المريض = كلمات[i + 1]
        return self.اسم_المريض

    def خصص_الرد(self, رد, نية):
        self.آخر_موضوع = نية
        if self.اسم_المريض:
            if نية == "حجز موعد":
                return f"بكل سرور {self.اسم_المريض}، وش اليوم المناسب لك؟"
            elif نية == "طوارئ":
                return f"نأسف {self.اسم_المريض}! اتصل بنا على 0501234567 فوراً."
            elif نية == "ترحيب":
                return f"هلا {self.اسم_المريض}! كيف أقدر أساعدك اليوم؟"
        return رد

def جملة_لأرقام(جملة, مفردات):
    متجه = np.zeros(len(مفردات))
    كلمات = جملة.split()
    for كلمة in كلمات:
        if كلمة in مفردات:
            متجه[مفردات[كلمة]] = 1
    return متجه

def فهم_النية(جملة):
    تحيات = ['السلام', 'عليكم', 'وعليكم', 'مرحبا', 'هلا', 'اهلا', 'صباح', 'مساء', 'هاي', 'هلو', 'اهلين', 'يهلا', 'حياك', 'ياهلا']
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
        "طوارئ": "نأسف لسماع ذلك. اتصل بنا مباشرة على 0501234567 لموعد عاجل.",
        "سؤال عن السعر": "أسعارنا:\nكشف: 150 ريال\nتنظيف: 200 ريال\nحشو: 300 ريال\nخلع: 250 ريال\nتبييض: 800 ريال\nتقويم: يحدد بعد الكشف\nابتسامة هوليود: يحدد بعد الكشف",
        "سؤال عن طبيب": "عندنا د. سارة و د. خالد متخصصين في طب الأسنان، وعندنا قسم خاص لأسنان الأطفال.",
        "سؤال عن الدوام": "دوامنا:\nالسبت - الأربعاء: 9 صباحاً - 9 مساءً\nالخميس: 9 صباحاً - 5 مساءً\nالجمعة: إجازة",
        "سؤال عن الموقع": "موقعنا: حي النزهة، شارع الأمير سلطان 📍\nللتواصل: 0501234567",
        "سؤال عن التواصل": "تواصلي معنا:\nجوال/واتساب: 0501234567\nانستقرام: @brightsmile_clinic\nسناب: @brightsmile_snap\nتيك توك: @brightsmile_tiktok\nيوتيوب: BrightSmile Clinic",
        "سؤال عن العروض": "عروضنا الحالية:\nكشف مجاني مع أي علاج\nخصم 20% على تبييض الأسنان\nقسط بدون فوائد على التقويم",
        "غير معروف": "عذراً، ما فهمت. أقدر أساعدك في:\nحجز موعد / إلغاء موعد\nمعلومات الأطباء / الأسعار\nأوقات الدوام / الموقع"
    }
    return ردود.get(نية, ردود["غير معروف"])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رسالة = update.message.text
    معرف_المستخدم = update.message.from_user.id

    if معرف_المستخدم not in ذاكرة_المستخدمين:
        ذاكرة_المستخدمين[معرف_المستخدم] = ذاكرة_المحادثة()

    ذاكرة = ذاكرة_المستخدمين[معرف_المستخدم]
    ذاكرة.استخرج_الاسم(رسالة)
    نية = فهم_النية(رسالة)
    رد = رد_البوت(نية)
    رد_مخصص = ذاكرة.خصص_الرد(رد, نية)
    ذاكرة.ذاكرة.append({'رسالة': رسالة, 'رد': رد_مخصص})

    await update.message.reply_text(رد_مخصص)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    معرف_المستخدم = update.message.from_user.id
    ذاكرة_المستخدمين[معرف_المستخدم] = ذاكرة_المحادثة()
    await update.message.reply_text("مرحبا في عيادة برايت سمايل 🦷\nكيف أقدر أساعدك اليوم؟")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("البوت شغال مع ذاكرة RNN! 🚀🧠")
    app.run_polling()

if __name__ == "__main__":
    main()