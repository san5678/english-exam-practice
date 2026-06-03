import json
import os
import sys
import random
from flask import Flask, jsonify, render_template, request, send_from_directory

sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

DATA_FILE = 'questions.json'


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/documents')
def api_documents():
    data = load_data()
    result = []
    for i, doc in enumerate(data):
        result.append({
            'index': i,
            'title': doc['filename'].replace('.docx', ''),
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

    if not question_list:
        data = load_data()
        if paper_id < 0 or paper_id >= len(data):
            return jsonify({'error': 'Paper not found'}), 404
        question_list = data[paper_id]['questions']

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


if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        from parser import parse_all_in_directory
        print('首次启动，正在解析Word文档...')
        results = parse_all_in_directory('.')
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f'解析完成：{len(results)} 个文件，{sum(r["question_count"] for r in results)} 题')
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
