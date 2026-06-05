#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""应用 08、09 章 markdown 译文"""

from __future__ import annotations

import sys

from nb_translate_utils import (
    ZH_CN,
    ROOT,
    apply_markdown_translations,
    cell_text,
    is_markdown,
    list_markdown_cells,
    load_notebook,
    save_notebook,
)

from translations_08_part1 import TRANSLATIONS_08_PART1
from translations_08_part2 import TRANSLATIONS_08_PART2
from translations_09 import TRANSLATIONS_09

TRANSLATIONS_08 = {**TRANSLATIONS_08_PART1, **TRANSLATIONS_08_PART2}
NOTEBOOKS = {
    "08-Designing-Kalman-Filters.ipynb": TRANSLATIONS_08,
    "09-Nonlinear-Filtering.ipynb": TRANSLATIONS_09,
}


def verify_code_unchanged(nb_name: str) -> None:
    src = load_notebook(ROOT / nb_name)
    dst = load_notebook(ZH_CN / nb_name)
    if len(src["cells"]) != len(dst["cells"]):
        raise SystemExit(f"{nb_name}: cell count mismatch")
    for i, (sc, dc) in enumerate(zip(src["cells"], dst["cells"])):
        if sc.get("cell_type") != dc.get("cell_type"):
            raise SystemExit(f"{nb_name}: cell {i} type mismatch")
        if not is_markdown(sc) and cell_text(sc) != cell_text(dc):
            raise SystemExit(f"{nb_name}: non-markdown cell {i} changed")


def apply(nb_name: str, translations: dict[int, str]) -> None:
    path = ZH_CN / nb_name
    nb = load_notebook(path)
    md_cells = {i for i, _ in list_markdown_cells(nb)}
    missing = md_cells - set(translations)
    extra = set(translations) - md_cells
    if missing:
        raise SystemExit(f"{nb_name}: missing translations for cells {sorted(missing)}")
    if extra:
        raise SystemExit(f"{nb_name}: extra translation keys {sorted(extra)}")
    apply_markdown_translations(nb, translations)
    save_notebook(nb, path)
    verify_code_unchanged(nb_name)
    print(f"OK: {nb_name} ({len(translations)} markdown cells)")


def main() -> None:
    for nb_name, trans in NOTEBOOKS.items():
        apply(nb_name, trans)


if __name__ == "__main__":
    main()
