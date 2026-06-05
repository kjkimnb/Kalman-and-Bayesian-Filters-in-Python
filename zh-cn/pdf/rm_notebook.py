#!/usr/bin/env python3
"""PDF 构建前预处理 notebook：注释掉会导致 LaTeX 转换失败的 magic。"""
import io
import sys


def preprocess(path):
    with open(path, encoding='utf8') as f:
        data = f.read()
    buf = io.StringIO(data)
    first_inline = False
    is_code_cell = False
    out_lines = []
    for line in buf:
        if '"cell_type":' in line:
            is_code_cell = '"code"' in line
        if is_code_cell:
            if '%matplotlib inline' in line:
                if first_inline:
                    line = line.replace('%matplotlib inline', '#%matplotlib inline')
                first_inline = True
            for token in (
                '%matplotlib notebook',
                'time.sleep',
                'fig.canvas.draw',
                'plt.gcf().canvas.draw',
            ):
                if token in line and not line.strip().startswith('#'):
                    line = line.replace(token, '#' + token)
        out_lines.append(line)
    with open(path, 'w', encoding='utf8') as f:
        f.write(''.join(out_lines))


if __name__ == '__main__':
    preprocess(sys.argv[1])
