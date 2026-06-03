import re
import json
import os
from docx import Document


def split_en_cn(text):
    m = re.match(r'^(.+?)（(.+)）\s*$', text)
    if m:
        en_part, cn_part = m.group(1).strip(), m.group(2).strip()
        if re.search(r'[\u4e00-\u9fff]', cn_part):
            return en_part, cn_part

    m = re.match(r'^(.+?)【(.+)】\s*$', text)
    if m:
        en_part, cn_part = m.group(1).strip(), m.group(2).strip()
        if re.search(r'[\u4e00-\u9fff]', cn_part):
            return en_part, cn_part

    m = re.match(r'^(.+?)『(.+)』\s*$', text)
    if m:
        en_part, cn_part = m.group(1).strip(), m.group(2).strip()
        if re.search(r'[\u4e00-\u9fff]', cn_part):
            return en_part, cn_part

    first_cn = None
    for i, ch in enumerate(text):
        if '\u4e00' <= ch <= '\u9fff':
            first_cn = i
            break

    if first_cn is None:
        return text, ''

    split_at = first_cn
    while split_at > 0 and text[split_at - 1] in ' \u3000\t':
        split_at -= 1

    en_part = text[:split_at].strip()
    cn_part = text[split_at:].strip()

    if not en_part:
        return text, ''

    if re.search(r'[\u4e00-\u9fff]', cn_part):
        return en_part, cn_part
    return text, ''


def split_multi_option_line(text):
    m = re.split(r'\s+([B-D])\s+', text, maxsplit=1)
    if len(m) < 3:
        return None
    if not re.match(r'^[A-D]$', m[1]):
        return None
    first_text = m[0].strip()
    second_text = m[2].strip()
    if not first_text or not second_text:
        return None
    return [split_en_cn(first_text), split_en_cn(second_text)]


def detect_format(paragraphs):
    for p in paragraphs[:20]:
        text = p.text.strip()
        if re.match(r'^\d+\.\s*$', text) or re.match(r'^\d+$', text):
            return 'structured'
        if text.startswith('原题：') or text.startswith('原文：'):
            return 'structured'
    return 'simple'


def parse_simple_format(paragraphs):
    questions = []
    current_q = None
    mode = None
    section_title = ''
    introduction_lines = []
    in_intro = True

    i = 0
    while i < len(paragraphs):
        text = paragraphs[i].text.strip()
        if not text:
            i += 1
            continue

        q_match = re.match(r'^(\d+)\.\s*(?:\([^)]*\))?\s*(.+)', text)
        option_match = re.match(r'^([A-D])[.\s、：:]+(.+)', text)
        answer_match = re.match(r'^答案[：:]\s*(.+)', text)
        translation_match = re.match(r'^(?:中文)?翻译[：:]?\s*(.+)', text)
        analysis_match = re.match(r'^(?:解析|作答理由|详细理由)[：:]?\s*(.+)', text)
        combined_answer_match = re.match(r'^答案[：:]\s*([A-D]+)\s*理由[：:]\s*(.+)', text)

        if q_match and (i + 1 < len(paragraphs) and re.match(r'^[A-D][.\s、：:]', paragraphs[i + 1].text.strip())):
            if current_q and current_q.get('question'):
                current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
                questions.append(current_q)
                introduction_lines = []
            in_intro = False
            current_q = {
                'id': int(q_match.group(1)),
                'question': q_match.group(2).strip(),
                'options': [],
                'option_translations': [],
                'question_translation': '',
                'answer': '',
                'explanation': '',
                'introduction': '',
                'section': section_title
            }
            mode = 'options'
            i += 1
            continue

        if option_match and current_q and mode == 'options':
            opt_text = option_match.group(2).strip()
            multi = split_multi_option_line(opt_text)
            if multi:
                for en, cn in multi:
                    current_q['options'].append(en or opt_text)
                    current_q['option_translations'].append(cn)
            else:
                opt_en, opt_cn = split_en_cn(opt_text)
                current_q['options'].append(opt_en or opt_text)
                current_q['option_translations'].append(opt_cn)
            if len(current_q['options']) >= 4:
                mode = None
            i += 1
            continue

        combined_ans = re.match(r'^答案[：:]\s*([A-D]+)\s*(?:理由[：:]?\s*(.+))?\s*$', text)
        if combined_ans and current_q:
            current_q['answer'] = combined_ans.group(1).strip()
            if combined_ans.group(2):
                current_q['explanation'] = combined_ans.group(2).strip()
            i += 1
            continue

        if answer_match and current_q:
            current_q['answer'] = answer_match.group(1).strip()
            i += 1
            continue

        if combined_answer_match and current_q:
            current_q['answer'] = combined_answer_match.group(1).strip()
            current_q['explanation'] = combined_answer_match.group(2).strip()
            i += 1
            continue

        if translation_match and current_q:
            current_q['question_translation'] = translation_match.group(1).strip()
            i += 1
            continue

        if analysis_match and current_q:
            current_q['explanation'] = analysis_match.group(1).strip()
            if current_q['options'] and mode is None:
                current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
                questions.append(current_q)
                introduction_lines = []
                current_q = None
                mode = None
            i += 1
            continue

        if in_intro and not q_match:
            section_header = re.match(r'^(?:一|二|三|四|五)[、.，,]\s*.+', text)
            if section_header:
                section_title = text
                introduction_lines = []
            elif not re.match(r'^\d+\.', text) and text:
                introduction_lines.append(text)
            i += 1
            continue

        i += 1

    if current_q and current_q.get('question'):
        current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
        questions.append(current_q)

    return questions


