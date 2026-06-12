import json
import os
import sys
import random
from functools import wraps
from flask import Flask, jsonify, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, init_db

sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'english-exam-practice-dev-key-2024')

init_db()

DATA_FILE = 'questions.json'


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


@app.route('/')
def index():
    return render_template('index.html')


TOPIC_MAP = {
    1: '硬件知识',
    2: 'CPU与内存',
    3: '存储与总线',
    4: 'I/O设备',
    5: '数据结构基础',
    6: '数据结构与算法',
    7: '数据结构综合',
    8: '数据结构与算法综合',
    9: '操作系统',
    10: 'C语言',
    11: 'C++与Java',
    12: '面向对象编程'
}

def _short_title(doc):
    """根据试卷 id 生成简短标题"""
    pid = doc.get('id', 0)
    topic = TOPIC_MAP.get(pid, '')
    if topic:
        return f'第{pid}次 · {topic}'
    return doc['filename'].replace('.docx', '')


@app.route('/api/register', methods=['POST'])
def api_register():
    body = request.get_json()
    if not body:
        return jsonify({'error': '请提供数据'}), 400
    username = body.get('username', '').strip()
    password = body.get('password', '')
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    if len(username) < 2 or len(username) > 20:
        return jsonify({'error': '用户名长度需在2-20之间'}), 400
    if len(password) < 4:
        return jsonify({'error': '密码长度至少4位'}), 400

    db = get_db()
    try:
        existing = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            return jsonify({'error': '用户名已存在'}), 409
        db.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        db.commit()
        user = db.execute('SELECT id, username FROM users WHERE username = ?', (username,)).fetchone()
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'ok': True, 'username': username})
    finally:
        db.close()


@app.route('/api/login', methods=['POST'])
def api_login():
    body = request.get_json()
    if not body:
        return jsonify({'error': '请提供数据'}), 400
    username = body.get('username', '').strip()
    password = body.get('password', '')
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    db = get_db()
    try:
        user = db.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,)).fetchone()
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': '用户名或密码错误'}), 401
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'ok': True, 'username': user['username']})
    finally:
        db.close()


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'ok': True})


@app.route('/api/me')
def api_me():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'username': session['username']})
    return jsonify({'logged_in': False})


@app.route('/api/documents')
def api_documents():
    data = load_data()
    result = []
    for i, doc in enumerate(data):
        title = _short_title(doc)
        result.append({
            'index': i,
            'title': title,
            'filename': doc['filename'],
            'question_count': doc['question_count']
        })
    return jsonify(result)


@app.route('/api/questions/<int:doc_index>')
def api_questions(doc_index):
    data = load_data()
    if doc_index < 0 or doc_index >= len(data):
        return jsonify({'error': 'Document not found'}), 404
    doc = data[doc_index]
    questions = []
    for q in doc['questions']:
        questions.append({
            'id': q['id'],
            'question': q['question'],
            'question_translation': q.get('question_translation', ''),
            'options': q['options'],
            'option_translations': q.get('option_translations', []),
            'answer': q.get('answer', ''),
            'explanation': q.get('explanation', ''),
            'introduction': q.get('introduction', ''),
            'section': q.get('section', ''),
            'type': q.get('type', 'single')
        })
    return jsonify({
        'title': doc['title'],
        'filename': doc['filename'],
        'question_count': doc['question_count'],
        'questions': questions
    })


@app.route('/api/reparse')
def api_reparse():
    from parser import parse_all_in_directory
    results = parse_all_in_directory('.')
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return jsonify({
        'status': 'ok',
        'files': len(results),
        'total_questions': sum(r['question_count'] for r in results)
    })


