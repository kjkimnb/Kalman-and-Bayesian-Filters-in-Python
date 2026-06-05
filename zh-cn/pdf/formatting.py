from __future__ import print_function
import io
import nbformat


def _cell_source(cell):
    src = cell.get('source', '')
    if isinstance(src, list):
        return ''.join(src)
    return src


def strip_raw_cells(nb):
    """移除 raw 单元格（如 \\addcontentsline），避免污染 PDF。"""
    nb['cells'] = [c for c in nb['cells'] if c.get('cell_type') != 'raw']


def remove_formatting(nb):
    cells = nb['cells']
    for i in range(len(cells)):
        src = _cell_source(cells[i])
        if src.lstrip().startswith('#format the book'):
            del cells[i]
            return


def _is_toc_link(src):
    s = src.lstrip()
    return s.startswith('[Table of Contents]') or s.startswith('[目录')


def remove_links(nb):
    cells = nb['cells']
    for i in range(len(cells)):
        if _is_toc_link(_cell_source(cells[i])):
            del cells[i]
            return


def remove_links_add_appendix(nb):
    cells = nb['cells']
    for i in range(len(cells)):
        if _is_toc_link(_cell_source(cells[i])):
            cells[i]['source'] = ['\\appendix\n']
            return
