import logging
import os

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Здравствуйте')

def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)

def main():
    from dotenv import load_dotenv
    load_dotenv()

    # Обязательная переменная — если нет, сразу KeyError
    TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
