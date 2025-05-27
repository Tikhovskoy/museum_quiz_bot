import logging
import os
import random
import json

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from redis_tools import save_user_question, get_user_question

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
    user_id = update.effective_user.id

    if user_message == "Новый вопрос":
        question = random.choice(list(questions_dict.keys()))
        save_user_question(user_id, question)
        update.message.reply_text(question)
    elif user_message == "Сдаться":
        current_question = get_user_question(user_id)
        if current_question and current_question in questions_dict:
            answer = questions_dict[current_question]
            update.message.reply_text(f"Правильный ответ:\n{answer}")
        else:
            update.message.reply_text("Вы ещё не взяли ни одного вопроса.")
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
