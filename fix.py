import json, sys, os, copy
sys.stdout.reconfigure(encoding='utf-8')

# Load questions.json
d = json.load(open('questions.json', encoding='utf-8'))

# ============================================================
# 试卷3 = 第三次作业 = d[7]
# Q40: 英译汉 Cache memory is a high-speed storage...
# Q42: 汉译英 静态随机存取存储器不需要刷新电路...
# ============================================================
e3 = d[7]
# q40 (index 39): id=1, type=single -> should be translation
q40 = e3['questions'][39]
q40['type'] = 'translation'
q40['question'] = 'Translate the following English into Chinese (英译汉): Cache memory is a high-speed storage that bridges the speed gap between CPU and main memory.'
q40['question_translation'] = '英译汉：高速缓冲存储器（Cache）'
q40['answer'] = '高速缓冲存储器是一种高速存储器，用于弥补CPU与主存储器之间的速度差距。'
q40['explanation'] = 'Cache memory译为"高速缓冲存储器"，bridge the gap译为"弥补差距"。'
q40['options'] = []
q40['option_translations'] = []
q40['introduction'] = '简答题（含翻译）'

# q42 (index 41): id=3, type=single -> should be translation
q42 = e3['questions'][41]
q42['type'] = 'translation'
q42['question'] = 'Translate the following Chinese into English (汉译英): 静态随机存取存储器不需要刷新电路，因此存取速度比动态随机存取存储器更快。'
q42['question_translation'] = '汉译英：SRAM vs DRAM 速度对比'
q42['answer'] = 'Static random-access memory(SRAM) does not require a refresh circuit, so it has a faster access speed than dynamic random-access memory(DRAM).'
q42['explanation'] = 'SRAM = Static Random-Access Memory, DRAM = Dynamic Random-Access Memory, refresh circuit = 刷新电路。'
q42['options'] = []
q42['option_translations'] = []
q42['introduction'] = '简答题（含翻译）'

print('试卷3 Q40/Q42 翻译题已修正')

# ============================================================
# 试卷4 = 第四次作业 = d[10]
# q36-q40 (id 1-5) 是阅读理解题，type=single -> reading
# ============================================================
e4 = d[10]
# q36-q40 are reading comprehension
reading_data_4 = [
    {
        'question': 'What does I/O stand for in the passage?',
        'question_translation': '在这段文字中，I/O代表什么？',
        'options': ['Internal/External（内部/外部）', 'Input/Output（输入/输出）', 'Input/Operation（输入/操作）', 'Instruction/Output（指令/输出）'],
        'option_translations': ['Internal/External', 'Input/Output', 'Input/Operation', 'Instruction/Output'],
        'answer': 'B',
        'explanation': '根据文章内容及计算机基础术语，I/O是Input/Output的缩写，代表"输入/输出"，故选B。'
    },
    {
        'question': 'Which of the following is NOT an input device mentioned in the passage?',
        'question_translation': '以下哪一项不是文中提到的输入设备？',
        'options': ['Scanner（扫描仪）', 'Microphone（麦克风）', 'Monitor（显示器）', 'Keyboard（键盘）'],
        'option_translations': ['Scanner', 'Microphone', 'Monitor', 'Keyboard'],
        'answer': 'C',
        'explanation': 'monitor（显示器）是输出设备，用于显示计算机的视觉输出，文章中明确将其归为输出设备，不属于输入设备，故选C。'
    },
    {
        'question': 'Which device is an example of both input and output according to the passage?',
        'question_translation': '根据文章，哪个设备既是输入设备又是输出设备？',
        'options': ['Mouse（鼠标）', 'Touch screen（触摸屏）', 'Printer（打印机）', 'Speaker（扬声器）'],
        'option_translations': ['Mouse', 'Touch screen', 'Printer', 'Speaker'],
        'answer': 'B',
        'explanation': '文章中提到touch screen（触摸屏）可同时检测触摸输入和显示输出内容，兼具输入和输出功能，是双向I/O设备的典型例子，故选B。'
    },
    {
        'question': 'What is the function of output devices?',
        'question_translation': '输出设备的功能是什么？',
        'options': ['Show processed data to users（向用户展示处理后的数据）', 'Send data to the computer（向计算机发送数据）', 'Read printed text into computers（将印刷文本读取到计算机中）', 'Store data for a long time（长期存储数据）'],
        'option_translations': ['Show processed data to users', 'Send data to the computer', 'Read printed text into computers', 'Store data for a long time'],
        'answer': 'A',
        'explanation': '根据文章中简答题的表述，输出设备的功能是向用户显示或呈现处理后的信息，即Show processed data to users，故选A。'
    },
    {
        'question': 'Why are I/O devices essential for computer systems?',
        'question_translation': '为什么输入/输出设备对计算机系统至关重要？',
        'options': ['They can store a large amount of data（它们可以存储大量数据）', 'They process data quickly（它们处理数据速度快）', 'They are easy to operate（它们操作简单）', 'They connect users and computer systems（它们连接用户与计算机系统）'],
        'option_translations': ['They can store a large amount of data', 'They process data quickly', 'They are easy to operate', 'They connect users and computer systems'],
        'answer': 'D',
        'explanation': '文章中提到I/O设备实现了用户与计算机系统之间的通信，这是其对计算机系统至关重要的原因，即连接用户与计算机系统，故选D。'
    }
]

