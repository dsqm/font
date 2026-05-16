#!/usr/bin/env python3
"""Copy glyph outlines from ref UFOs to source UFO for glyphs with non-PUA equivalents."""

import defcon
from fontTools.pens.recordingPen import RecordingPointPen


def copy_glyph_outline(src_glyph, dst_glyph):
    dst_glyph.clearContours()
    dst_glyph.clearComponents()
    dst_glyph.width = src_glyph.width
    recorder = RecordingPointPen()
    src_glyph.drawPoints(recorder)
    recorder.replay(dst_glyph.getPointPen())


def build_unicode_map(ufo_path):
    font = defcon.Font(ufo_path)
    umap = {}
    for glyph in font:
        for uni in glyph.unicodes:
            umap[uni] = glyph.name
    return font, umap


def main():
    mapping_path = "dist/PUA 映射.txt"
    src_ufo_path = "sources/masters/ChaiSans-Regular.ufo"
    ref_ufos = [
        "ref/Source Han Sans SC VF-Regular.ufo",
        "ref/PlangothicP1-Regular.ufo",
        "ref/PlangothicP2-Regular.ufo",
    ]

    # Parse the mapping file for rows with a non-PUA equivalent (4th column)
    entries = []
    with open(mapping_path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 4 and parts[3].strip():
                pua_hex = parts[1].strip()
                glyph_name = parts[2].strip()
                equiv_char = parts[3].strip()
                entries.append((int(pua_hex[2:], 16), glyph_name, equiv_char, ord(equiv_char)))

    print(f"Found {len(entries)} entries with non-PUA equivalents")

    # Load all ref UFOs
    ref_fonts = []
    for path in ref_ufos:
        print(f"Loading {path}...")
        font, umap = build_unicode_map(path)
        ref_fonts.append((path.split("/")[-1], font, umap))

    print("Loading source UFO...")
    src_font = defcon.Font(src_ufo_path)

    copied = []
    skipped_has_content = []
    not_found = []

    for pua_cp, glyph_name, equiv_char, equiv_cp in entries:
        # Find in ref UFOs in priority order
        ref_glyph = None
        source_label = None
        for ufo_name, font, umap in ref_fonts:
            ref_name = umap.get(equiv_cp)
            if ref_name:
                ref_glyph = font[ref_name]
                source_label = f"{ufo_name}:{ref_name}"
                break

        if ref_glyph is None:
            not_found.append((glyph_name, f"U+{equiv_cp:04X}", equiv_char))
            continue

        if glyph_name not in src_font:
            src_glyph = src_font.newGlyph(glyph_name)
            src_glyph.unicodes = [pua_cp]
        else:
            src_glyph = src_font[glyph_name]
            if len(src_glyph) > 0 or len(src_glyph.components) > 0:
                skipped_has_content.append((glyph_name, f"U+{pua_cp:04X}"))
                continue

        copy_glyph_outline(ref_glyph, src_glyph)
        copied.append((glyph_name, f"U+{pua_cp:04X}", f"U+{equiv_cp:04X}", source_label))

    print("\nSaving source UFO...")
    src_font.save()

    print(f"\n=== Copied ({len(copied)}) ===")
    for name, pua, equiv, src in copied:
        print(f"  {name} ({pua}) <- {equiv} [{src}]")

    print(f"\n=== Skipped: glyph already has content ({len(skipped_has_content)}) ===")
    for name, pua in skipped_has_content:
        print(f"  {name} ({pua})")

    if not_found:
        print(f"\n=== Not found in any ref UFO ({len(not_found)}) ===")
        for name, equiv, char in not_found:
            print(f"  {name} <- {equiv} ({char})")


if __name__ == "__main__":
    main()
