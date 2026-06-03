import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('questions.json', encoding='utf-8'))

e3 = None
for e in d:
    if e['id'] == 3:
        e3 = e
        break

# 删除旧的 q42 (index 41)
del e3['questions'][41]

# 拆成5题
reading_data = [
    {
        'id': 42, 'type': 'reading', 'section': '三. 简答题',
        'question': '1. What is another name for main memory?',
        'question_translation': '主存的另一个名称是什么？',
        'options': ['Secondary Memory', 'Primary Memory', 'Auxiliary Memory', 'External Memory'],
        'option_translations': ['辅助存储器', '主存储器', '辅助存储器', '外部存储器'],
        'answer': 'B',
        'explanation': '主存又称primary memory，故选B。',
        'introduction': ''
    },
    {
        'id': 43, 'type': 'reading', 'section': '三. 简答题',
        'question': '2. What happens to RAM data when power is off?',
        'question_translation': 'RAM断电后数据会怎样？',
        'options': ['Data is saved', 'Data is lost', 'Data is stored in disk', 'Data is kept in ROM'],
        'option_translations': ['数据被保存', '数据丢失', '数据存储到磁盘', '数据保存在只读存储器'],
        'answer': 'B',
        'explanation': 'RAM断电后数据丢失，故选B。',
        'introduction': ''
    },
    {
        'id': 44, 'type': 'reading', 'section': '三. 简答题',
        'question': '3. Which RAM is widely used as main memory?',
        'question_translation': '哪种RAM广泛用作主存？',
        'options': ['SRAM', 'DRAM', 'ROM', 'Cache'],
        'option_translations': ['静态随机存取存储器', '动态随机存取存储器', '只读存储器', '高速缓存'],
        'answer': 'B',
        'explanation': 'DRAM成本低、容量大，广泛用作主存，故选B。',
        'introduction': ''
    },
    {
        'id': 45, 'type': 'reading', 'section': '三. 简答题',
        'question': '4. ROM stores ______.',
        'question_translation': 'ROM存储______。',
        'options': ['temporary data', 'computer startup instructions', 'user files', 'cache data'],
        'option_translations': ['临时数据', '计算机启动指令', '用户文件', '缓存数据'],
        'answer': 'B',
        'explanation': 'ROM存储计算机启动指令，故选B。',
        'introduction': ''
    },
    {
        'id': 46, 'type': 'reading', 'section': '三. 简答题',
        'question': '5. What is the function of cache memory?',
        'question_translation': 'Cache的功能是什么？',
        'options': ['Store all computer data', 'Speed up CPU access', 'Replace main memory', 'Save data after power off'],
        'option_translations': ['存储计算机所有数据', '加快CPU访问速度', '替代主存储器', '断电保存数据'],
        'answer': 'B',
        'explanation': 'Cache的功能是加快CPU访问速度，故选B。',
        'introduction': ''
    }
]

for rd in reading_data:
    e3['questions'].append(rd)

e3['question_count'] = len(e3['questions'])
for qi, q in enumerate(e3['questions']):
    q['id'] = qi + 1

json.dump(d, open('questions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 验证
for q in e3['questions'][39:]:
    print(f'  id={q["id"]:>3} type={q["type"]:<12} q={q["question"][:70]}')
print(f'\n试卷3: {e3["question_count"]}题 (37-41:简答/阅读)')
