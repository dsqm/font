import csv
import os
import xml.etree.ElementTree as ET

ufo_glyphs_dir = "sources/masters/ChaiSans-Regular.ufo/glyphs"

# Collect all Unicode code points present in the UFO
ufo_codepoints: set[str] = set()
for filename in os.listdir(ufo_glyphs_dir):
    if not filename.endswith(".glif"):
        continue
    tree = ET.parse(os.path.join(ufo_glyphs_dir, filename))
    for uni in tree.getroot().findall("unicode"):
        ufo_codepoints.add(uni.attrib["hex"].upper())

# Check each chaipua codepoint from the CSV
missing: list[tuple[int, str]] = []
with open("yuniversus-chaipua.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for lineno, row in enumerate(reader, start=2):
        chaipua = row["chaipua"].strip()
        if not chaipua:
            continue
        if chaipua.upper() not in ufo_codepoints:
            missing.append((lineno, chaipua))

if missing:
    print(f"缺失 {len(missing)} 个码位：")
    for lineno, cp in missing:
        print(f"  第 {lineno} 行: U+{cp.upper()}")
else:
    print("所有 chaipua 码位均已在 UFO 中找到。")
