from redis_tools import save_user_question, get_user_question

user_id = 12345
question = "В каком году состоялась битва при Куликове?"

save_user_question(user_id, question)
retrieved_question = get_user_question(user_id)
print(f"Сохранённый вопрос для пользователя {user_id}: {retrieved_question}")
