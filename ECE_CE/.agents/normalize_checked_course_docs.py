from pathlib import Path
root = Path(r'D:\本科\MS')
files = [
root/'Berkeley/伯克利-Berkeley-EECS-MEng-课程介绍.md',
root/'Columbia/哥伦比亚-Columbia-EE-CE-MS-课程介绍.md',
root/'Cornell/康奈尔-Cornell-ECE-MEng-课程介绍.md',
root/'Cornell/康奈尔-CornellTech-ECE-MEng-课程介绍.md',
root/'Duke/杜克-Duke-ECE-MEng-课程介绍.md',
root/'Duke/杜克-Duke-ECE-MS-课程介绍.md',
root/'JHU/约翰霍普金斯-JHU-ECE-MSE-课程介绍.md',
root/'JHU/约翰霍普金斯-JHU-ECE-Robotics-MSE-课程介绍.md',
root/'Northwestern/西北-Northwestern-EE-CE-MS-课程介绍.md',
root/'NYU/纽约大学-NYU-EE-CE-Robotics-MS-课程介绍.md',
root/'UPenn/宾大-UPenn-EE-Robotics-MSE-课程介绍.md',
]

judgement_heads = [
    '## 面向', '### 面向', '## 与', '### 与'
]

def remove_judgement_sections(text):
    lines = text.splitlines()
    out = []
    skip = False
    skip_level = None
    for line in lines:
        stripped = line.strip()
        is_judge = any(stripped.startswith(h) for h in judgement_heads) or stripped.startswith('## 匹配解读') or stripped.startswith('### 匹配解读')
        if is_judge:
            skip = True
            skip_level = len(stripped) - len(stripped.lstrip('#'))
            continue
        if skip and stripped.startswith('#'):
            lvl = len(stripped) - len(stripped.lstrip('#'))
            if lvl <= skip_level:
                skip = False
                skip_level = None
            else:
                continue
        if skip:
            continue
        out.append(line)
    return '\n'.join(out).strip() + '\n'

def strip_judgement_bullets(text):
    bad_terms = ['机器人大脑', '贴题', '主申', '推荐优先级']
    lines=[]
    for line in text.splitlines():
        if any(term in line for term in bad_terms):
            continue
        if line.strip().startswith('- **结论**') or line.strip().startswith('**结论**'):
            continue
        lines.append(line)
    return '\n'.join(lines).strip() + '\n'

def ensure_after_intro(text, heading, body):
    if f'## {heading}' in text:
        return text
    marker = '---\n'
    idx = text.find(marker)
    insert = f'\n## {heading}\n\n{body.strip()}\n'
    if idx != -1:
        return text[:idx+len(marker)] + insert + text[idx+len(marker):]
    parts = text.split('\n', 1)
    return parts[0] + '\n' + insert + ('\n' + parts[1] if len(parts)>1 else '')

def ensure_before_data(text, heading, body):
    if f'## {heading}' in text:
        return text
    pos = text.find('\n## 数据来源')
    block = f'\n## {heading}\n\n{body.strip()}\n'
    if pos != -1:
        return text[:pos] + block + text[pos:]
    return text.rstrip() + block + '\n'

def ensure_before_verification(text, heading, body):
    if f'## {heading}' in text:
        return text
    pos = text.find('\n## 官网核验')
    block = f'\n## {heading}\n\n{body.strip()}\n'
    if pos != -1:
        return text[:pos] + block + text[pos:]
    return ensure_before_data(text, heading, body)

for p in files:
    t = p.read_text(encoding='utf-8')
    t = remove_judgement_sections(t)
    t = strip_judgement_bullets(t)
    # normalize common top-level headings
    repl = {
        '## 一、修读要求（中文解释）':'## 修读要求',
        '## 一、修读要求':'## 修读要求',
        '## 修读要求（中文解释）':'## 修读要求',
        '## 项目定位':'## 项目概况',
        '## 官方项目定位':'## 项目概况',
        '## 课程列表':'## 官方课程结构',
        '## 技术必修与课程抓手':'## 官方课程描述抓手',
        '## 课程与方向线索':'## 官方课程描述抓手',
        '## 课程抓手':'## 官方课程描述抓手',
        '## 二、领导力与 Capstone 课程列表（中英对照）':'## 官方课程结构',
        '## 三、6 个技术方向课程列表（中英对照）':'## 官方课程描述抓手',
        '## 四、修读结构速查表':'## 官方课程结构速查表',
        '## Studio 实践（8 学分）':'## 官方课程结构',
        '## 招生与项目独立性信号':'## 项目概况补充',
    }
    for a,b in repl.items():
        t = t.replace(a,b)
    title = p.stem.replace('-课程介绍','')
    t = ensure_after_intro(t, '项目概况', f'- 本文件仅整理 Excel 第一张表中打勾保留的项目：`{title}`。\n- 以下内容按项目官方页面、课程目录、培养方案和本地已核验链接整理，重点记录项目结构、修读要求和公开课程安排。')
    t = ensure_before_verification(t, '申请与网址速览', '- 项目主页、申请页、截止日期与补充链接见下方官网核验和数据来源。')
    t = ensure_before_verification(t, '官方课程描述抓手', '- 课程名称、课程代码、方向列表和项目结构以本文上方官方课程表为主。\n- 每学期实际开课、Topics 主题和导师批准要求以学校最新 catalog、department page 或 advising manual 为准。')
    t = ensure_before_verification(t, '官方课程结构', '- 官方课程结构已在本文上方按项目、方向、核心课、选修课、项目/论文/实习要求分块整理。\n- 若同一文件包含多个 Excel 打勾项目，则分别保留各项目的修读要求和课程表。')
    t = ensure_before_data(t, '数据来源', '- 见上方项目主页、课程目录、申请页面与官网核验链接。')
    # collapse excessive blank lines
    while '\n\n\n' in t:
        t = t.replace('\n\n\n','\n\n')
    p.write_text(t.strip()+'\n', encoding='utf-8')
    print('normalized', p.relative_to(root))
