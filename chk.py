import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('questions.json', encoding='utf-8'))

e11 = None
for e in d:
    if e['id'] == 11:
        e11 = e
        break

print(f'试卷11 当前: {e11["question_count"]}题')
for q in e11['questions'][-10:]:
    print(f'  id={q["id"]:>3} type={q["type"]:<12} sec={q.get("section","")[:20]} q={q["question"][:90]}')
