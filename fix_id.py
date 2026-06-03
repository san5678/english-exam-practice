import json, sys
sys.stdout.reconfigure(encoding='utf-8')

d = json.load(open('questions.json', encoding='utf-8'))
d.sort(key=lambda e: e['id'])

for e in d:
    print(f'id={e["id"]:>2}: {e["filename"][:50]}')

json.dump(d, open('questions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('\n已按 id 排序')
