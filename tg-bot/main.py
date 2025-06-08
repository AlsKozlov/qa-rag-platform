from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
from dotenv import load_dotenv
import aiohttp
import os

load_dotenv()

API_URL = os.getenv("API_URL")
DESCRIPTION = os.getenv("DESCRIPTION")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {'Content-type': 'application/json'}
    msg = {
        'question': update.message.text,
        'conversation_id': update.message.chat.id
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=headers, json=msg) as response:
            response_json = await response.json()

    await update.message.reply_text(response_json.get('answer', "Извините, я не могу ответить на это."))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(DESCRIPTION)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(DESCRIPTION)

def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN is not set in .env")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_answer))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