def parse_structured_format(paragraphs):
    questions = []
    current_q = None
    section_title = ''
    introduction_lines = []
    in_intro = True
    mode = None

    i = 0
    while i < len(paragraphs):
        text = paragraphs[i].text.strip()
        if not text:
            i += 1
            continue

        q_number_match = re.match(r'^(\d+)[.)]?\s*$', text)
        combined_q = re.match(r'^(\d+)[.)]\s*(?:原文|英文)[：:]\s*(.+)', text)
        combined_q_orig = re.match(r'^(\d+)[.)]\s*(?:原题|原文|英文)[：:]\s*(.+)', text)
        fw_combined_q = re.match(r'^（(\d+)）(?:英文|原文)[：:]\s*(.+)', text)
        section_header = re.match(r'^(?:一|二|三|四|五)[、.，,]\s*.+', text)

        # Handle combined number + prefix: "51.原文：xxx" or "51.英文：xxx"
        if combined_q:
            if current_q and current_q.get('question'):
                if 'question_translation' not in current_q:
                    current_q['question_translation'] = ''
                if 'explanation' not in current_q:
                    current_q['explanation'] = ''
                if 'introduction' not in current_q:
                    current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
                questions.append(current_q)
                introduction_lines = []
            in_intro = False
            current_q = {
                'id': int(combined_q.group(1)),
                'question': combined_q.group(2).strip(),
                'question_translation': '',
                'options': [],
                'option_translations': [],
                'answer': '',
                'explanation': '',
                'introduction': '',
                'section': section_title
            }
            mode = 'after_question'
            i += 1
            continue

        # Handle full-width paren number: （1）英文：xxx (reading comprehension)
        if fw_combined_q:
            if current_q and current_q.get('question'):
                if 'question_translation' not in current_q:
                    current_q['question_translation'] = ''
                if 'explanation' not in current_q:
                    current_q['explanation'] = ''
                if 'introduction' not in current_q:
                    current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
                questions.append(current_q)
                introduction_lines = []
            in_intro = False
            current_q = {
                'id': int(fw_combined_q.group(1)),
                'question': fw_combined_q.group(2).strip(),
                'question_translation': '',
                'options': [],
                'option_translations': [],
                'answer': '',
                'explanation': '',
                'introduction': '',
                'section': section_title,
                '_fw_renumber': True
            }
            mode = 'after_question'
            i += 1
            continue

        if section_header:
            section_title = text
            introduction_lines = []
            in_intro = True
            i += 1
            continue

        if q_number_match:
            if current_q and current_q.get('question'):
                if 'question_translation' not in current_q:
                    current_q['question_translation'] = ''
                if 'explanation' not in current_q:
                    current_q['explanation'] = ''
                if 'introduction' not in current_q:
                    current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
                questions.append(current_q)
                introduction_lines = []
            in_intro = False
            current_q = {
                'id': int(q_number_match.group(1)),
                'question': '',
                'question_translation': '',
                'options': [],
                'option_translations': [],
                'answer': '',
                'explanation': '',
                'introduction': '',
                'section': section_title
            }
            mode = 'question'
            i += 1
            continue

        if in_intro and current_q is None:
            introduction_lines.append(text)
            i += 1
            continue

        if current_q is None:
            i += 1
            continue

        q_orig = re.match(r'^(?:原题|原文|英文(?!原文))[：:]?\s*(.+)', text)
        q_trans = re.match(r'^(?:中文)?翻译[：:]?\s*(.+)', text)
        option_full = re.match(r'^选项[：:]\s*(.+)', text)
        option_header = re.match(r'^选项[：:]?\s*$', text)
        opt_match = re.match(r'^([A-D])[.、：:\s]+(.+)', text)
        answer_match = re.match(r'^(?:答案|参考答案)[：:]\s*([A-D]+)\s*$', text)
        answer_with_paren = re.match(r'^(?:答案|参考答案)[：:]\s*([A-D]+)[（(][^)）]*[)）]\s*$', text)
        answer_text_match = re.match(r'^(?:答案|参考答案)[：:]\s*(.+)$', text)
        reason_match = re.match(r'^(?:作答理由|详细理由|解析)[：:]?\s*(.+)', text)

        # Translation question patterns
        en_source = re.match(r'^英文原[文题][：:]\s*(.+)', text)
        cn_source = re.match(r'^中文原[文题][：:]\s*(.+)', text)
        ref_cn_trans = re.match(r'^(?:参考标准译文|参考中文译文)[：:]\s*(.+)', text)
        ref_en_trans = re.match(r'^(?:参考英文译文|参考标准英文)[：:]\s*(.+)', text)
        cn_trans_for_answer = re.match(r'^中文翻译[：:]\s*(.+)', text)
        en_trans_for_answer = re.match(r'^英文翻译[：:]\s*(.+)', text)
        trans_answer = re.match(r'^译文[：:]\s*(.+)', text)
        trans_prefix = re.match(r'^(?:中文)?翻译[：:]?\s*(.+)', text)

        # In translation mode, `译文：` serves as answer
        if trans_answer and current_q:
            current_q['answer'] = trans_answer.group(1).strip()
            if not current_q.get('translation_direction'):
                current_q['translation_direction'] = 'en2cn'
            current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
            questions.append(current_q)
            introduction_lines = []
            current_q = None
            mode = None
            i += 1
            continue

        # In translation mode, `中文翻译：` / `英文翻译：` serve as reference answers
        if mode == 'translation':
            if cn_trans_for_answer and current_q:
                current_q['answer'] = cn_trans_for_answer.group(1).strip()
                current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
                questions.append(current_q)
                introduction_lines = []
                current_q = None
                mode = None
                i += 1
                continue
            if en_trans_for_answer and current_q:
                current_q['answer'] = en_trans_for_answer.group(1).strip()
                current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
                questions.append(current_q)
                introduction_lines = []
                current_q = None
                mode = None
                i += 1
                continue
            # In translation mode, capture raw text as answer (for blank 答案：)
            if not text.startswith(('答案', '作答理由', '详细理由', '解析', '原题', '原文', '英文')):
                current_q['answer'] = text.strip()
                # Don't save yet; wait for reason or next question
                i += 1
                continue

        if en_source and current_q:
            current_q['question'] = en_source.group(1).strip()
            current_q['translation_direction'] = 'en2cn'
            mode = 'translation'
            i += 1
            continue

        if cn_source and current_q:
            current_q['question'] = cn_source.group(1).strip()
            current_q['translation_direction'] = 'cn2en'
            mode = 'translation'
            i += 1
            continue

        if ref_cn_trans and current_q and mode == 'translation':
            current_q['answer'] = ref_cn_trans.group(1).strip()
            current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
            questions.append(current_q)
            introduction_lines = []
            current_q = None
            mode = None
            i += 1
            continue

        if ref_en_trans and current_q and mode == 'translation':
            current_q['answer'] = ref_en_trans.group(1).strip()
            current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
            questions.append(current_q)
            introduction_lines = []
            current_q = None
            mode = None
            i += 1
            continue

        if q_orig:
            q_text = q_orig.group(1).strip()
            current_q['question'] = q_text
            # Detect translation direction from prefix
            cn2en_prefix = re.match(r'^汉译英[：:]\s*(.+)', q_text)
            en2cn_prefix = re.match(r'^英译汉[：:]\s*(.+)', q_text)
            if cn2en_prefix:
                current_q['question'] = cn2en_prefix.group(1).strip()
                current_q['translation_direction'] = 'cn2en'
                mode = 'translation'
            elif en2cn_prefix:
                current_q['question'] = en2cn_prefix.group(1).strip()
                current_q['translation_direction'] = 'en2cn'
                mode = 'translation'
            else:
                mode = 'after_question'
            i += 1
            continue

        if q_trans and current_q:
            current_q['question_translation'] = q_trans.group(1).strip()
            if current_q['options']:
                mode = 'after_options'
            i += 1
            continue

        if option_header:
            mode = 'options'
            i += 1
            continue

        # Handle inline options: `选项：A. xxx B. xxx`
        if option_full and current_q:
            opt_text = option_full.group(1).strip()
            # Try to match multiple options on one line
            parts = re.split(r'\s+(?=[A-D][.、：:\s])', opt_text)
            for part in parts:
                part = part.strip()
                opt_m = re.match(r'^([A-D])[.、：:\s]+(.+)', part)
                if opt_m:
                    opt_text_inner = opt_m.group(2).strip()
                    multi = split_multi_option_line(opt_text_inner)
                    if multi:
                        for en, cn in multi:
                            current_q['options'].append(en or opt_text_inner)
                            current_q['option_translations'].append(cn)
                    else:
                        opt_en, opt_cn = split_en_cn(opt_text_inner)
                        current_q['options'].append(opt_en or opt_text_inner)
                        current_q['option_translations'].append(opt_cn)
            mode = 'options'
            i += 1
            continue

        if opt_match and current_q and mode in ('options', 'after_question', 'after_options', 'question'):
            opt_text = opt_match.group(2).strip()
            multi = split_multi_option_line(opt_text)
            if multi:
                for en, cn in multi:
                    current_q['options'].append(en)
                    current_q['option_translations'].append(cn)
            else:
                opt_en, opt_cn = split_en_cn(opt_text)
                current_q['options'].append(opt_en)
                current_q['option_translations'].append(opt_cn)
            i += 1
            continue

        combined_ans2 = re.match(r'^(?:答案|参考答案)[：:]\s*([A-D]+)\s*(?:(?:详细)?理由[：:]?\s*(.+))?\s*$', text)
        if combined_ans2 and current_q:
            current_q['answer'] = combined_ans2.group(1).strip()
            if combined_ans2.group(2):
                current_q['explanation'] = combined_ans2.group(2).strip()
            i += 1
            continue

        if answer_with_paren and current_q:
            current_q['answer'] = answer_with_paren.group(1).strip()
            i += 1
            continue

        if answer_match and current_q:
            current_q['answer'] = answer_match.group(1).strip()
            i += 1
            continue

        if answer_text_match and current_q and not re.match(r'^[A-D]+$', answer_text_match.group(1).strip()):
            current_q['answer'] = answer_text_match.group(1).strip()
            i += 1
            continue

        if reason_match and current_q:
            current_q['explanation'] = reason_match.group(1).strip()
            if current_q.get('question'):
                if 'introduction' not in current_q:
                    current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
                questions.append(current_q)
                introduction_lines = []
                current_q = None
                mode = None
            i += 1
            continue

        if current_q and mode in ('question', 'after_question', 'after_options'):
            simple_q = re.match(r'^\d+\.\s*(?:\([^)]*\))?\s*(.+)', text)
            if simple_q and not current_q.get('question'):
                current_q['question'] = simple_q.group(1).strip()
                i += 1
                continue

            simple_opt = re.match(r'^([A-D])[.、:：\s]+(.+)', text)
            if simple_opt and mode in ('after_question', 'after_options'):
                opt_text = simple_opt.group(2).strip()
                multi = split_multi_option_line(opt_text)
                if multi:
                    for en, cn in multi:
                        current_q['options'].append(en or opt_text)
                        current_q['option_translations'].append(cn)
                else:
                    opt_en, opt_cn = split_en_cn(opt_text)
                    current_q['options'].append(opt_en or opt_text)
                    current_q['option_translations'].append(opt_cn)
                mode = 'options'
                i += 1
                continue

            trans = re.match(r'^(?:中文)?翻译[：:]?\s*(.+)', text)
            if trans:
                current_q['question_translation'] = trans.group(1).strip()
                i += 1
                continue

            ans_reason = re.match(r'^答案[：:]\s*([A-D]+)\s*理由[：:]\s*(.+)', text)
            if ans_reason:
                current_q['answer'] = ans_reason.group(1).strip()
                current_q['explanation'] = ans_reason.group(2).strip()
                if current_q.get('question'):
                    if 'introduction' not in current_q:
                        current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
                    questions.append(current_q)
                    introduction_lines = []
                    current_q = None
                    mode = None
                i += 1
                continue

        i += 1

    if current_q and current_q.get('question'):
        if 'introduction' not in current_q:
            current_q['introduction'] = '\n'.join(introduction_lines) if introduction_lines else ''
        questions.append(current_q)

    return questions


