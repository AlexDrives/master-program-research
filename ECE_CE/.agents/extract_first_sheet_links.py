import json
import pathlib
import re
import xml.etree.ElementTree as ET
import zipfile

XLSX = pathlib.Path(r"D:\本科\MS\Alex刘俊豪-2027 快捷-ECE&CE&CS&AIE初选.xlsx")
OUT_JSON = pathlib.Path(r"D:\本科\MS\.agents\first_sheet_links.json")
OUT_TSV = pathlib.Path(r"D:\本科\MS\.agents\first_sheet_links.tsv")

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def col_name(ref: str) -> str:
    return re.match(r"[A-Z]+", ref).group(0)


def load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    path = "xl/sharedStrings.xml"
    if path not in zf.namelist():
        return []
    root = ET.fromstring(zf.read(path))
    return ["".join(t.text or "" for t in si.iter("{%s}t" % NS["a"])) for si in root]


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


def load_rels(zf: zipfile.ZipFile, path: str) -> dict[str, str]:
    if path not in zf.namelist():
        return {}
    root = ET.fromstring(zf.read(path))
    return {rel.attrib["Id"]: rel.attrib["Target"] for rel in root}


with zipfile.ZipFile(XLSX) as zf:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    sheets = wb.find("a:sheets", NS)
    wb_rels = load_rels(zf, "xl/_rels/workbook.xml.rels")
    first = list(sheets)[0]
    sheet_target = "xl/" + wb_rels[first.attrib["{%s}id" % NS["r"]]]
    sheet_rels_path = "xl/worksheets/_rels/" + pathlib.PurePosixPath(sheet_target).name + ".rels"
    sheet_rels = load_rels(zf, sheet_rels_path)
    shared = load_shared_strings(zf)
    sheet = ET.fromstring(zf.read(sheet_target))

    hyperlink_by_ref = {}
    hyperlinks = sheet.find("a:hyperlinks", NS)
    if hyperlinks is not None:
        for link in hyperlinks:
            ref = link.attrib.get("ref", "")
            rid = link.attrib.get("{%s}id" % NS["r"])
            target = sheet_rels.get(rid, link.attrib.get("location", "")) if rid else link.attrib.get("location", "")
            for part in ref.split():
                hyperlink_by_ref[part] = target

    rows = sheet.find("a:sheetData", NS)
    raw_rows = []
    for row in rows:
        rid = int(row.attrib["r"])
        cells = {}
        links = {}
        for cell in row:
            ref = cell.attrib.get("r")
            col = col_name(ref)
            val = cell_value(cell, shared).strip()
            if val:
                cells[col] = val
            if ref in hyperlink_by_ref:
                links[col] = hyperlink_by_ref[ref]
        if cells or links:
            raw_rows.append({"row": rid, "cells": cells, "links": links})

    OUT_JSON.write_text(json.dumps(raw_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
        f.write("row\tuniversity\tprogram\tproject_url\tcourse_url\thighlight\n")
        for item in raw_rows:
            r = item["row"]
            cells = item["cells"]
            links = item["links"]
            if r < 3:
                continue
            university = cells.get("D", "")
            program = cells.get("I", "")
            highlight = cells.get("AF", "")
            if university or program:
                f.write(
                    f"{r}\t{university}\t{program}\t"
                    f"{links.get('I','')}\t{links.get('AD','') or links.get('AE','') or links.get('AF','')}\t"
                    f"{highlight.replace(chr(9), ' ')}\n"
                )

print(OUT_JSON)
print(OUT_TSV)