for i, rd in enumerate(reading_data_4):
    q = e4['questions'][35 + i]
    q['type'] = 'reading'
    q['question'] = rd['question']
    q['question_translation'] = rd['question_translation']
    q['options'] = rd['options']
    q['option_translations'] = rd['option_translations']
    q['answer'] = rd['answer']
    q['explanation'] = rd['explanation']
    q['introduction'] = '阅读理解题'
    q['section'] = '四. 阅读理解'

print('试卷4 阅读理解题已修正')

# ============================================================
# 试卷5 = 第五次作业 = d[8]
# q51 翻译题第一题已有 (id=2, type=translation) ✓
# q52-q54 阅读理解最后两题 (id=1,2,3 -> 实际是阅读理解)
# 但实际上docx中 p403-450 有翻译题1-2和补充单选题1-5
# ============================================================
e5 = d[8]

# q51 (index 50): id=2, type=translation - keep as is ✓
# q52 (index 51): id=1, type=single -> reading
q52 = e5['questions'][51]
q52['type'] = 'reading'
q52['question'] = 'Which of the following statements about linked lists is NOT correct? (        )'
q52['question_translation'] = '下列关于链表的叙述，错误的是哪一项？'
q52['options'] = [
    'Linked lists store elements in non-contiguous memory locations.（链表在非连续内存空间存储元素）',
    'A doubly linked list allows traversal in both directions.（双向链表支持双向遍历）',
    'Insertion and deletion in linked lists are more efficient than in arrays in most cases.（多数情况下链表增删效率高于数组）',
    'Linked lists support random access to elements, same as arrays.（链表和数组一样支持元素随机访问）'
]
q52['option_translations'] = ['非连续存储', '双向遍历', '增删高效', '随机访问']
q52['answer'] = 'D'
q52['explanation'] = '链表不支持随机访问，需从头结点依次遍历才能找到目标元素；而数组支持通过索引直接随机访问，其余选项均为链表的正确特性，故选D。'
q52['introduction'] = '阅读理解题'
q52['section'] = '四. 补充单选题'

# q53 (index 52): id=2, type=single -> reading
q53 = e5['questions'][52]
q53['type'] = 'reading'
q53['question'] = 'What is the main difference between linked lists and arrays in terms of memory storage? (        )'
q53['question_translation'] = '链表和数组在内存存储方面的主要区别是什么？'
q53['options'] = [
    'Linked lists store elements in contiguous memory, while arrays do not.（链表存储连续内存，数组反之）',
    'Neither linked lists nor arrays store elements in contiguous memory.（链表和数组均不存储在连续内存）',
    'Both linked lists and arrays store elements in contiguous memory.（链表和数组均存储在连续内存）',
    'Arrays store elements in contiguous memory, while linked lists do not.（数组存储在连续内存，链表不是）'
]
q53['option_translations'] = ['链表连续数组不连续', '均不连续', '均连续', '数组连续链表不连续']
q53['answer'] = 'D'
q53['explanation'] = '数组的元素存储在连续的内存地址中，可通过索引直接定位；链表的结点存储在非连续内存中，通过指针连接，这是两者在内存存储上的核心区别，故选D。'
q53['introduction'] = '阅读理解题'
q53['section'] = '四. 补充单选题'

# q54 (index 53): id=3, type=single -> reading
q54 = e5['questions'][53]
q54['type'] = 'reading'
q54['question'] = 'Which type of linked list allows traversal in two directions? ( )'
q54['question_translation'] = '哪种链表可以双向遍历？'
q54['options'] = [
    'Doubly linked list（双向链表）',
    'All types of linked lists（所有类型的链表）',
    'Singly linked list（单向链表）',
    'Circular linked list（循环链表）'
]
q54['option_translations'] = ['双向链表', '所有链表', '单向链表', '循环链表']
q54['answer'] = 'A'
q54['explanation'] = '双向链表（Doubly linked list）的每个结点有两个指针，分别指向前驱和后继结点，因此可双向遍历；单链表只能单向遍历，循环链表虽可循环，但默认单向，故选A。'
q54['introduction'] = '阅读理解题'
q54['section'] = '四. 补充单选题'

print('试卷5 阅读理解题已修正')