def parse_docx(filepath):
    doc = Document(filepath)
    paragraphs = list(doc.paragraphs)

    fmt = detect_format(paragraphs)

    if fmt == 'simple':
        questions = parse_simple_format(paragraphs)
    else:
        questions = parse_structured_format(paragraphs)

    title = paragraphs[0].text.strip() if paragraphs else os.path.basename(filepath)

    # Renumber reading comprehension questions (full-width paren numbers)
    # Find max normal ID, then renumber fw questions after it
    normal_ids = [q['id'] for q in questions if not q.get('_fw_renumber')]
    fw_questions = [q for q in questions if q.get('_fw_renumber')]
    if fw_questions and normal_ids:
        next_id = max(normal_ids) + 1
        for q in fw_questions:
            q['id'] = next_id
            next_id += 1

    for q in questions:
        if q.get('translation_direction'):
            q['type'] = 'translation'
        else:
            ans = q.get('answer', '')
            # If answer is letters only (A-D+), classify as single/multiple
            if re.match(r'^[A-D]+$', ans):
                q['type'] = 'multiple' if len(ans) > 1 else 'single'
                # Auto-generate 对/错 options for judgment questions without options
                if not q.get('options') and len(ans) == 1:
                    q['options'] = ['对 (True)', '错 (False)']
                    q['option_translations'] = ['正确', '错误']
            elif ans and (not q.get('options') or len(q.get('options', [])) <= 1):
                # Answer is text (like a translation), but not detected as translation
                q['type'] = 'translation'
                if re.search(r'[\u4e00-\u9fff]', ans):
                    q['translation_direction'] = 'en2cn'
                else:
                    q['translation_direction'] = 'cn2en'
            else:
                q['type'] = 'single'

    return {
        'title': title,
        'filename': os.path.basename(filepath),
        'question_count': len(questions),
        'questions': questions
    }


def parse_all_in_directory(directory='.'):
    results = []
    for f in sorted(os.listdir(directory)):
        if f.endswith('.docx') and not f.startswith('~$'):
            filepath = os.path.join(directory, f)
            try:
                result = parse_docx(filepath)
                results.append(result)
                print(f"[OK] {f} -> {result['question_count']} 题")
            except Exception as e:
                print(f"[FAIL] {f}: {e}")
    return results


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    results = parse_all_in_directory('.')
    with open('questions.json', 'w', encoding='utf-8') as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)
    print(f'\n共解析 {len(results)} 个文件，总计 {sum(r["question_count"] for r in results)} 题')
