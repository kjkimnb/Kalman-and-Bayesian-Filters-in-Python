# Kalman and Bayesian Filters in Python（中文版）

本目录为 [Kalman and Bayesian Filters in Python](https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python) 的中文翻译版，基于 Jupyter Notebook，代码与公式保持与英文原版一致。

## 使用方式

```bash
cd zh-cn
pip install -r requirements.txt
jupyter notebook table_of_contents.ipynb
```

请从 [目录](table_of_contents.ipynb) 开始阅读。

## 导出 PDF

可生成带封面、可跳转目录、含代码运行结果（含图片）的完整 PDF：

```bash
cd pdf
pip install nbconvert[webpdf] playwright
playwright install chromium
./build_pdf.sh
```

详见 [pdf/README.md](pdf/README.md)。输出：`Kalman_and_Bayesian_Filters_in_Python_zh-CN.pdf`（约 450 页）。

## 翻译说明

- 讲解文字为中文；关键数学与专业术语保留英文并附中文（如：卡尔曼滤波（Kalman filter））
- 所有代码单元格、LaTeX 公式未改动
- 详细规范见 [TRANSLATION_GUIDE.md](TRANSLATION_GUIDE.md)
- 翻译进度见 [NOTEBOOK_STATUS.md](NOTEBOOK_STATUS.md)

## 目录结构

与英文原版平行：`zh-cn/` 下 notebook 路径与根目录一致，运行依赖 `kf_book/`、`book_format.py`、`figs/` 等同名复制。