# ============================================================
# 试卷6 = 第六次作业 = d[9]
# 缺少 Q51-Q54 翻译题（在docx的p443-p451）
# ============================================================
e6 = d[9]
# 当前questions列表有55题。需要追加4题 (Q51-Q54)

# 先修正已有题目的 section
# 这些在 "五、简答题（翻译）"
for i in range(51, 55):
    q = e6['questions'][i]
    q['section'] = '五. 简答题（翻译）'

trans_data_6 = [
    {
        'id': 51,
        'type': 'translation',
        'section': '五. 简答题（翻译）',
        'question': 'Translate the following English into Chinese: A graph consists of a set of vertices and a set of edges that connect pairs of vertices, which can be used to model relationships between objects.',
        'question_translation': '英译汉：图的结构定义',
        'answer': '图由一组顶点和一组连接顶点对的边组成，可用于建模对象之间的关系。',
        'explanation': 'vertices=顶点, edges=边, model=建模。',
        'options': [],
        'option_translations': [],
        'introduction': '简答题（含翻译）'
    },
    {
        'id': 52,
        'type': 'translation',
        'section': '五. 简答题（翻译）',
        'question': 'Translate the following English into Chinese: A binary search tree is a binary tree where the left subtree of each node contains only nodes with values less than the node\'s value, and the right subtree contains only nodes with values greater than the node\'s value.',
        'question_translation': '英译汉：二叉搜索树的定义',
        'answer': '二叉搜索树是一种二叉树，其中每个节点的左子树仅包含值小于该节点值的节点，右子树仅包含值大于该节点值的节点。',
        'explanation': 'binary search tree=二叉搜索树, left subtree=左子树, right subtree=右子树。',
        'options': [],
        'option_translations': [],
        'introduction': '简答题（含翻译）'
    },
    {
        'id': 53,
        'type': 'translation',
        'section': '五. 简答题（翻译）',
        'question': 'Translate the following English into Chinese: Heapify is an operation that restores the heap property after the structure of the heap is changed.',
        'question_translation': '英译汉：堆化操作定义',
        'answer': '堆化是在堆的结构发生变化后，恢复堆特性的一种操作。',
        'explanation': 'Heapify=堆化, restore=恢复, heap property=堆特性。',
        'options': [],
        'option_translations': [],
        'introduction': '简答题（含翻译）'
    },
    {
        'id': 54,
        'type': 'translation',
        'section': '五. 简答题（翻译）',
        'question': 'Translate the following English into Chinese: The time complexity of an algorithm is a measure of the amount of time an algorithm takes to run as a function of the size of the input.',
        'question_translation': '英译汉：时间复杂度定义',
        'answer': '算法的时间复杂度是衡量算法运行所需时间随输入规模变化的一种度量方式。',
        'explanation': 'time complexity=时间复杂度, as a function of=随...变化。',
        'options': [],
        'option_translations': [],
        'introduction': '简答题（含翻译）'
    }
]

max_id_e6 = max(q.get('id', 0) for q in e6['questions'])
for td in trans_data_6:
    td['id'] = max_id_e6 + 1
    max_id_e6 += 1
    # Copy any required fields
    if 'answer' not in td: td['answer'] = ''
    if 'explanation' not in td: td['explanation'] = ''
    if 'introduction' not in td: td['introduction'] = ''
    if 'question_translation' not in td: td['question_translation'] = ''
    if 'options' not in td: td['options'] = []
    if 'option_translations' not in td: td['option_translations'] = []
    if 'section' not in td or not td['section']:
        td['section'] = td.get('section', '')
    e6['questions'].append(td)

e6['question_count'] = len(e6['questions'])

print('试卷6 Q51-Q54 翻译题已添加')

# ============================================================
# 试卷9 = 第九次作业 = d[2]
# 缺少 Q51-Q52 翻译题 和 (1)-(5) 阅读理解
# ============================================================
e9 = d[2]

# Q51 英译汉
e9_q51 = {
    'id': 51,
    'type': 'translation',
    'section': '四. 简答题',
    'question': 'Translate the following English into Chinese (英译汉): We can view an operating system as a resource allocator that manages computer resources.',
    'question_translation': '英译汉：操作系统作为资源分配器',
    'answer': '我们可以把操作系统看作是管理计算机资源的资源分配器。',
    'explanation': 'view...as=把...看作, resource allocator=资源分配器。',
    'options': [],
    'option_translations': [],
    'introduction': '简答题（含翻译）'
}

