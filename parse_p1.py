import json
d = json.load(open('questions.json', encoding='utf-8'))

e1 = [e for e in d if e['id'] == 1][0]
for q in e1['questions']:
    if q['id'] in range(31, 41):
        q['type'] = 'multiple'
    elif q['id'] in (41, 42):
        q['type'] = 'translation'
    print(f'  Q{q["id"]:>3} type={q["type"]:<12} ans={q["answer"]:<6} q={q["question"][:60]}')

json.dump(d, open('questions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n修正完成：单选题30 + 多选题10 + 简答题2 = {len(e1["questions"])}题')
