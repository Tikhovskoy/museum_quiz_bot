import os
import json

data_dir = os.path.join(os.path.dirname(__file__), 'data')
filename = '120br.txt'
filepath = os.path.join(data_dir, filename)

with open(filepath, encoding='koi8-r') as file:
    lines = file.readlines()

questions_dict = {}
question_text = ''
answer_text = ''
mode = None

for line in lines:
    line = line.rstrip('\r\n')
    if line.startswith('Вопрос'):
        mode = 'question'
        question_text = ''
        answer_text = ''
        continue
    elif line.startswith('Ответ:'):
        mode = 'answer'
        continue
    elif line.startswith('Вопрос') or line.startswith('Комментарий:') or line.startswith('Источник:') or line.startswith('Автор:'):
        mode = None
        continue

    if mode == 'question':
        if question_text:
            question_text += '\n'
        question_text += line
    elif mode == 'answer':
        if not answer_text and line.strip():
            answer_text = line.strip()
            if question_text and answer_text:
                questions_dict[question_text.strip()] = answer_text.strip()
            mode = None

for i, (q, a) in enumerate(questions_dict.items()):
    print(f"Вопрос: {q}\nОтвет: {a}\n{'-'*40}")
    if i == 2:
        break

print(f'Всего вопросов: {len(questions_dict)}')

output_path = os.path.join(data_dir, filename.replace('.txt', '_dict.json'))
with open(output_path, 'w', encoding='utf-8') as out:
    json.dump(questions_dict, out, ensure_ascii=False, indent=2)

print(f'Вопросы сохранены в {output_path}')