@app.route('/api/random-exam')
def api_random_exam():
    data = load_data()
    if not data:
        return jsonify({'error': 'No data'}), 404

    count = request.args.get('count', 50, type=int)
    count = max(1, min(count, sum(doc['question_count'] for doc in data)))

    flat = []
    for doc_idx, doc in enumerate(data):
        for q in doc['questions']:
            if not q.get('options'):
                continue
            flat.append({
                'doc_index': doc_idx,
                'source': doc['filename'].replace('.docx', ''),
                'question': q
            })

    if not flat:
        return jsonify({'error': 'No valid questions'}), 404

    groups = {}
    for item in flat:
        groups.setdefault(item['doc_index'], []).append(item)

    per_doc = count // len(groups)
    remaining = count % len(groups)

    pool = []
    for doc_idx in sorted(groups.keys()):
        take = per_doc + (1 if doc_idx < remaining else 0)
        take = min(take, len(groups[doc_idx]))
        picked = random.sample(groups[doc_idx], take)
        pool.extend(picked)

    if len(pool) < count:
        all_items = [it for it in flat if it not in pool]
        needed = count - len(pool)
        if all_items:
            pool.extend(random.sample(all_items, min(needed, len(all_items))))

    random.shuffle(pool)

    questions = []
    for idx, item in enumerate(pool):
        q = item['question']
        questions.append({
            'id': idx + 1,
            'question': q['question'],
            'question_translation': q.get('question_translation', ''),
            'options': q['options'],
            'option_translations': q.get('option_translations', []),
            'answer': q.get('answer', ''),
            'explanation': q.get('explanation', ''),
            'introduction': q.get('introduction', ''),
            'section': q.get('section', ''),
            'type': q.get('type', 'single'),
            'source': item['source']
        })

    sources = {}
    for item in pool:
        sources[item['source']] = sources.get(item['source'], 0) + 1

    return jsonify({
        'total': len(questions),
        'sources': sources,
        'questions': questions
    })


# ============================================================
# 评分系统
# ============================================================

POINT_RULES = {
    'single': 1,
    'multiple': 2,
    'judge': 1,
    'translation': 3,
    'reading': 2
}


@app.route('/api/score-rules')
def api_score_rules():
    return jsonify(POINT_RULES)


