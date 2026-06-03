import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('questions.json', encoding='utf-8'))

# 试卷6 (d[9]) 应该有 55 + 4 = 59 题，当前 63 题（多了4道）
# 试卷9 (d[2]) 应该有 50 + 2 + 5 = 57 题，当前 64 题（多了7道）
# 删除重复的题（最后添加的4+7道）

# 试卷6：只保留前55+4=59题
e6 = d[9]
print(f'试卷6 修复前: {len(e6["questions"])} 题')
e6['questions'] = e6['questions'][:59]
e6['question_count'] = 59
print(f'试卷6 修复后: {len(e6["questions"])} 题')

# 试卷9：只保留前50+7=57题  
e9 = d[2]
print(f'试卷9 修复前: {len(e9["questions"])} 题')
e9['questions'] = e9['questions'][:57]
e9['question_count'] = 57
print(f'试卷9 修复后: {len(e9["questions"])} 题')

json.dump(d, open('questions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('修复完成')
