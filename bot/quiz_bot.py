import json
import logging
import os
import random
import re
from enum import Enum, auto

from dotenv import load_dotenv
from redis_tools import (get_redis_client, get_user_question, get_user_score,
                         increase_user_score, save_user_question)
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

PLATFORM = "telegram"


class States(Enum):
    QUESTION = auto()
    ANSWER = auto()


def load_questions(questions_path):
    with open(questions_path, encoding="utf-8") as f:
        return json.load(f)


def start(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("Новый вопрос"), KeyboardButton("Сдаться")],
        [KeyboardButton("Мой счёт")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Привет! Я бот для викторин!", reply_markup=reply_markup)
    return States.QUESTION


def handle_new_question_request(update: Update, context: CallbackContext):
    questions = context.bot_data["questions"]
    redis_client = context.bot_data["redis_client"]
    question = random.choice(list(questions.keys()))
    user_id = update.effective_user.id
    save_user_question(redis_client, user_id, question, PLATFORM)
    update.message.reply_text(question)
    return States.ANSWER


def clean_answer(answer):
    answer = answer.split(".", 1)[0]
    answer = re.split(r"[\(\[]", answer)[0]
    answer = answer.strip().lower()
    return answer


def handle_solution_attempt(update: Update, context: CallbackContext):
    questions = context.bot_data["questions"]
    redis_client = context.bot_data["redis_client"]
    user_id = update.effective_user.id
    user_answer = update.message.text.strip().lower()
    current_question = get_user_question(redis_client, user_id, PLATFORM)
    if not current_question or current_question not in questions:
        update.message.reply_text(
            "Пожалуйста, сначала возьмите вопрос — нажмите «Новый вопрос»."
        )
        return States.QUESTION

    correct_answer = questions[current_question]
    main_correct_answer = clean_answer(correct_answer)

    if user_answer == main_correct_answer:
        increase_user_score(redis_client, user_id, PLATFORM)
        update.message.reply_text(
            "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        )
        return States.QUESTION
    else:
        update.message.reply_text("Неправильно… Попробуешь ещё раз?")
        return States.ANSWER


def handle_give_up(update: Update, context: CallbackContext):
    questions = context.bot_data["questions"]
    redis_client = context.bot_data["redis_client"]
    user_id = update.effective_user.id
    current_question = get_user_question(redis_client, user_id, PLATFORM)
    if current_question and current_question in questions:
        answer = questions[current_question]
        update.message.reply_text(f"Правильный ответ:\n{answer}")
    else:
        update.message.reply_text("Вы ещё не взяли ни одного вопроса.")
    question = random.choice(list(questions.keys()))
    save_user_question(redis_client, user_id, question, PLATFORM)
    update.message.reply_text(question)
    return States.ANSWER


def handle_score(update: Update, context: CallbackContext):
    redis_client = context.bot_data["redis_client"]
    user_id = update.effective_user.id
    score = get_user_score(redis_client, user_id, PLATFORM)
    update.message.reply_text(f"Ваш счёт: {score}")
    return States.QUESTION


def fallback(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Пожалуйста, пользуйтесь кнопками или отвечайте на вопрос!"
    )
    return States.QUESTION


def main():
    load_dotenv()
    telegram_token = os.environ["TELEGRAM_TOKEN"]
    questions_path = os.environ.get(
        "QUESTIONS_PATH",
        os.path.join(os.path.dirname(__file__), "..", "data", "120br_dict.json"),
    )
    redis_host = os.environ["REDIS_HOST"]
    redis_port = int(os.environ["REDIS_PORT"])
    redis_password = os.environ["REDIS_PASSWORD"]

    questions = load_questions(questions_path)
    redis_client = get_redis_client(redis_host, redis_port, redis_password)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher

    dp.bot_data["questions"] = questions
    dp.bot_data["redis_client"] = redis_client

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            States.QUESTION: [
                MessageHandler(
                    Filters.regex("^Новый вопрос$"), handle_new_question_request
                ),
                MessageHandler(Filters.regex("^Сдаться$"), handle_give_up),
                MessageHandler(Filters.regex("^Мой счёт$"), handle_score),
            ],
            States.ANSWER: [
                MessageHandler(Filters.regex("^Сдаться$"), handle_give_up),
                MessageHandler(Filters.regex("^Мой счёт$"), handle_score),
                MessageHandler(
                    Filters.text & ~Filters.command, handle_solution_attempt
                ),
            ],
        },
        fallbacks=[MessageHandler(Filters.all, fallback)],
        allow_reentry=True,
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
