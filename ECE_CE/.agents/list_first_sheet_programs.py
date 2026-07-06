import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile


NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def col_index(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref).group(0)
    value = 0
    for ch in letters:
        value = value * 26 + ord(ch) - 64
    return value


def load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    shared = []
    for si in root.findall("a:si", NS):
        shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["a"])))
    return shared


def read_first_sheet(path: str) -> list[list[str | None]]:
    with zipfile.ZipFile(path) as zf:
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
        first_sheet = next(iter(workbook.find("a:sheets", NS)))
        rid = first_sheet.attrib["{%s}id" % NS["r"]]
        target = rel_map[rid]
        if not target.startswith("xl/"):
            target = "xl/" + target
        sheet = ET.fromstring(zf.read(target))
        shared = load_shared_strings(zf)

        rows = []
        for row in sheet.findall(".//a:sheetData/a:row", NS):
            values = []
            current_col = 1
            for cell in row.findall("a:c", NS):
                ref = cell.attrib.get("r", "A1")
                col = col_index(ref)
                while current_col < col:
                    values.append(None)
                    current_col += 1

                cell_type = cell.attrib.get("t")
                v = cell.find("a:v", NS)
                is_node = cell.find("a:is", NS)
                text = None
                if cell_type == "s" and v is not None and v.text is not None:
                    text = shared[int(v.text)]
                elif cell_type == "inlineStr" and is_node is not None:
                    text = "".join(
                        t.text or "" for t in is_node.iter("{%s}t" % NS["a"])
                    )
                elif v is not None:
                    text = v.text
                values.append(text)
                current_col += 1
            rows.append(values)
        return rows


def main(path: str) -> None:
    rows = read_first_sheet(path)
    items = []
    for row in rows[2:]:
        university = row[3] if len(row) > 3 else None
        degree = row[8] if len(row) > 8 else None
        website = row[13] if len(row) > 13 else None
        category = row[2] if len(row) > 2 else None
        if not university:
            continue
        items.append(
            {
                "category": category,
                "university": university.strip() if isinstance(university, str) else university,
                "degree": degree.strip() if isinstance(degree, str) else degree,
                "website": website.strip() if isinstance(website, str) else website,
            }
        )
    print(json.dumps(items, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
