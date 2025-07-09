import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import openai

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# پیکربندی لاگ‌ها برای نمایش اطلاعات در کنسول
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- پیکربندی ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# بررسی وجود توکن‌ها
if not BOT_TOKEN:
    logger.error("BOT_TOKEN در متغیرهای محیطی یافت نشد. لطفاً آن را تنظیم کنید.")
    exit()
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY در متغیرهای محیطی یافت نشد. لطفاً آن را تنظیم کنید.")
    exit()

# تنظیم کلید API اوپن‌ای‌آی
openai.api_key = OPENAI_API_KEY

# --- توابع مدیریت دستورات و پیام‌ها ---

async def start_command(update: Update, context) -> None:
    """پاسخ به دستور /start یا 'استارت'."""
    user = update.effective_user
    await update.message.reply_html(
        rf"سلام {user.mention_html()}! من یک ربات هستم. فعلاً کاربر اصلی آنلاین نیست، ولی من می‌تونم به سوالات شما پاسخ بدم. لطفاً سوالتون رو بپرسید."
    )

async def handle_message(update: Update, context) -> None:
    """پاسخ به پیام‌های کاربر با استفاده از هوش مصنوعی."""
    user_message = update.message.text
    if not user_message: # اگر پیام متنی نبود، کاری انجام نده
        return

    logger.info(f"پیام دریافت شده از {update.effective_user.id}: {user_message}")

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo", # مدل هوش مصنوعی (می‌تونید gpt-4 رو هم امتحان کنید اگر دسترسی دارید)
            messages=[
                {"role": "system", "content": "شما یک دستیار مفید هستید. کاربر اصلی در حال حاضر در دسترس نیست، اما شما اینجا هستید تا به سوالات پاسخ دهید."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150, # حداکثر طول پاسخ هوش مصنوعی
            temperature=0.7, # خلاقیت هوش مصنوعی (0.0 تا 1.0)
        )
        ai_response = response.choices[0].message.content
        await update.message.reply_text(f"فعلا کاربر نیست ولی من می‌تونم به سوالاتتون پاسخ بدم:\n{ai_response}")
    except Exception as e:
        logger.error(f"خطا در تولید پاسخ هوش مصنوعی: {e}")
        await update.message.reply_text("متاسفم، در حال حاضر نمی‌تونم به سوال شما پاسخ بدم. لطفاً دوباره تلاش کنید.")

# --- تابع اصلی برای راه‌اندازی ربات ---

def main() -> None:
    """ربات را اجرا می‌کند."""
    # ساخت Application و ارسال توکن ربات
    application = Application.builder().token(BOT_TOKEN).build()

    # ثبت هندلرها (مدیران پیام‌ها)
    application.add_handler(CommandHandler("start", start_command)) # برای دستور /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) # برای پیام‌های متنی غیر از دستورات

    # اجرای ربات تا زمانی که کاربر Ctrl-C را فشار دهد
    logger.info("ربات راه‌اندازی شد! برای توقف Ctrl-C را فشار دهید.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
  
