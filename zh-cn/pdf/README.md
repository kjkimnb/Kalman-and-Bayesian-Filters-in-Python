# 中文版 PDF 构建说明

> **大多数读者不需要运行本文档。** 预生成的 PDF 已在仓库根目录：
> [`../Kalman_and_Bayesian_Filters_in_Python_zh-CN.pdf`](../Kalman_and_Bayesian_Filters_in_Python_zh-CN.pdf)
> — 直接下载即可。

以下说明仅供**修改 notebook 后需要重新导出 PDF** 时使用。

## 一键构建

```bash
cd zh-cn/pdf
pip install -r ../requirements.txt nbconvert[webpdf] playwright
playwright install chromium   # 首次需要
./build_pdf.sh
```

输出文件：`zh-cn/Kalman_and_Bayesian_Filters_in_Python_zh-CN.pdf`

## 构建步骤

| 步骤 | 脚本 | 说明 |
|------|------|------|
| 1 | `prepare_tmp.py` | 复制 19 个主章节到 `tmp/`，预处理 magic，**执行 notebook** 生成输出 |
| 2 | `merge_book.py` | 合并为 `book.ipynb`，去掉目录链接与 raw 单元格 |
| 3 | `export_book_pdf.py` | 导出 HTML（嵌入图片）→ 插入封面/目录 → Chromium 渲染 PDF |

## 选项

```bash
# 跳过重新执行 notebook（使用已有输出，更快）
./build_pdf.sh --no-execute
```

## 包含章节

与英文版 `pdf/merge_book.py` 相同：

- 前言 + 第 1–14 章
- 附录 A、B、D、E

## 依赖

- Python 3.8+
- `filterpy`, `jupyter`, `nbconvert[webpdf]`, `playwright`
- 系统字体：`fonts-noto-cjk`（中文显示）

## 文件说明

- `build_pdf.sh` — 主入口
- `export_book_pdf.py` — HTML + Playwright PDF（封面、目录、内链）
- `templates/zh_book/` — 可选 LaTeX 模板（XeLaTeX 路线，部分公式可能报错）
- `tmp/`、`book.ipynb`、`book_export.html` — 构建中间产物
