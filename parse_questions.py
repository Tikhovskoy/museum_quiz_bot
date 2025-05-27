import os
import re

data_dir = os.path.join(os.path.dirname(__file__), 'data')
filename = '120br.txt'
filepath = os.path.join(data_dir, filename)

with open(filepath, encoding='koi8-r') as file:
    content = file.read()

question_pattern = re.compile(
    r'Вопрос\s*(\d+):\n(.*?)\nОтвет:\n(.*?)\n(?:Комментарий:\n(.*?))?(?:\nИсточник:\n(.*?))?(?:\nАвтор:\n(.*?))?\n',
    re.DOTALL
)

questions = []
for match in question_pattern.finditer(content):
    number = int(match.group(1))
    question = match.group(2).strip()
    answer = match.group(3).strip()
    comment = match.group(4).strip() if match.group(4) else ""
    source = match.group(5).strip() if match.group(5) else ""
    author = match.group(6).strip() if match.group(6) else ""

    questions.append({
        'number': number,
        'question': question,
        'answer': answer,
        'comment': comment,
        'source': source,
        'author': author,
    })

for q in questions[:3]:
    print(f"Вопрос {q['number']}: {q['question']}")
    print(f"Ответ: {q['answer']}")
    print(f"Комментарий: {q['comment']}")
    print(f"Источник: {q['source']}")
    print(f"Автор: {q['author']}\n{'-'*40}")
