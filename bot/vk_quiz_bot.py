import json
import logging
import os
import random
import re

import vk_api
from dotenv import load_dotenv
from redis_tools import (get_redis_client, get_user_question, get_user_score,
                         increase_user_score, save_user_question)
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

PLATFORM = "vk"


def load_questions(questions_path):
    with open(questions_path, encoding="utf-8") as f:
        return json.load(f)


def build_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Новый вопрос", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Сдаться", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("Мой счёт", color=VkKeyboardColor.SECONDARY)
    return keyboard


def clean_answer(answer):
    answer = answer.split(".", 1)[0]
    answer = re.split(r"[\(\[]", answer)[0]
    answer = answer.strip().lower()
    return answer


def main():
    load_dotenv()
    vk_token = os.environ["VK_GROUP_TOKEN"]
    vk_group_id = int(os.environ["VK_GROUP_ID"])
    questions_path = os.environ.get(
        "QUESTIONS_PATH",
        os.path.join(os.path.dirname(__file__), "..", "data", "120br_dict.json"),
    )
    redis_host = os.environ["REDIS_HOST"]
    redis_port = int(os.environ["REDIS_PORT"])
    redis_password = os.environ["REDIS_PASSWORD"]

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("vk_quiz_bot")

    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, vk_group_id)
    keyboard = build_keyboard()

    questions = load_questions(questions_path)
    redis_client = get_redis_client(redis_host, redis_port, redis_password)
    logger.info("VK Quiz Bot started!")
    print("Longpoll started, waiting for events...")

    for event in longpoll.listen():
        print("Catch event:", event)
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
            user_id = event.message.from_id
            text = event.message.text.strip()

            if text == "Новый вопрос":
                question = random.choice(list(questions.keys()))
                save_user_question(redis_client, user_id, question, PLATFORM)
                vk.messages.send(
                    user_id=user_id,
                    random_id=vk_api.utils.get_random_id(),
                    message=question,
                    keyboard=keyboard.get_keyboard(),
                )
                print(f"Задан новый вопрос пользователю {user_id}")
            elif text == "Сдаться":
                current_question = get_user_question(redis_client, user_id, PLATFORM)
                if current_question and current_question in questions:
                    answer = questions[current_question]
                    vk.messages.send(
                        user_id=user_id,
                        random_id=vk_api.utils.get_random_id(),
                        message=f"Правильный ответ:\n{answer}",
                        keyboard=keyboard.get_keyboard(),
                    )
                else:
                    vk.messages.send(
                        user_id=user_id,
                        random_id=vk_api.utils.get_random_id(),
                        message="Вы ещё не взяли ни одного вопроса.",
                        keyboard=keyboard.get_keyboard(),
                    )
                question = random.choice(list(questions.keys()))
                save_user_question(redis_client, user_id, question, PLATFORM)
                vk.messages.send(
                    user_id=user_id,
                    random_id=vk_api.utils.get_random_id(),
                    message=question,
                    keyboard=keyboard.get_keyboard(),
                )
                print(f"Пользователь {user_id} сдался, задан новый вопрос")
            elif text == "Мой счёт":
                score = get_user_score(redis_client, user_id, PLATFORM)
                vk.messages.send(
                    user_id=user_id,
                    random_id=vk_api.utils.get_random_id(),
                    message=f"Ваш счёт: {score}",
                    keyboard=keyboard.get_keyboard(),
                )
            else:
                current_question = get_user_question(redis_client, user_id, PLATFORM)
                if not current_question or current_question not in questions:
                    vk.messages.send(
                        user_id=user_id,
                        random_id=vk_api.utils.get_random_id(),
                        message="Пожалуйста, сначала возьмите вопрос — нажмите «Новый вопрос».",
                        keyboard=keyboard.get_keyboard(),
                    )
                else:
                    user_answer = text.lower()
                    correct_answer = questions[current_question]
                    main_correct_answer = clean_answer(correct_answer)
                    if user_answer == main_correct_answer:
                        increase_user_score(redis_client, user_id, PLATFORM)
                        vk.messages.send(
                            user_id=user_id,
                            random_id=vk_api.utils.get_random_id(),
                            message="Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»",
                            keyboard=keyboard.get_keyboard(),
                        )
                    else:
                        vk.messages.send(
                            user_id=user_id,
                            random_id=vk_api.utils.get_random_id(),
                            message="Неправильно… Попробуешь ещё раз?",
                            keyboard=keyboard.get_keyboard(),
                        )


if __name__ == "__main__":
    main()
