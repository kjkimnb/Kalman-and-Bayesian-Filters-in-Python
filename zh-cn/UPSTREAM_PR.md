# Upstream PR (rlabbe/Kalman-and-Bayesian-Filters-in-Python)

**Branch pushed:** `kjkimnb:zh-cn-translation` (single commit, only `zh-cn/`)

**Open PR here:**  
https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python/compare/master...kjkimnb:zh-cn-translation?expand=1

---

## Title

Add Simplified Chinese translation (zh-cn/)

## Body (copy into PR description)

## Summary

This PR adds a **Simplified Chinese** edition of the book in a self-contained `zh-cn/` directory. The original English notebooks are **unchanged**.

## Contents

| Item | Location |
|------|----------|
| Chinese notebooks | `zh-cn/` (ch. 0–14, appendices, supporting notebooks) |
| Entry point | `zh-cn/table_of_contents.ipynb` |
| Pre-built PDF (~29 MB) | `zh-cn/Kalman_and_Bayesian_Filters_in_Python_zh-CN.pdf` |
| Notes | `zh-cn/README.md`, `zh-cn/TRANSLATION_GUIDE.md` |

## Translation

- Markdown → Chinese; **code cells and LaTeX unchanged**
- Key terms bilingual where helpful (e.g. Kalman filter / 卡尔曼滤波)
- PDF: cover, chapter-level TOC with page numbers, embedded outputs

## Use

```bash
cd zh-cn && pip install -r requirements.txt && jupyter notebook table_of_contents.ipynb
```

Happy to adjust layout or scope per your preference.
