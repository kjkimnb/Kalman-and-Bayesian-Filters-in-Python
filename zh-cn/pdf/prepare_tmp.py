#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""准备 PDF 构建用的 tmp 目录：复制 notebook 与依赖并预处理。"""

import shutil
import subprocess
import sys
from pathlib import Path

PDF_DIR = Path(__file__).resolve().parent
ZH_CN = PDF_DIR.parent
TMP = PDF_DIR / 'tmp'

NOTEBOOKS = [
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


def main(execute: bool = True) -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)

    for name in NOTEBOOKS:
        shutil.copy2(ZH_CN / name, TMP / name)

    shutil.copy2(ZH_CN / 'book_format.py', TMP / 'book_format.py')
    shutil.copytree(ZH_CN / 'kf_book', TMP / 'kf_book')
    if (ZH_CN / 'figs').exists():
        shutil.copytree(ZH_CN / 'figs', TMP / 'figs')

    rm = PDF_DIR / 'rm_notebook.py'
    for nb in NOTEBOOKS:
        subprocess.run([sys.executable, str(rm), str(TMP / nb)], check=True)

    if execute:
        print('正在执行 notebook（含代码输出与图片），耗时较长…')
        for nb in NOTEBOOKS:
            print(f'  execute: {nb}')
            subprocess.run(
                [
                    'jupyter', 'nbconvert',
                    '--allow-errors',
                    '--inplace',
                    '--execute',
                    '--ExecutePreprocessor.timeout=600',
                    nb,
                ],
                cwd=TMP,
                check=False,
            )


if __name__ == '__main__':
    do_exec = '--no-execute' not in sys.argv
    main(execute=do_exec)
