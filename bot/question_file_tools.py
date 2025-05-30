def load_questions(questions_path):
    questions = {}
    with open(questions_path, encoding="utf-8") as file:
        question = None
        for line in file:
            line = line.strip()
            if line.startswith("Вопрос"):
                question = line.split(":", 1)[1].strip()
            elif line.startswith("Ответ") and question:
                answer = line.split(":", 1)[1].strip()
                questions[question] = answer
                question = None
    return questions
