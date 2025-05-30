import chardet

IGNORED_PREFIXES = ("Комментарий", "Источник", "Автор")


def detect_encoding(file_path, sample_size=1000):
    with open(file_path, "rb") as f:
        return chardet.detect(f.read(sample_size)).get("encoding", "utf-8")


def parse_questions(lines):
    questions = {}
    buffer = []
    collecting = None

    for line in map(str.strip, lines):
        if line.startswith("Вопрос"):
            buffer.clear()
            collecting = "question"
            continue
        if line.startswith("Ответ"):
            collecting = "answer"
            continue
        if line.startswith(IGNORED_PREFIXES):
            collecting = None
            continue

        if collecting == "question":
            buffer.append(line)
        elif collecting == "answer":
            question = " ".join(buffer).strip()
            answer = line.strip()
            if question and answer:
                questions[question] = answer
            buffer.clear()
            collecting = None

    return questions


def load_questions(questions_path):
    encoding = detect_encoding(questions_path)
    with open(questions_path, encoding=encoding) as file:
        return parse_questions(file)
