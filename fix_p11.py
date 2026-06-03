import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('questions.json', encoding='utf-8'))

e11 = None
for e in d:
    if e['id'] == 11:
        e11 = e
        break

# 修正现有 section
for q in e11['questions']:
    sec = q.get('section', '')
    if sec.startswith('一'):
        q['section'] = '一. 单选题（50题）'
    elif sec.startswith('二'):
        q['section'] = '二. 多选题（10题）'
    elif sec.startswith('三'):
        q['section'] = '三. 判断题（10题）'
    elif sec.startswith('四'):
        q['section'] = '四. 简答题（2题）'

reading = [
    {
        'id': 63, 'type': 'reading', 'section': '五. 阅读理解（5题）',
        'question': 'What is the main advantage of C++ compared with Java?',
        'question_translation': '与Java相比，C++的主要优势是什么？',
        'options': [
            'direct hardware operation（直接硬件操作）',
            'simpler syntax（更简单的语法）',
            'cross-platform（跨平台）',
            'automatic GC（自动垃圾回收）'
        ],
        'option_translations': ['直接硬件操作', '更简单的语法', '跨平台', '自动垃圾回收'],
        'answer': 'A',
        'explanation': 'C++允许直接操作硬件（direct hardware operation），而Java运行在JVM虚拟机上，不直接操作硬件。C++语法并不比Java简单（排除B），跨平台和自动GC是Java的优势而非C++（排除C、D），故选A。',
        'introduction': 'C++ vs Java 对比阅读'
    },
    {
        'id': 64, 'type': 'reading', 'section': '五. 阅读理解（5题）',
        'question': 'What does Java\'s "write once, run anywhere" depend on?',
        'question_translation': 'Java"一次编写，到处运行"依赖什么？',
        'options': [
            'text editor（文本编辑器）',
            'operating system（操作系统）',
            'JVM and byte-code（JVM和字节码）',
            'compiler（编译器）'
        ],
        'option_translations': ['文本编辑器', '操作系统', 'JVM和字节码', '编译器'],
        'answer': 'C',
        'explanation': 'Java的跨平台特性依赖JVM（Java虚拟机）和字节码（byte-code）。Java源代码编译成字节码后，由各平台的JVM解释执行，从而实现"一次编写，到处运行"（write once, run anywhere）。文本编辑器、操作系统、编译器本身都不能实现跨平台，故选C。',
        'introduction': ''
    },
    {
        'id': 65, 'type': 'reading', 'section': '五. 阅读理解（5题）',
        'question': 'Which feature makes Java more robust?',
        'question_translation': '哪个特性使Java更加健壮？',
        'options': [
            'manual memory management（手动内存管理）',
            'complex structure（复杂结构）',
            'strict error checking（严格的错误检查）',
            'hardware operation（硬件操作）'
        ],
        'option_translations': ['手动内存管理', '复杂结构', '严格的错误检查', '硬件操作'],
        'answer': 'C',
        'explanation': 'Java通过严格的错误检查（strict error checking）机制（如编译时类型检查、运行时异常处理）增强了程序的健壮性（robustness）。Java使用自动GC而非手动内存管理（排除A），复杂结构和硬件操作与健壮性无关（排除B、D），故选C。',
        'introduction': ''
    },
    {
        'id': 66, 'type': 'reading', 'section': '五. 阅读理解（5题）',
        'question': 'What do C++ and Java have in common?',
        'question_translation': 'C++和Java有什么共同点？',
        'options': [
            'support OOP core features（支持面向对象核心特性）',
            'interpreted language（解释型语言）',
            'automatic GC（自动垃圾回收）',
            'hardware-level operation（硬件级操作）'
        ],
        'option_translations': ['支持面向对象核心特性', '解释型语言', '自动垃圾回收', '硬件级操作'],
        'answer': 'A',
        'explanation': 'C++和Java都支持面向对象编程（OOP）的核心特性，包括封装（encapsulation）、继承（inheritance）、多态（polymorphism）。Java是解释型语言且有自动GC，C++是编译型语言且无自动GC（排除B、C）；硬件级操作仅C++支持（排除D），故选A。',
        'introduction': ''
    },
    {
        'id': 67, 'type': 'reading', 'section': '五. 阅读理解（5题）',
        'question': 'According to the passage, which statement is TRUE?',
        'question_translation': '根据文章，哪个说法是正确的？',
        'options': [
            'C++ is platform-independent（C++是平台无关的）',
            'C++ is an interpreted language（C++是解释型语言）',
            'Java can operate hardware directly（Java可以直接操作硬件）',
            'Java has automatic garbage collection（Java具有自动垃圾回收功能）'
        ],
        'option_translations': ['C++是平台无关的', 'C++是解释型语言', 'Java可直接操作硬件', 'Java具有自动垃圾回收'],
        'answer': 'D',
        'explanation': 'Java具有自动垃圾回收（automatic garbage collection）是Java的显著特性之一。C++依赖于平台且是编译型语言（排除A、B），Java运行在JVM上无法直接操作硬件（排除C），故选D。',
        'introduction': ''
    }
]

for rd in reading:
    e11['questions'].append(rd)

e11['question_count'] = len(e11['questions'])
for qi, q in enumerate(e11['questions']):
    q['id'] = qi + 1

json.dump(d, open('questions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 验证
for q in e11['questions'][62:]:
    print(f'  id={q["id"]:>3} type={q["type"]:<12} ans={q["answer"]} q={q["question"][:80]}')
print(f'\n试卷11: {e11["question_count"]}题')
