import argparse
import json
import os


def build_questions(filepath):
    with open(filepath, encoding="koi8-r") as file:
        lines = file.readlines()

    questions = {}
    question_text = ""
    answer_text = ""
    mode = None

    for line in lines:
        line = line.rstrip("\r\n")
        if line.startswith("Вопрос"):
            mode = "question"
            question_text = ""
            answer_text = ""
            continue
        elif line.startswith("Ответ:"):
            mode = "answer"
            continue
        elif (
            line.startswith("Вопрос")
            or line.startswith("Комментарий:")
            or line.startswith("Источник:")
            or line.startswith("Автор:")
        ):
            mode = None
            continue

        if mode == "question":
            if question_text:
                question_text += "\n"
            question_text += line
        elif mode == "answer":
            if not answer_text and line.strip():
                answer_text = line.strip()
                if question_text and answer_text:
                    questions[question_text.strip()] = answer_text.strip()
                mode = None

    return questions


def main():
    parser = argparse.ArgumentParser(
        description="Генерация dict и json с вопросами для викторины"
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

    questions = build_questions(filepath)

    for i, (q, a) in enumerate(questions.items()):
        print(f"Вопрос: {q}\nОтвет: {a}\n{'-'*40}")
        if i == 2:
            break

    print(f"Всего вопросов: {len(questions)}")

    output_path = filepath.replace(".txt", "_dict.json")
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(questions, out, ensure_ascii=False, indent=2)

    print(f"Вопросы сохранены в {output_path}")


if __name__ == "__main__":
    main()
