import logging
import os
import random
import json

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', '120br_dict.json')

def load_questions():
    with open(QUESTIONS_PATH, encoding='utf-8') as f:
        return json.load(f)

questions_dict = None

def start(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton('Новый вопрос'), KeyboardButton('Сдаться')],
        [KeyboardButton('Мой счёт')]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False
    )
    update.message.reply_text(
        'Привет! Я бот для викторин!',
        reply_markup=reply_markup
    )

def handle_message(update: Update, context: CallbackContext):
    global questions_dict
    user_message = update.message.text

    if user_message == "Новый вопрос":
        question = random.choice(list(questions_dict.keys()))
        context.user_data['current_question'] = question
        update.message.reply_text(question)
    elif user_message == "Сдаться":
        update.message.reply_text('Пока сдача не реализована')
    elif user_message == "Мой счёт":
        update.message.reply_text('Пока счёт не реализован')
    else:
        update.message.reply_text(
            "Пожалуйста, пользуйтесь кнопками: «Новый вопрос», «Сдаться» или «Мой счёт»."
        )

def main():
    from dotenv import load_dotenv
    load_dotenv()

    TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

    global questions_dict
    questions_dict = load_questions()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
