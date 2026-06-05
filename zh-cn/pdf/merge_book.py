#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并 zh-cn 各章节 notebook 为单一 book.ipynb，供 PDF 导出。"""

from __future__ import print_function

import io
from pathlib import Path

import nbformat

from formatting import remove_links, remove_links_add_appendix, strip_raw_cells

PDF_DIR = Path(__file__).resolve().parent
ZH_CN = PDF_DIR.parent
TMP = PDF_DIR / 'tmp'

# 与英文版 merge_book.py 相同的章节顺序（不含独立目录 notebook）
NOTEBOOK_ORDER = [
    '00-Preface.ipynb',
    '01-g-h-filter.ipynb',
    '02-Discrete-Bayes.ipynb',
    '03-Gaussians.ipynb',
    '04-One-Dimensional-Kalman-Filters.ipynb',
    '05-Multivariate-Gaussians.ipynb',
    '06-Multivariate-Kalman-Filters.ipynb',
    '07-Kalman-Filter-Math.ipynb',
    '08-Designing-Kalman-Filters.ipynb',
    '09-Nonlinear-Filtering.ipynb',
    '10-Unscented-Kalman-Filter.ipynb',
    '11-Extended-Kalman-Filters.ipynb',
    '12-Particle-Filters.ipynb',
    '13-Smoothing.ipynb',
    '14-Adaptive-Filtering.ipynb',
    'Appendix-A-Installation.ipynb',
    'Appendix-B-Symbols-and-Notations.ipynb',
    'Appendix-D-HInfinity-Filters.ipynb',
    'Appendix-E-Ensemble-Kalman-Filters.ipynb',
]


def merge_notebooks(out_path, filenames):
    merged = None
    added_appendix = False
    for fname in filenames:
        path = Path(fname)
        with io.open(path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, nbformat.NO_CONVERT)
        name = path.name
        if not added_appendix and name.startswith('Appendix'):
            remove_links_add_appendix(nb)
            added_appendix = True
        else:
            remove_links(nb)
        if merged is None:
            merged = nb
        else:
            merged.cells.extend(nb.cells)
    strip_raw_cells(merged)
    with io.open(out_path, 'w', encoding='utf-8') as f:
        nbformat.write(merged, f)


def clean_spurious_strings(path):
    with open(path, encoding='utf-8') as f:
        s = f.read()
    for old in (
        '<IPython.core.display.Javascript object>',
        '<IPython.core.display.HTML object>',
    ):
        s = s.replace(old, '')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(s)


if __name__ == '__main__':
    sources = [TMP / name for name in NOTEBOOK_ORDER]
    missing = [str(p) for p in sources if not p.exists()]
    if missing:
        raise SystemExit('缺少 notebook：\n' + '\n'.join(missing))
    out = PDF_DIR / 'book.ipynb'
    merge_notebooks(out, sources)
    clean_spurious_strings(out)
    print(f'已合并 {len(NOTEBOOK_ORDER)} 个 notebook -> {out}')
