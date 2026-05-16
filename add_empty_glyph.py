#!/usr/bin/env python3
"""
Read PUA codepoints from dist/PUA 映射.txt, check both UFO projects,
and create missing glif files while updating contents.plist and lib.plist.
"""

import plistlib
from pathlib import Path

SOURCES_DIR = Path("sources/masters")
MAPPING_FILE = Path("dist/PUA 映射.txt")

UFO_DIRS = [
    SOURCES_DIR / "ChaiSans-Regular.ufo",
    SOURCES_DIR / "ChaiSerif-Regular.ufo",
]


def parse_mapping(filepath):
    entries = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                hex_val = parts[1].strip().lstrip("U+")
                glyph_name = parts[2].strip()
                entries.append((hex_val.upper(), glyph_name))
    return entries


def read_plist(filepath):
    with open(filepath, "rb") as f:
        return plistlib.load(f)


def write_plist(filepath, data):
    with open(filepath, "wb") as f:
        plistlib.dump(data, f, fmt=plistlib.FMT_XML, sort_keys=True)


def make_glif(glyph_name, hex_val, is_serif):
    advance = '<advance height="1880" width="1000"/>' if is_serif else '<advance width="1000"/>'
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<glyph name="{glyph_name}" format="2">\n'
        f'\t<unicode hex="{hex_val}"/>\n'
        f'\t{advance}\n'
        '\t<outline/>\n'
        '</glyph>\n'
    )


def process_ufo(ufo_dir, entries):
    is_serif = "Serif" in ufo_dir.name
    glyphs_dir = ufo_dir / "glyphs"
    contents_path = glyphs_dir / "contents.plist"
    lib_path = ufo_dir / "lib.plist"

    contents = read_plist(contents_path)
    lib = read_plist(lib_path)
    glyph_order = lib.get("public.glyphOrder", [])
    glyph_order_set = set(glyph_order)

    added = []
    for hex_val, glyph_name in entries:
        if glyph_name in contents:
            continue

        filename = f"{glyph_name}.glif"
        glif_path = glyphs_dir / filename
        glif_path.write_text(make_glif(glyph_name, hex_val, is_serif), encoding="utf-8")

        contents[glyph_name] = filename

        if glyph_name not in glyph_order_set:
            glyph_order.append(glyph_name)
            glyph_order_set.add(glyph_name)

        added.append((hex_val, glyph_name))

    if added:
        lib["public.glyphOrder"] = glyph_order
        write_plist(contents_path, contents)
        write_plist(lib_path, lib)

    return added


def main():
    entries = parse_mapping(MAPPING_FILE)
    print(f"Loaded {len(entries)} PUA entries from mapping file.\n")

    for ufo_dir in UFO_DIRS:
        print(f"Processing {ufo_dir.name}...")
        added = process_ufo(ufo_dir, entries)
        if added:
            print(f"  Added {len(added)} missing glyphs:")
            for hex_val, name in added:
                print(f"    U+{hex_val}  {name}")
        else:
            print("  All glyphs already present.")
        print()


if __name__ == "__main__":
    main()
