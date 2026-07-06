import json
from pathlib import Path

root = Path(r"D:\本科\MS\CS_AIE")
selected = json.loads((root / "第二张表-CS_AIE-打勾项目抽取.json").read_text(encoding="utf-8"))
files = sorted(root.rglob("*课程介绍.md"))

school_map = {
    "Carnegie Mellon University": "CMU",
    "University of Illinois—\u200bUrbana-\u200bChampaign": "UIUC",
    "University of California—\u200bSan Diego": "UCSD",
    "Georgia Institute of Technology": "GeorgiaTech",
    "University of Michigan—\u200bAnn Arbor": "Michigan",
    "University of Maryland—\u200bCollege Park": "Maryland",
    "Stanford University": "Stanford",
    "University of California—\u200bBerkeley": "Berkeley",
    "Cornell University": "Cornell",
    "Northeastern University": "Northeastern",
    "Purdue University—\u200bWest Lafayette": "Purdue",
    "New York University": "NYU",
    "University of Southern California": "USC",
    "University of Pennsylvania": "UPenn",
    "University of California-Los Angeles": "UCLA",
    "Northwestern University": "Northwestern",
    "Columbia University": "Columbia",
    "University of California—\u200bIrvine": "UCI",
    "Duke University": "Duke",
    "Johns Hopkins University": "JHU",
    "University of California—\u200bSanta Barbara": "UCSB",
}

required_heads = [
    "## 项目概况",
    "## 修读要求",
    "## 官方课程",
    "## 官方课程描述抓手",
    "## 申请与网址速览",
    "## 官网核验",
    "## 数据来源",
]

print(f"selected_projects={len(selected)}")
print(f"course_intro_files={len(files)}")
missing = []
for item in selected:
    folder = school_map.get(item["school"])
    candidates = [p for p in files if folder and folder in p.parts]
    if not candidates:
        missing.append((item["row"], item["school"], item["program"]))
print(f"missing_project_mappings={len(missing)}")
for m in missing:
    print("MISSING", m)

print("\nfile_checks")
for p in files:
    text = p.read_text(encoding="utf-8", errors="replace")
    missing_heads = [h for h in required_heads if h not in text]
    old_target_style = any(s in text for s in ["推荐选课课表", "方向相关课程池", "代表课程/方向抓手"])
    has_full_course_signal = any(
        s in text
        for s in [
            "全部课程池",
            "完整官方",
            "官方完整",
            "完整列表",
            "全部课程",
            "课程列表",
            "全部 specialization",
            "官方全部",
            "官方课程结构 / 全部课程池",
            "官方课程结构/全部课程池",
        ]
    )
    risk = []
    if missing_heads:
        risk.append("missing_heads")
    if old_target_style:
        risk.append("old_target_style")
    if not has_full_course_signal:
        risk.append("weak_full_course_signal")
    if text.count("http") < 2:
        risk.append("few_sources")
    print(
        f"{p.relative_to(root)}\tchars={len(text)}\turls={text.count('http')}"
        f"\tfull_course_signal={has_full_course_signal}\told_target_style={old_target_style}"
        f"\tmissing_heads={missing_heads}\trisk={risk}"
    )
