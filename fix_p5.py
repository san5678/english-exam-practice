import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('questions.json', encoding='utf-8'))

e5 = None
for e in d:
    if e['id'] == 5:
        e5 = e
        break

# 修正 section
for i in range(0, 30):
    e5['questions'][i]['section'] = '一. 单选题（共30题）'
for i in range(30, 50):
    e5['questions'][i]['section'] = '二. 多选题（共20题）'

# 删除旧 q51-54 (index 50-53)
del e5['questions'][50:]

# 三. 简答题（含翻译） - 2题
trans = [
    {
        'id': 51, 'type': 'translation', 'section': '三. 简答题（含翻译）',
        'question': 'Translate the following English sentences into Chinese (professional and accurate). The object-oriented approach emphasizes the role of objects, along with their attributes and operations, that form the nucleus of the solution. The structured data and its related operations could be encapsulated in a single object which may be reused and easily upgraded.',
        'question_translation': '',
        'answer': '面向对象方法强调对象及其属性与操作的作用，这些共同构成了解决方案的核心。结构化数据及其相关操作可以被封装在单个对象中，从而实现复用并便于升级维护。',
        'explanation': 'object-oriented approach=面向对象方法, encapsulated=封装, reused=复用, upgraded=升级维护。',
        'options': [], 'option_translations': [], 'introduction': ''
    },
    {
        'id': 52, 'type': 'translation', 'section': '三. 简答题（含翻译）',
        'question': 'Translate the following English sentences into Chinese (professional and accurate). A data structure is a data type whose values are composed of component elements that are related by some structure. If we provide a set of possible data values and a set of operations that act on the values, we can think of the combination as a data type.',
        'question_translation': '',
        'answer': '数据结构是一种数据类型，其值由具有某种结构关系的组成元素构成。如果我们定义一组可能的数据取值以及作用于这些取值的操作集合，就可以将这一组合视为一种数据类型。',
        'explanation': 'data structure=数据结构, data type=数据类型, component elements=组成元素, combination=组合。',
        'options': [], 'option_translations': [], 'introduction': ''
    }
]

# 四. 补充单选题（5题）
single = [
    {
        'id': 53, 'type': 'single', 'section': '四. 补充单选题',
        'question': 'Which of the following statements about linked lists is NOT correct? (        )',
        'question_translation': '下列关于链表的叙述，错误的是哪一项？',
        'options': [
            'Linked lists store elements in non-contiguous memory locations.（链表在非连续内存空间存储元素）',
            'A doubly linked list allows traversal in both directions.（双向链表支持双向遍历）',
            'Insertion and deletion in linked lists are more efficient than in arrays in most cases.（多数情况下链表增删效率高于数组）',
            'Linked lists support random access to elements, same as arrays.（链表和数组一样支持元素随机访问）'
        ],
        'option_translations': ['非连续内存存储', '双向遍历', '增删高效', '随机访问'],
        'answer': 'D',
        'explanation': '链表不支持随机访问，需从头结点依次遍历才能找到目标元素；而数组支持通过索引直接随机访问，其余选项均为链表的正确特性，故选D。',
        'introduction': ''
    },
    {
        'id': 54, 'type': 'single', 'section': '四. 补充单选题',
        'question': 'What is the main difference between linked lists and arrays in terms of memory storage? (        )',
        'question_translation': '链表和数组在内存存储方面的主要区别是什么？',
        'options': [
            'Linked lists store elements in contiguous memory, while arrays do not.（链表存储连续内存，数组反之）',
            'Neither linked lists nor arrays store elements in contiguous memory.（链表和数组均不存储在连续内存）',
            'Both linked lists and arrays store elements in contiguous memory.（链表和数组均存储在连续内存）',
            'Arrays store elements in contiguous memory, while linked lists do not.（数组存储在连续内存，链表不是）'
        ],
        'option_translations': ['链表连续数组不连续', '均不连续', '均连续', '数组连续链表不连续'],
        'answer': 'D',
        'explanation': '数组的元素存储在连续的内存地址中，可通过索引直接定位；链表的结点存储在非连续内存中，通过指针连接，这是两者在内存存储上的核心区别，故选D。',
        'introduction': ''
    },
    {
        'id': 55, 'type': 'single', 'section': '四. 补充单选题',
        'question': 'Which type of linked list allows traversal in two directions? ( )',
        'question_translation': '哪种链表可以双向遍历？',
        'options': [
            'Doubly linked list（双向链表）',
            'All types of linked lists（所有类型的链表）',
            'Singly linked list（单向链表）',
            'Circular linked list（循环链表）'
        ],
        'option_translations': ['双向链表', '所有链表', '单向链表', '循环链表'],
        'answer': 'A',
        'explanation': '双向链表（Doubly linked list）的每个结点有两个指针，分别指向前驱和后继结点，因此可双向遍历；单链表只能单向遍历，循环链表虽可循环，但默认单向，故选A。',
        'introduction': ''
    },
    {
        'id': 56, 'type': 'single', 'section': '四. 补充单选题',
        'question': 'Why do linked lists have higher memory overhead than arrays? ( )',
        'question_translation': '为什么链表比数组的内存开销更大？',
        'options': [
            'Because linked lists have dynamic size.（因为链表大小动态可变）',
            'Because each node of linked lists needs to store a pointer besides data.（因为链表每个结点除数据外还要存指针）',
            'Because linked lists do not support random access.（因为链表不支持随机访问）',
            'Because linked lists need to store more data elements.（因为链表需要存储更多数据元素）'
        ],
        'option_translations': ['大小动态可变', '结点需存指针', '不支持随机访问', '存储更多数据元素'],
        'answer': 'B',
        'explanation': '链表的每个结点除了存储数据（数据域），还需要存储指针（指针域）来连接相邻结点，额外的指针占用了更多内存；A（动态大小）是优点，不影响内存开销，C（不支持随机访问）是访问特性，D（存储更多元素）与内存开销无关，故选B。',
        'introduction': ''
    },
    {
        'id': 57, 'type': 'single', 'section': '四. 补充单选题',
        'question': 'Which of the following is NOT an application of linked lists? ( )',
        'question_translation': '下列哪一项不是链表的应用？',
        'options': [
            'Dynamic data collections（动态数据集合）',
            'Text editors（文本编辑器）',
            'Random access to elements（元素随机访问）',
            'Implementing stacks and queues（实现栈和队列）'
        ],
        'option_translations': ['动态数据集合', '文本编辑器', '元素随机访问', '实现栈和队列'],
        'answer': 'C',
        'explanation': '随机访问是数组的特性，链表不支持随机访问，因此"随机访问元素"不可能是链表的应用；A（动态数据集合）、B（文本编辑器，用于存储字符）、D（实现栈和队列）均是链表的常见应用，故选C。',
        'introduction': ''
    }
]

for t in trans:
    e5['questions'].append(t)
for s in single:
    e5['questions'].append(s)

e5['question_count'] = len(e5['questions'])
for qi, q in enumerate(e5['questions']):
    q['id'] = qi + 1

json.dump(d, open('questions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 验证最后7题
for q in e5['questions'][50:]:
    print(f'  id={q["id"]:>3} type={q["type"]:<12} sec={q["section"][:20]} q={q["question"][:80]}')
print(f'\n试卷5: {e5["question_count"]}题 (单选30+20 + 翻译2 + 单选5)')