@app.route('/api/submit-answers', methods=['POST'])
def api_submit_answers():
    body = request.get_json()
    if not body:
        return jsonify({'error': 'No data'}), 400

    paper_id = body.get('paper_id', 0)
    answers = body.get('answers', {})
    question_list = body.get('questions', [])

    data = load_data()
    if not question_list:
        if paper_id < 0 or paper_id >= len(data):
            return jsonify({'error': 'Paper not found'}), 404
        question_list = data[paper_id]['questions']

    source_map = {}
    for q in question_list:
        qid = str(q.get('id', ''))
        if q.get('source'):
            source_map[qid] = q['source']
        elif 0 <= paper_id < len(data):
            source_map[qid] = data[paper_id].get('filename', '')
        else:
            source_map[qid] = ''

    total_points = 0
    earned_points = 0
    detail = []

    for q in question_list:
        qtype = q.get('type', 'single')
        qid = str(q.get('id', ''))
        correct_answer = q.get('answer', '').strip()
        user_answer = answers.get(qid, '')

        point_value = POINT_RULES.get(qtype, 1)
        total_points += point_value

        result = {
            'id': q['id'],
            'type': qtype,
            'point': point_value,
            'correct_answer': correct_answer,
            'user_answer': user_answer or ''
        }
        answered = bool(user_answer)

        if qtype == 'translation':
            result['scored'] = 'manual'
            result['earned'] = point_value if answered else 0
            result['grade'] = 'submitted' if answered else 'unanswered'
            if answered:
                earned_points += point_value
        elif qtype == 'multiple':
            if not answered:
                result['earned'] = 0
                result['grade'] = 'unanswered'
            else:
                correct_set = set(correct_answer.upper())
                user_set = set(user_answer.strip().upper())
                if user_set == correct_set:
                    result['earned'] = point_value
                    result['grade'] = 'correct'
                    earned_points += point_value
                elif user_set and user_set.issubset(correct_set):
                    result['earned'] = max(1, point_value // 2)
                    result['grade'] = 'partial'
                    earned_points += max(1, point_value // 2)
                else:
                    result['earned'] = 0
                    result['grade'] = 'incorrect'
        else:
            if not answered:
                result['earned'] = 0
                result['grade'] = 'unanswered'
            elif user_answer.strip().upper() == correct_answer.upper():
                result['earned'] = point_value
                result['grade'] = 'correct'
                earned_points += point_value
            else:
                result['earned'] = 0
                result['grade'] = 'incorrect'
        detail.append(result)

    percentage = (earned_points / total_points * 100) if total_points > 0 else 0
    if percentage >= 90:
        grade = 'A'
    elif percentage >= 80:
        grade = 'B'
    elif percentage >= 70:
        grade = 'C'
    elif percentage >= 60:
        grade = 'D'
    else:
        grade = 'F'

    answered_count = sum(1 for d in detail if d.get('grade') != 'unanswered')
    correct_count = sum(1 for d in detail if d.get('grade') == 'correct')

    if 'user_id' in session:
        db = get_db()
        try:
            for d in detail:
                if d['grade'] in ('incorrect', 'partial'):
                    qid = str(d['id'])
                    source_file = source_map.get(qid, '')
                    db.execute('''
                        INSERT INTO error_book (user_id, question_id, source_file, question_type, wrong_count, last_wrong_at)
                        VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                        ON CONFLICT(user_id, question_id, source_file)
                        DO UPDATE SET wrong_count = wrong_count + 1,
                                      correct_count = 0,
                                      last_wrong_at = CURRENT_TIMESTAMP,
                                      mastered = 0
                    ''', (session['user_id'], qid, source_file, d['type']))
            db.commit()
        finally:
            db.close()

    return jsonify({
        'total_points': total_points,
        'earned_points': earned_points,
        'percentage': round(percentage, 1),
        'grade': grade,
        'answered_count': answered_count,
        'correct_count': correct_count,
        'total_count': len(detail),
        'detail': detail
    })


@app.route('/api/error-book')
@login_required
def api_error_book():
    db = get_db()
    try:
        rows = db.execute('''
            SELECT id, question_id, source_file, question_type,
                   wrong_count, correct_count, mastered, last_wrong_at
            FROM error_book
            WHERE user_id = ?
            ORDER BY mastered ASC, wrong_count DESC, last_wrong_at DESC
        ''', (session['user_id'],)).fetchall()

        result = []
        for r in rows:
            total = r['correct_count'] + r['wrong_count']
            accuracy = round(r['correct_count'] / total * 100) if total > 0 else 0
            result.append({
                'id': r['id'],
                'question_id': r['question_id'],
                'source_file': r['source_file'],
                'question_type': r['question_type'],
                'wrong_count': r['wrong_count'],
                'correct_count': r['correct_count'],
                'accuracy_rate': accuracy,
                'mastered': bool(r['mastered']),
                'last_wrong_at': r['last_wrong_at']
            })
        return jsonify(result)
    finally:
        db.close()


@app.route('/api/error-book/stats')
@login_required
def api_error_book_stats():
    db = get_db()
    try:
        total = db.execute(
            'SELECT COUNT(*) as cnt FROM error_book WHERE user_id = ?',
            (session['user_id'],)
        ).fetchone()['cnt']

        mastered = db.execute(
            'SELECT COUNT(*) as cnt FROM error_book WHERE user_id = ? AND mastered = 1',
            (session['user_id'],)
        ).fetchone()['cnt']

        agg = db.execute('''
            SELECT SUM(correct_count) as total_correct,
                   SUM(correct_count + wrong_count) as total_attempts
            FROM error_book WHERE user_id = ?
        ''', (session['user_id'],)).fetchone()

        accuracy_rate = 0
        if agg['total_attempts'] and agg['total_attempts'] > 0:
            accuracy_rate = round(agg['total_correct'] / agg['total_attempts'] * 100)

        by_source_rows = db.execute('''
            SELECT source_file, COUNT(*) as cnt
            FROM error_book WHERE user_id = ?
            GROUP BY source_file ORDER BY cnt DESC
        ''', (session['user_id'],)).fetchall()
        by_source = {r['source_file']: r['cnt'] for r in by_source_rows}

        return jsonify({
            'total_errors': total,
            'mastered_count': mastered,
            'accuracy_rate': accuracy_rate,
            'by_source': by_source
        })
    finally:
        db.close()


@app.route('/api/error-book/practice', methods=['POST'])
@login_required
def api_error_book_practice():
    body = request.get_json() or {}
    count = body.get('count', 50)
    count = max(1, min(count, 200))

    db = get_db()
    try:
        rows = db.execute('''
            SELECT id, question_id, source_file, question_type
            FROM error_book
            WHERE user_id = ? AND mastered = 0
            ORDER BY RANDOM() LIMIT ?
        ''', (session['user_id'], count)).fetchall()

        if not rows:
            return jsonify({'error': '没有未掌握的错题'}), 404

        all_data = load_data()
        doc_index_map = {}
        for i, doc in enumerate(all_data):
            doc_index_map[doc['filename']] = i

        questions = []
        for r in rows:
            source = r['source_file']
            doc_idx = doc_index_map.get(source)
            if doc_idx is None:
                continue
            doc = all_data[doc_idx]
            qid = r['question_id']
            for q in doc['questions']:
                if str(q.get('id')) == qid:
                    questions.append({
                        'id': q['id'],
                        'question': q['question'],
                        'question_translation': q.get('question_translation', ''),
                        'options': q['options'],
                        'option_translations': q.get('option_translations', []),
                        'answer': q.get('answer', ''),
                        'explanation': q.get('explanation', ''),
                        'introduction': q.get('introduction', ''),
                        'section': q.get('section', ''),
                        'type': q.get('type', 'single'),
                        'source': source,
                        'error_book_id': r['id']
                    })
                    break

        sources = {}
        for q in questions:
            sources[q['source']] = sources.get(q['source'], 0) + 1

        return jsonify({
            'total': len(questions),
            'sources': sources,
            'questions': questions
        })
    finally:
        db.close()


@app.route('/api/error-book/attempts', methods=['POST'])
@login_required
def api_error_book_attempts():
    body = request.get_json()
    if not body:
        return jsonify({'error': 'No data'}), 400

    error_book_id = body.get('error_book_id')
    user_answer = body.get('user_answer', '')
    is_correct = body.get('is_correct', False)

    if not error_book_id:
        return jsonify({'error': 'missing error_book_id'}), 400

    db = get_db()
    try:
        eb = db.execute(
            'SELECT id, correct_count, wrong_count FROM error_book WHERE id = ? AND user_id = ?',
            (error_book_id, session['user_id'])
        ).fetchone()
        if not eb:
            return jsonify({'error': '错题记录不存在'}), 404

        db.execute('''
            INSERT INTO error_attempts (user_id, error_book_id, user_answer, is_correct)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], error_book_id, user_answer, 1 if is_correct else 0))

        if is_correct:
            new_correct = eb['correct_count'] + 1
            mastered = 1 if new_correct >= 2 else 0
            db.execute('''
                UPDATE error_book
                SET correct_count = ?, mastered = ?
                WHERE id = ?
            ''', (new_correct, mastered, error_book_id))
        else:
            db.execute('''
                UPDATE error_book
                SET wrong_count = wrong_count + 1, correct_count = 0, mastered = 0, last_wrong_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (error_book_id,))

        db.commit()
        return jsonify({'ok': True})
    finally:
        db.close()


if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        from parser import parse_all_in_directory
        print('首次启动，正在解析Word文档...')
        results = parse_all_in_directory('.')
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f'解析完成：{len(results)} 个文件，{sum(r["question_count"] for r in results)} 题')
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