# Q52 汉译英
e9_q52 = {
    'id': 52,
    'type': 'translation',
    'section': '四. 简答题',
    'question': 'Translate the following Chinese into English (汉译英): 现代操作系统具备多任务处理能力，可以同时运行多个进程。',
    'question_translation': '汉译英：现代操作系统的多任务能力',
    'answer': 'Modern operating systems have multitasking capabilities and can run multiple processes simultaneously.',
    'explanation': '多任务处理=multitasking, 进程=processes, 同时=simultaneously。',
    'options': [],
    'option_translations': [],
    'introduction': '简答题（含翻译）'
}

# 阅读理解 (1)-(5)
reading_data_9 = [
    {
        'id': 53,
        'type': 'reading',
        'section': '五. 阅读理解',
        'question': 'What is the passage mainly about? ( )',
        'question_translation': '这篇文章主要讲的是什么？',
        'options': ['Computer hardware（计算机硬件）', 'Keyboard usage（键盘使用）', 'Operating system（操作系统）', 'Computer games（电脑游戏）'],
        'option_translations': ['计算机硬件', '键盘使用', '操作系统', '电脑游戏'],
        'answer': 'C',
        'explanation': '整篇阅读及整套习题的知识点均围绕操作系统展开。',
        'introduction': '阅读理解（Operating System）'
    },
    {
        'id': 54,
        'type': 'reading',
        'section': '五. 阅读理解',
        'question': 'What is the main job of an OS? ( )',
        'question_translation': '操作系统的主要工作是什么？',
        'options': ['Resource management（资源管理）', 'Printing files（打印文件）', 'Playing music（播放音乐）', 'Watching videos（观看视频）'],
        'option_translations': ['资源管理', '打印文件', '播放音乐', '观看视频'],
        'answer': 'A',
        'explanation': '操作系统最核心的工作就是管理计算机软硬件资源。',
        'introduction': '阅读理解（Operating System）'
    },
    {
        'id': 55,
        'type': 'reading',
        'section': '五. 阅读理解',
        'question': 'Which of the following is not mentioned as a computer resource? ( )',
        'question_translation': '以下哪项不属于计算机资源？',
        'options': ['CPU time（CPU时间）', 'Paper（纸张）', 'I/O devices（输入输出设备）', 'Memory space（内存空间）'],
        'option_translations': ['CPU时间', '纸张', 'I/O设备', '内存空间'],
        'answer': 'B',
        'explanation': '纸张不属于计算机电子资源，其余三项都是标准系统资源。',
        'introduction': '阅读理解（Operating System）'
    },
    {
        'id': 56,
        'type': 'reading',
        'section': '五. 阅读理解',
        'question': 'Which statement is true about modern OS? ( )',
        'question_translation': '关于现代操作系统说法正确的是？',
        'options': ['They are multitasking（支持多任务）', 'They are single-tasking（仅支持单任务）', 'They have no job queue（没有作业队列）', 'They cannot run processes together（无法同时运行进程）'],
        'option_translations': ['支持多任务', '仅支持单任务', '没有作业队列', '无法同时运行进程'],
        'answer': 'A',
        'explanation': '支持多任务是现代操作系统的典型特征。',
        'introduction': '阅读理解（Operating System）'
    },
    {
        'id': 57,
        'type': 'reading',
        'section': '五. 阅读理解',
        'question': 'What can people do for special-purpose equipment? ( )',
        'question_translation': '人们可以为专用设备做什么？',
        'options': ['Destroy hardware（损坏硬件）', 'Design or modify OS（设计或修改操作系统）', 'Change CPU randomly（随意更换中央处理器）', 'Delete all software（删除所有软件）'],
        'option_translations': ['损坏硬件', '设计或修改操作系统', '随意更换CPU', '删除所有软件'],
        'answer': 'B',
        'explanation': '针对专用设备，人们可以设计或修改适配的操作系统。',
        'introduction': '阅读理解（Operating System）'
    }
]

e9['questions'].append(e9_q51)
e9['questions'].append(e9_q52)
for rd in reading_data_9:
    rd['options'] = rd.get('options', [])
    rd['option_translations'] = rd.get('option_translations', [])
    rd['introduction'] = rd.get('introduction', '')
    e9['questions'].append(rd)

e9['question_count'] = len(e9['questions'])
print('试卷9 Q51-Q52翻译题 + (1)-(5)阅读理解已添加')

# Save
json.dump(d, open('questions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n=== 完成 ===')
print(f'试卷3 (d[7]): Q40/Q42 翻译题已修正 → {d[7]["question_count"]} 题')
print(f'试卷4 (d[10]): q36-q40 阅读理解题已修正 → {d[10]["question_count"]} 题')
print(f'试卷5 (d[8]): q52-q54 阅读理解题已修正 → {d[8]["question_count"]} 题')
print(f'试卷6 (d[9]): Q51-Q54 翻译题已添加 → {d[9]["question_count"]} 题')
print(f'试卷9 (d[2]): Q51-Q52翻译+(1)-(5)阅读已添加 → {d[2]["question_count"]} 题')
