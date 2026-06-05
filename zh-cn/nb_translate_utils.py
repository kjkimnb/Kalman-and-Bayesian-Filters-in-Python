#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notebook 翻译辅助：复制原版、仅修改 markdown 单元格。"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
ZH_CN = Path(__file__).resolve().parent


def load_notebook(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_notebook(nb: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)


def cell_text(cell: dict[str, Any]) -> str:
    source = cell.get("source", [])
    if isinstance(source, list):
        return "".join(source)
    return source or ""


def set_cell_text(cell: dict[str, Any], text: str) -> None:
    if not text:
        cell["source"] = [""]
        return
    lines = text.splitlines(keepends=True)
    if not text.endswith("\n") and lines:
        last = lines[-1]
        if last.endswith("\n"):
            lines[-1] = last.rstrip("\n")
    cell["source"] = lines


def is_markdown(cell: dict[str, Any]) -> bool:
    return cell.get("cell_type") == "markdown"


def copy_notebook(rel_path: str, force: bool = False) -> Path:
    """从仓库根目录复制 notebook 到 zh-cn/。"""
    src = ROOT / rel_path
    dst = ZH_CN / rel_path
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        print(f"已存在，跳过复制: {dst}")
        return dst
    shutil.copy2(src, dst)
    print(f"已复制: {src} -> {dst}")
    return dst


def list_markdown_cells(nb: dict[str, Any]) -> list[tuple[int, str]]:
    return [(i, cell_text(c)) for i, c in enumerate(nb["cells"]) if is_markdown(c)]


def apply_markdown_translations(nb: dict[str, Any], translations: dict[int, str]) -> None:
    for idx, text in translations.items():
        cell = nb["cells"][idx]
        if not is_markdown(cell):
            raise ValueError(f"单元格 {idx} 不是 markdown")
        set_cell_text(cell, text)


def show_markdown(rel_path: str) -> None:
    """打印 markdown 单元格索引与预览，供翻译参考。"""
    path = ZH_CN / rel_path
    if not path.exists():
        copy_notebook(rel_path)
    nb = load_notebook(path)
    for idx, text in list_markdown_cells(nb):
        preview = text[:120].replace("\n", " ")
        print(f"[{idx}] ({len(text)} chars) {preview}...")


def collect_notebook_paths() -> list[str]:
    paths: list[str] = []
    for p in sorted(ROOT.rglob("*.ipynb")):
        rel = str(p.relative_to(ROOT))
        if rel.startswith("zh-cn/") or rel.startswith(".git/"):
            continue
        paths.append(rel)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Notebook 翻译辅助")
    sub = parser.add_subparsers(dest="cmd")

    p_copy = sub.add_parser("copy", help="复制 notebook 到 zh-cn/")
    p_copy.add_argument("notebook", help="相对路径，如 00-Preface.ipynb")
    p_copy.add_argument("--force", action="store_true")

    p_show = sub.add_parser("show", help="列出 markdown 单元格")
    p_show.add_argument("notebook")

    p_list = sub.add_parser("list", help="列出所有待翻译 notebook")

    args = parser.parse_args()
    if args.cmd == "copy":
        copy_notebook(args.notebook, force=args.force)
    elif args.cmd == "show":
        show_markdown(args.notebook)
    elif args.cmd == "list":
        for p in collect_notebook_paths():
            status = "exists" if (ZH_CN / p).exists() else "missing"
            print(f"{status}\t{p}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
