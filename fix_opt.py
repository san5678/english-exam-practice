import json, re
d = json.load(open('questions.json', encoding='utf-8'))

# 试卷11 新增的阅读题 id 63-67
e11 = [e for e in d if e['id'] == 11][0]
for q in e11['questions']:
    if q['id'] in (63, 64, 65, 66, 67):
        q['options'] = [re.sub(r'[（(][^）)]*[）)]', '', o).strip() for o in q.get('options', [])]

json.dump(d, open('questions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 验证
for q in e11['questions']:
    if q['id'] in (63, 64, 65, 66, 67):
        print(f'  id={q["id"]} options={q["options"]}')
print('完成')
