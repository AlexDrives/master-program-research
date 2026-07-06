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
        shared.append(
            "".join(t.text or "" for t in si.iter("{%s}t" % NS["a"]))
        )
    return shared


def main(path: str) -> None:
    with zipfile.ZipFile(path) as zf:
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
        sheets = []
        for s in workbook.find("a:sheets", NS):
            rid = s.attrib["{%s}id" % NS["r"]]
            sheets.append((s.attrib["name"], rel_map[rid]))
        print("SHEETS=" + json.dumps(sheets, ensure_ascii=False))

        shared = load_shared_strings(zf)
        first_name, target = sheets[0]
        if not target.startswith("xl/"):
            target = "xl/" + target
        sheet = ET.fromstring(zf.read(target))
        print("TITLE=" + first_name)

        for row in sheet.findall(".//a:sheetData/a:row", NS)[:160]:
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
            print(json.dumps(values, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
