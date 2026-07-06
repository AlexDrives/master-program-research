from pathlib import Path

root = Path(r"D:\本科\MS\CS_AIE")
schools = [
    "Berkeley",
    "CMU",
    "Columbia",
    "Cornell",
    "Duke",
    "GeorgiaTech",
    "JHU",
    "Maryland",
    "Michigan",
    "Northeastern",
    "Northwestern",
    "NYU",
    "Purdue",
    "Stanford",
    "UCI",
    "UCLA",
    "UCSB",
    "UCSD",
    "UIUC",
    "UPenn",
    "USC",
]
for school in schools:
    (root / school).mkdir(parents=True, exist_ok=True)
print(f"created_or_existing={len(schools)}")
