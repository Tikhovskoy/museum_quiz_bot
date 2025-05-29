import argparse
import json
import os
import re


def build_questions(filepath):
    with open(filepath, encoding="koi8-r") as file:
        content = file.read()

    pattern = re.compile(r"Вопрос\s*\d+:\n(.*?)\nОтвет:\n(.*?)\n", re.DOTALL)

    questions = {}
    for match in pattern.finditer(content):
        question = match.group(1).strip()
        answer = match.group(2).strip()
        questions[question] = answer

    return questions


def main():
    parser = argparse.ArgumentParser(
        description="Преобразует текстовый файл вопросов в JSON-словарь для викторины"
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
    output_path = filepath.replace(".txt", "_dict.json")
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(questions, out, ensure_ascii=False, indent=2)

    print(f"Вопросы ({len(questions)}) сохранены в {output_path}")


if __name__ == "__main__":
    main()
