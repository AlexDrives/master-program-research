import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(r"D:\本科\MS")
out_dir = root / "CS_AIE"
book = root / "Alex刘俊豪-2027 快捷-ECE&CE&CS&AIE初选.xlsx"
ns = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def col_to_num(col: str) -> int:
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    return n

with zipfile.ZipFile(book) as z:
    names = z.namelist()
    shared = []
    if "xl/sharedStrings.xml" in names:
        shared_root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in shared_root.findall("a:si", ns):
            shared.append("".join(t.text or "" for t in si.findall(".//a:t", ns)))

    sheet = "xl/worksheets/sheet2.xml"
    sheet_root = ET.fromstring(z.read(sheet))

    rels = {}
    relpath = "xl/worksheets/_rels/sheet2.xml.rels"
    if relpath in names:
        rel_root = ET.fromstring(z.read(relpath))
        for rel in rel_root:
            rels[rel.attrib.get("Id")] = rel.attrib.get("Target")

    hyperlinks = {}
    for link in sheet_root.findall(".//a:hyperlink", ns):
        ref = link.attrib.get("ref")
        rid = link.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        hyperlinks[ref] = rels.get(rid, link.attrib.get("location"))

    def cell_value(cell):
        cell_type = cell.attrib.get("t")
        value = cell.find("a:v", ns)
        inline = cell.find("a:is", ns)
        if cell_type == "s" and value is not None:
            return shared[int(value.text)]
        if cell_type == "inlineStr" and inline is not None:
            return "".join(t.text or "" for t in inline.findall(".//a:t", ns))
        return value.text if value is not None else ""

    rows = []
    for row in sheet_root.findall(".//a:sheetData/a:row", ns):
        row_num = int(row.attrib["r"])
        cells = {}
        for cell in row.findall("a:c", ns):
            ref = cell.attrib["r"]
            col = re.match(r"([A-Z]+)", ref).group(1)
            cells[col] = cell_value(cell)
            if ref in hyperlinks:
                cells[f"{col}_url"] = hyperlinks[ref]
        rows.append((row_num, cells))

headers = {}
for row_num, cells in rows[:3]:
    for col, value in cells.items():
        if not col.endswith("_url") and value:
            headers.setdefault(col, value)

selected = []
for row_num, cells in rows:
    marker = str(cells.get("B", "")).strip()
    if "√" in marker or "✓" in marker or "选" in marker or marker.lower() in {"x", "yes", "y"}:
        selected.append(
            {
                "row": row_num,
                "marker": marker,
                "category": cells.get("C", ""),
                "school": cells.get("D", ""),
                "rank": cells.get("F", ""),
                "major_rank": cells.get("G", ""),
                "college": cells.get("H", ""),
                "program": cells.get("I", ""),
                "program_length": cells.get("J", ""),
                "concentrations": cells.get("K", ""),
                "curriculum": cells.get("L", ""),
                "curriculum_url": cells.get("L_url", ""),
                "program_home": cells.get("N", ""),
                "program_home_url": cells.get("N_url", ""),
                "admission": cells.get("O", ""),
                "admission_url": cells.get("O_url", ""),
                "deadline": cells.get("P", ""),
                "deadline_url": cells.get("P_url", ""),
                "highlights": cells.get("AF", ""),
                "remarks": cells.get("AG", ""),
                "remarks_url": cells.get("AG_url", ""),
            }
        )

out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "第二张表-CS_AIE-打勾项目抽取.json").write_text(
    json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8"
)

print(f"sheet=sheet2 selected_count={len(selected)}")
for item in selected:
    url = item["curriculum_url"] or item["curriculum"] or item["program_home_url"] or item["program_home"]
    print(f"{item['row']}\t{item['marker']}\t{item['school']}\t{item['program']}\t{url}")
