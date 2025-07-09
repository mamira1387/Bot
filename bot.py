import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import google.generativeai as genai # کتابخانه جدید برای جمینی

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# پیکربندی لاگ‌ها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # تغییر نام به GEMINI_API_KEY

if not BOT_TOKEN:
    logger.error("BOT_TOKEN در متغیرهای محیطی یافت نشد. لطفاً آن را تنظیم کنید.")
    exit()
if not GEMINI_API_KEY: # بررسی GEMINI_API_KEY
    logger.error("GEMINI_API_KEY در متغیرهای محیطی یافت نشد. لطفاً آن را تنظیم کنید.")
    exit()

# پیکربندی جمینی با کلید API
genai.configure(api_key=GEMINI_API_KEY)

# انتخاب مدل جمینی (می‌توانید مدل‌های دیگر را نیز امتحان کنید)
# برای دیدن مدل‌های موجود: print([m.name for m in genai.list_models()])
model = genai.GenerativeModel('gemini-pro')

# --- Bot Commands and Message Handlers ---

async def start_command(update: Update, context) -> None:
    """پاسخ به دستور /start یا 'استارت'."""
    user = update.effective_user
    await update.message.reply_html(
        rf"سلام {user.mention_html()}! من یک ربات هستم. فعلاً کاربر اصلی آنلاین نیست، ولی من می‌تونم به سوالات شما پاسخ بدم. لطفاً سوالتون رو بپرسید."
    )

async def handle_message(update: Update, context) -> None:
    """پاسخ به پیام‌های کاربر با استفاده از هوش مصنوعی."""
    user_message = update.message.text
    if not user_message:
        return

    logger.info(f"پیام دریافت شده از {update.effective_user.id}: {user_message}")

    try:
        # ساخت یک چت برای حفظ مکالمه (اختیاری، اما مفید برای مکالمات پیچیده‌تر)
        chat = model.start_chat(history=[])
        
        # ارسال پیام کاربر به مدل جمینی
        response = chat.send_message(user_message)
        ai_response = response.text # پاسخ از جمینی

        await update.message.reply_text(f"فعلا کاربر نیست ولی من می‌تونم به سوالاتتون پاسخ بدم:\n{ai_response}")
    except Exception as e:
        logger.error(f"خطا در تولید پاسخ هوش مصنوعی: {e}")
        await update.message.reply_text("متاسفم، در حال حاضر نمی‌تونم به سوال شما پاسخ بدم. لطفاً دوباره تلاش کنید.")

# --- Main function to run the bot ---

def main() -> None:
    """ربات را اجرا می‌کند."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("ربات راه‌اندازی شد! برای توقف Ctrl-C را فشار دهید.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
    
