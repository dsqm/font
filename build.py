#!/usr/bin/env python3
"""Build OTF, WOFF, and WOFF2 fonts from UFO sources in sources/masters/."""

import csv
import sys
from pathlib import Path
import ufo2ft
from defcon import Font
from fontTools.ttLib import TTFont


def _rename_ufo_glyphs(ufo) -> None:
    """Rename non-ASCII glyph names to uniXXXX in the in-memory UFO.

    CFF only allows latin-1 glyph names, so Chinese names must be converted
    before compiling. We operate on the in-memory defcon.Font rather than on
    disk so the source UFO is never modified.
    """
    layer = ufo.layers.defaultLayer
    rename = {}
    for glyph in layer:
        if not glyph.name.isascii():
            if glyph.unicodes:
                new_name = "uni" + "".join(f"{u:04X}" for u in glyph.unicodes)
            else:
                new_name = f"glyph{abs(hash(glyph.name)) % 100000:05d}"
            rename[glyph.name] = new_name

    for old, new in rename.items():
        layer[old].name = new  # defcon propagates the rename to the layer dict

    for glyph in layer:
        for component in glyph.components:
            if component.baseGlyph in rename:
                component.baseGlyph = rename[component.baseGlyph]

    if "public.glyphOrder" in ufo.lib:
        ufo.lib["public.glyphOrder"] = [
            rename.get(n, n) for n in ufo.lib["public.glyphOrder"]
        ]


def build(ufo_path: Path, dist_dir: Path) -> None:

    print(f"Compiling {ufo_path.name} ...")
    ufo = Font(str(ufo_path))
    _rename_ufo_glyphs(ufo)
    # useProductionNames=False: we already renamed; avoids an internal
    # save/reload that would fail on non-ASCII names.
    # optimizeCFF=0: skips subroutinization (also triggers a save internally).
    otf = ufo2ft.compileOTF(ufo, useProductionNames=False, optimizeCFF=0)
    ttf = ufo2ft.compileTTF(ufo, useProductionNames=False)

    # "Chai Sans-Regular" → "NotoSansChaiSC-Regular"
    stem = ufo_path.stem.replace(" ", "")
    dist_dir.mkdir(parents=True, exist_ok=True)

    otf_path = dist_dir / f"{stem}.otf"
    otf.save(str(otf_path))
    print(f"  → {otf_path.relative_to(Path.cwd())}")

    ttf_path = dist_dir / f"{stem}.ttf"
    ttf.save(str(ttf_path))
    print(f"  → {ttf_path.relative_to(Path.cwd())}")

    for flavor, ext in (("woff", ".woff"), ("woff2", ".woff2")):
        out = dist_dir / f"{stem}{ext}"
        f = TTFont(str(otf_path))
        f.flavor = flavor
        f.save(str(out))
        print(f"  → {out.relative_to(Path.cwd())}")


def build_yuniversus(ufo_path: Path, csv_path: Path, dist_dir: Path) -> None:
    # Load the 45 (chaipua → yuniversus) codepoint pairs from the CSV.
    # Rows where both columns are non-empty define cross-font PUA mappings.
    # if csv_path is missing, skip building
    if not csv_path.is_file():
        print(f"Warning: {csv_path} not found, skipping ChaiSansYuniversus build")
        return

    chaipua_to_yuniversus: dict[int, int] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            yuniversus = row["yuniversus"].strip()
            chaipua = row["chaipua"].strip()
            if yuniversus and chaipua:
                chaipua_to_yuniversus[int(chaipua, 16)] = ord(yuniversus)

    print(f"Building ChaiSansYuniversus from {ufo_path.name} ...")
    ufo = Font(str(ufo_path))

    # Patch font metadata.
    for attr in ("familyName", "postscriptFontName", "styleMapFamilyName",
                 "openTypeNamePreferredFamilyName"):
        if getattr(ufo.info, attr):
            setattr(ufo.info, attr, getattr(ufo.info, attr).replace("Chai Sans", "Chai Sans Yuniversus"))

    layer = ufo.layers.defaultLayer

    # Keep only glyphs that have a Yuniversus mapping, plus their component
    # dependencies (recursively) and .notdef.
    keep: set[str] = {".notdef"}
    for glyph in layer:
        if any(u in chaipua_to_yuniversus for u in glyph.unicodes):
            keep.add(glyph.name)

    def _collect_components(name: str) -> None:
        if name not in layer:
            return
        for comp in layer[name].components:
            if comp.baseGlyph not in keep:
                keep.add(comp.baseGlyph)
                _collect_components(comp.baseGlyph)

    for name in list(keep):
        _collect_components(name)

    removed = 0
    for glyph in list(layer):
        if glyph.name not in keep:
            del layer[glyph.name]
            removed += 1
    if "public.glyphOrder" in ufo.lib:
        ufo.lib["public.glyphOrder"] = [n for n in ufo.lib["public.glyphOrder"] if n in keep]

    # Append Yuniversus codepoint alongside the existing ChaiSans PUA codepoint.
    added = 0
    for glyph in layer:
        extra = [chaipua_to_yuniversus[u] for u in glyph.unicodes if u in chaipua_to_yuniversus]
        if extra:
            glyph.unicodes = extra
            added += len(extra)
    print(f"  Kept {len(keep)} glyphs (removed {removed}), added {added} Yuniversus mappings")

    _rename_ufo_glyphs(ufo)
    otf = ufo2ft.compileOTF(ufo, useProductionNames=False, optimizeCFF=0)
    ttf = ufo2ft.compileTTF(ufo, useProductionNames=False)

    dist_dir.mkdir(parents=True, exist_ok=True)
    otf_path = dist_dir / "ChaiSansYuniversus-Regular.otf"
    otf.save(str(otf_path))
    print(f"  → {otf_path.relative_to(Path.cwd())}")

    ttf_path = dist_dir / "ChaiSansYuniversus-Regular.ttf"
    ttf.save(str(ttf_path))
    print(f"  → {ttf_path.relative_to(Path.cwd())}")

    for flavor, ext in (("woff", ".woff"), ("woff2", ".woff2")):
        out = dist_dir / f"ChaiSansYuniversus-Regular{ext}"
        f = TTFont(str(otf_path))
        f.flavor = flavor
        f.save(str(out))
        print(f"  → {out.relative_to(Path.cwd())}")


if __name__ == "__main__":
    root = Path(__file__).parent
    ufos = sorted((root / "sources" / "masters").glob("*.ufo"))
    if not ufos:
        sys.exit("No .ufo files found in sources/masters/")

    dist = root / "dist"
    for ufo in ufos:
        build(ufo, dist)

    chai_sans_ufo = root / "sources" / "masters" / "ChaiSans-Regular.ufo"
    csv_path = root / "yuniversus-chaipua.csv"
    build_yuniversus(chai_sans_ufo, csv_path, dist)

    print("Done.")
