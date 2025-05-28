import argparse
import os
import re


def parse_questions(filepath):
    with open(filepath, encoding="koi8-r") as file:
        content = file.read()

    question_pattern = re.compile(
        r"Вопрос\s*(\d+):\n(.*?)\nОтвет:\n(.*?)\n(?:Комментарий:\n(.*?))?(?:\nИсточник:\n(.*?))?(?:\nАвтор:\n(.*?))?\n",
        re.DOTALL,
    )

    questions = []
    for match in question_pattern.finditer(content):
        number = int(match.group(1))
        question = match.group(2).strip()
        answer = match.group(3).strip()
        comment = match.group(4).strip() if match.group(4) else ""
        source = match.group(5).strip() if match.group(5) else ""
        author = match.group(6).strip() if match.group(6) else ""

        questions.append(
            {
                "number": number,
                "question": question,
                "answer": answer,
                "comment": comment,
                "source": source,
                "author": author,
            }
        )

    return questions


def main():
    parser = argparse.ArgumentParser(
        description="Парсинг текстовых файлов с вопросами для викторины"
    )
    parser.add_argument(
        "--file",
        default=os.path.join(os.path.dirname(__file__), "data", "120br.txt"),
        help="Путь к текстовому файлу с вопросами",
    )
    args = parser.parse_args()

    filepath = args.file

    if not os.path.isfile(filepath):
        print(f"Файл {filepath} не найден.")
        return

    questions = parse_questions(filepath)

    for q in questions[:3]:
        print(f"Вопрос {q['number']}: {q['question']}")
        print(f"Ответ: {q['answer']}")
        print(f"Комментарий: {q['comment']}")
        print(f"Источник: {q['source']}")
        print(f"Автор: {q['author']}\n{'-'*40}")

    print(f"Всего вопросов: {len(questions)}")


if __name__ == "__main__":
    main()
