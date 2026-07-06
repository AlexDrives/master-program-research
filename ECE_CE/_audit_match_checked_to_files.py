import json
from pathlib import Path

root = Path(r"D:\本科\MS")
selected = json.loads((root / "当前打勾项目抽取.json").read_text(encoding="utf-8"))
course_files = sorted(root.rglob("*课程介绍.md"))

school_map = {
    "Duke University": "Duke",
    "Johns Hopkins University": "JHU",
    "Northwestern University": "Northwestern",
    "University of Pennsylvania": "UPenn",
    "Cornell University": "Cornell",
    "Columbia University": "Columbia",
    "University of California--Berkeley": "Berkeley",
    "Rice University": "Rice",
    "University of California--Los Angeles": "UCLA",
    "Carnegie Mellon University": "CMU",
    "University of Michigan--Ann Arbor": "Michigan",
    "University of Southern California": "USC",
    "University of California--San Diego": "UCSD",
    "New York University": "NYU",
    "University of California--Davis": "UCD",
    "University of California--Irvine": "UCI",
    "University of Illinois--Urbana-Champaign": "UIUC",
    "Boston University": "BU",
    "University of Washington": "UWashington",
}

def normalize_url(url):
    return (url or "").strip().rstrip("/")

def likely_files(item):
    folder = school_map.get(item["school"])
    files = [p for p in course_files if folder and folder in p.parts]
    program = item["program"].lower()
    if folder == "Duke" and "meng" in program:
        files = [p for p in files if "MEng" in p.name]
    elif folder == "Duke" and "science" in program:
        files = [p for p in files if "MS" in p.name and "MEng" not in p.name]
    elif folder == "JHU" and "robotics" in program.lower():
        files = [p for p in files if "Robotics" in p.name]
    elif folder == "JHU":
        files = [p for p in files if "Robotics" not in p.name]
    elif folder == "Cornell" and "tech" in program:
        files = [p for p in files if "Tech" in p.name]
    elif folder == "Cornell":
        files = [p for p in files if "Tech" not in p.name]
    elif folder == "NYU" and "mechatronics" in program:
        files = [p for p in files if "Mechatronics" in p.name]
    elif folder == "NYU":
        files = [p for p in files if "EE-CE" in p.name]
    elif folder == "USC" and program.strip().startswith("ms in computer engineering"):
        files = [p for p in files if "USC-CE-MS" in p.name]
    elif folder == "USC":
        files = [p for p in files if "ECE-CE" in p.name]
    return files

rows = []
for item in selected:
    files = likely_files(item)
    urls = []
    for key in ["curriculum_url", "curriculum", "program_home_url", "program_home", "remarks_url"]:
        u = item.get(key, "")
        if isinstance(u, str) and u.startswith("http"):
            urls.append(normalize_url(u))
    hits = []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        found = []
        for u in urls:
            candidates = {u, u.rstrip("/")}
            if "#text" in u:
                candidates.add(u.replace("#text", ""))
            if "#requirementstext" in u:
                candidates.add(u.replace("#requirementstext", ""))
            if any(c in text for c in candidates):
                found.append(u)
        hits.append((f.relative_to(root).as_posix(), len(found), len(urls), found, urls))
    rows.append({**item, "files": hits})

print("| row | school | program | local file(s) | URL match | missing given URLs |")
print("|---:|---|---|---|---:|---|")
for row in rows:
    if not row["files"]:
        print(f"| {row['row']} | {row['school']} | {row['program']} | MISSING | 0/0 | no mapped file |")
        continue
    file_bits = []
    match = 0
    total = 0
    missing = []
    for fname, found_n, total_n, found, urls in row["files"]:
        file_bits.append(fname)
        match += found_n
        total += total_n
        missing.extend([u for u in urls if u not in found])
    print(f"| {row['row']} | {row['school']} | {row['program']} | {'<br>'.join(file_bits)} | {match}/{total} | {'<br>'.join(missing) if missing else ''} |")
