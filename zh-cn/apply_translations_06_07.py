#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""应用 06、07 章 markdown 译文"""

from __future__ import annotations

import json
import sys
from pathlib import Path

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

from translations_06_part1 import TRANSLATIONS_06_PART1
from translations_06_part2 import TRANSLATIONS_06_PART2
from translations_07 import TRANSLATIONS_07

TRANSLATIONS_06 = {**TRANSLATIONS_06_PART1, **TRANSLATIONS_06_PART2}
NOTEBOOKS = {
    "06-Multivariate-Kalman-Filters.ipynb": TRANSLATIONS_06,
    "07-Kalman-Filter-Math.ipynb": TRANSLATIONS_07,
}


def verify_code_unchanged(nb_name: str) -> None:
  src = load_notebook(ROOT / nb_name)
  dst = load_notebook(ZH_CN / nb_name)
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
