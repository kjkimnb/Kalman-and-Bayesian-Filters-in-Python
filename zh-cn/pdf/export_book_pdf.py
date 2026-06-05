#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 book.ipynb 导出为带封面、可跳转目录的 PDF（Chromium / Playwright）。
保留代码输入与运行结果（含图片）。
"""

from __future__ import annotations

import asyncio
import re
import subprocess
import sys
from pathlib import Path

PDF_DIR = Path(__file__).resolve().parent
BOOK = PDF_DIR / 'book.ipynb'
OUT_PDF = PDF_DIR.parent / 'Kalman_and_Bayesian_Filters_in_Python_zh-CN.pdf'
HTML = PDF_DIR / 'book_export.html'


COVER_HTML = """
<div id="cover-page" style="
  page-break-after: always;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  font-family: 'Noto Serif CJK SC', 'Source Han Serif SC', serif;
  padding: 2rem;
">
  <h1 style="font-size: 2.4rem; margin-bottom: 1.2rem; border: none;">
    Python 中的 Kalman 与 Bayesian 滤波
  </h1>
  <h2 style="font-size: 1.5rem; font-weight: normal; color: #333; border: none;">
    Kalman and Bayesian Filters in Python
  </h2>
  <p style="font-size: 1.2rem; margin-top: 1rem;">中文译本</p>
  <p style="margin-top: auto; color: #555;">Roger R Labbe Jr</p>
</div>
"""

TOC_STYLE = """
<style>
#book-toc-page { page-break-after: always; padding: 2rem 3rem; font-family: 'Noto Sans CJK SC', sans-serif; }
#book-toc-page h1 { border-bottom: 2px solid #333; padding-bottom: 0.5rem; }
#book-toc-page ol { line-height: 1.8; }
#book-toc-page a { color: #1a5276; text-decoration: none; }
#book-toc-page a:hover { text-decoration: underline; }
#book-toc-page .toc-h2 { margin-left: 1.5rem; font-size: 0.95rem; }
@media print {
  .jp-InputPrompt, .jp-OutputPrompt { font-size: 0.8rem; }
  img { max-width: 100%; page-break-inside: avoid; }
}
</style>
"""


def export_html() -> None:
    subprocess.run(
        [
            'jupyter', 'nbconvert',
            '--to', 'html',
            '--template', 'lab',
            '--embed-images',
            str(BOOK),
            '--output', HTML.stem,
        ],
        cwd=PDF_DIR,
        check=True,
    )


def slugify(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
    return re.sub(r'[\s_]+', '-', text) or 'section'


def build_toc_and_inject_ids(html: str) -> str:
    """从已有 h1/h2 标题生成目录（nbconvert lab 模板已带 id）。"""
    headings: list[tuple[int, str, str]] = []

    for m in re.finditer(
        r'<h([12])\s+id="([^"]+)"[^>]*>(.*?)</h\1>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    ):
        level = int(m.group(1))
        hid = m.group(2)
        title_html = m.group(3)
        title = re.sub(r'<a class="anchor-link".*?</a>', '', title_html, flags=re.DOTALL)
        title = re.sub(r'<[^>]+>', '', title).strip()
        if not title or title.startswith('In ['):
            continue
        if hid == 'table-of-contents':
            continue
        headings.append((level, title, hid))

    toc_items = []
    for level, title, hid in headings:
        cls = 'toc-h2' if level == 2 else ''
        toc_items.append(f'<li class="{cls}"><a href="#{hid}">{title}</a></li>')

    toc_html = (
        '<div id="book-toc-page">'
        '<h1 id="table-of-contents">目录</h1>'
        f'<ol>{"".join(toc_items[:250])}</ol>'
        '</div>'
    )

    insert_at = html.find('<body')
    if insert_at == -1:
        return COVER_HTML + TOC_STYLE + toc_html + html
    body_open_end = html.find('>', insert_at) + 1
    return html[:body_open_end] + TOC_STYLE + COVER_HTML + toc_html + html[body_open_end:]


def postprocess_html() -> None:
    html = HTML.read_text(encoding='utf-8')
    html = build_toc_and_inject_ids(html)
    HTML.write_text(html, encoding='utf-8')


async def html_to_pdf() -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(HTML.resolve().as_uri(), wait_until='networkidle')
        await page.pdf(
            path=str(OUT_PDF),
            format='A4',
            print_background=True,
            tagged=True,
            outline=True,
            margin={'top': '18mm', 'bottom': '18mm', 'left': '16mm', 'right': '16mm'},
        )
        await browser.close()


def main() -> None:
    if not BOOK.exists():
        raise SystemExit(f'未找到 {BOOK}，请先运行 merge_book.py')
    print('导出 HTML…')
    export_html()
    print('生成封面与目录…')
    postprocess_html()
    print('渲染 PDF…')
    asyncio.run(html_to_pdf())
    print(f'完成: {OUT_PDF} ({OUT_PDF.stat().st_size / 1024 / 1024:.1f} MB)')


if __name__ == '__main__':
    main()
