import pathlib
import xml.etree.ElementTree as ET
import zipfile

XLSX = pathlib.Path(r"D:\本科\MS\Alex刘俊豪-2027 快捷-ECE&CE&CS&AIE初选.xlsx")
NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    path = "xl/sharedStrings.xml"
    if path not in zf.namelist():
        return []
    root = ET.fromstring(zf.read(path))
    out = []
    for si in root:
        out.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["a"])))
    return out


def cell_value(cell: ET.Element, shared: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    value = cell.find("a:v", NS)
    if cell_type == "s" and value is not None:
        return shared[int(value.text)]
    if value is not None:
        return value.text or ""
    inline = cell.find("a:is", NS)
    if inline is not None:
        return "".join(t.text or "" for t in inline.iter("{%s}t" % NS["a"]))
    return ""


with zipfile.ZipFile(XLSX) as zf:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    sheets = wb.find("a:sheets", NS)
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    first = list(sheets)[0]
    target = "xl/" + rel_map[first.attrib["{%s}id" % NS["r"]]]
    shared = load_shared_strings(zf)
    sheet = ET.fromstring(zf.read(target))
    rows = sheet.find("a:sheetData", NS)

    print(f"sheet_name\t{first.attrib.get('name')}")
    print("row\tuniversity\tdegree_program\thighlight")
    for row in list(rows)[2:120]:
        rid = row.attrib["r"]
        data = {cell.attrib.get("r"): cell_value(cell, shared) for cell in row}
        university = data.get("D" + rid, "").strip()
        degree_program = data.get("I" + rid, "").strip()
        highlight = data.get("AF" + rid, "").strip()
        if university:
            print(f"{rid}\t{university}\t{degree_program}\t{highlight}")
