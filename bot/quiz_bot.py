import logging
import os
import random
import json
import re

from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from enum import Enum, auto

from redis_tools import save_user_question, get_user_question

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', '120br_dict.json')

class States(Enum):
    QUESTION = auto()
    ANSWER = auto()

def load_questions():
    with open(QUESTIONS_PATH, encoding='utf-8') as f:
        return json.load(f)

questions_dict = None

def start(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton('Новый вопрос'), KeyboardButton('Сдаться')],
        [KeyboardButton('Мой счёт')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        'Привет! Я бот для викторин!',
        reply_markup=reply_markup
    )
    return States.QUESTION

def handle_new_question_request(update: Update, context: CallbackContext):
    global questions_dict
    question = random.choice(list(questions_dict.keys()))
    user_id = update.effective_user.id
    save_user_question(user_id, question)
    update.message.reply_text(question)
    return States.ANSWER

def clean_answer(answer):
    answer = answer.split('.', 1)[0]
    answer = re.split(r'[\(\[]', answer)[0]
    answer = answer.strip().lower()
    return answer

def handle_solution_attempt(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_answer = update.message.text.strip().lower()
    current_question = get_user_question(user_id)
    if not current_question or current_question not in questions_dict:
        update.message.reply_text("Пожалуйста, сначала возьмите вопрос — нажмите «Новый вопрос».")
        return States.QUESTION

    correct_answer = questions_dict[current_question]
    main_correct_answer = clean_answer(correct_answer)

    if user_answer == main_correct_answer:
        update.message.reply_text(
            "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        )
        return States.QUESTION
    else:
        update.message.reply_text(
            "Неправильно… Попробуешь ещё раз?"
        )
        return States.ANSWER

def handle_give_up(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    current_question = get_user_question(user_id)
    if current_question and current_question in questions_dict:
        answer = questions_dict[current_question]
        update.message.reply_text(f"Правильный ответ:\n{answer}")
    else:
        update.message.reply_text("Вы ещё не взяли ни одного вопроса.")
    question = random.choice(list(questions_dict.keys()))
    save_user_question(user_id, question)
    update.message.reply_text(question)
    return States.ANSWER

def handle_score(update: Update, context: CallbackContext):
    update.message.reply_text('Пока счёт не реализован')
    return States.QUESTION

def fallback(update: Update, context: CallbackContext):
    update.message.reply_text('Пожалуйста, пользуйтесь кнопками или отвечайте на вопрос!')
    return States.QUESTION

def main():
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

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            States.QUESTION: [
                MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request),
                MessageHandler(Filters.regex('^Сдаться$'), handle_give_up),
                MessageHandler(Filters.regex('^Мой счёт$'), handle_score),
            ],
            States.ANSWER: [
                MessageHandler(Filters.regex('^Сдаться$'), handle_give_up),
                MessageHandler(Filters.regex('^Мой счёт$'), handle_score),
                MessageHandler(Filters.text & ~Filters.command, handle_solution_attempt),
            ],
        },
        fallbacks=[MessageHandler(Filters.all, fallback)],
        allow_reentry=True,
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
