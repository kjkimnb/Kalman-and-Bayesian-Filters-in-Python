#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 book.ipynb 导出为带封面、正式层级目录（章→节→页码）的 PDF。
"""

from __future__ import annotations

import asyncio
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pypdf import PdfReader

PDF_DIR = Path(__file__).resolve().parent
BOOK = PDF_DIR / 'book.ipynb'
OUT_PDF = PDF_DIR.parent / 'Kalman_and_Bayesian_Filters_in_Python_zh-CN.pdf'
HTML = PDF_DIR / 'book_export.html'

# 与 merge_book.py 章节顺序对应的目录标签
CHAPTER_LABELS = [
    '前言',
    '第 1 章',
    '第 2 章',
    '第 3 章',
    '第 4 章',
    '第 5 章',
    '第 6 章',
    '第 7 章',
    '第 8 章',
    '第 9 章',
    '第 10 章',
    '第 11 章',
    '第 12 章',
    '第 13 章',
    '第 14 章',
    '附录 A',
    '附录 B',
    '附录 D',
    '附录 E',
]

COVER_HTML = """
<div id="cover-page">
  <div class="cover-frame">
    <p class="cover-eyebrow">中文译本</p>
    <h1 class="cover-title">Python 中的<br>Kalman 与 Bayesian 滤波</h1>
    <div class="cover-divider"></div>
    <p class="cover-subtitle">Kalman and Bayesian Filters in Python</p>
    <p class="cover-author">Roger R Labbe Jr</p>
  </div>
</div>
"""

BOOK_STYLE = """
<style>
/* ===== 封面：整页正中 ===== */
#cover-page {
  page-break-after: always;
  width: 100%;
  height: 257mm;
  margin: 0;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  background: linear-gradient(165deg, #fafbfc 0%, #eef1f5 100%);
  font-family: 'Noto Serif CJK SC', 'Source Han Serif SC', 'Songti SC', serif;
}
.cover-frame {
  text-align: center;
  width: 82%;
  max-width: 140mm;
}
.cover-eyebrow {
  font-family: 'Noto Sans CJK SC', sans-serif;
  font-size: 11pt;
  letter-spacing: 0.35em;
  color: #5a6a7a;
  margin: 0 0 1.2rem 0;
  text-transform: none;
}
.cover-title {
  font-size: 26pt;
  font-weight: 700;
  line-height: 1.45;
  color: #1a2332;
  margin: 0;
  border: none;
  padding: 0;
}
.cover-divider {
  width: 36mm;
  height: 0.6pt;
  background: #2c5282;
  margin: 1.4rem auto;
}
.cover-subtitle {
  font-family: 'Noto Sans CJK SC', sans-serif;
  font-size: 13pt;
  font-weight: 400;
  color: #3d4f63;
  margin: 0 0 1.6rem 0;
  line-height: 1.5;
}
.cover-author {
  font-family: 'Noto Sans CJK SC', sans-serif;
  font-size: 11pt;
  color: #6b7c8f;
  margin: 0;
}

/* ===== 目录：出版物风格 ===== */
#book-toc-page {
  page-break-after: always;
  padding: 14mm 18mm 16mm 18mm;
  font-family: 'Noto Sans CJK SC', 'Source Han Serif SC', sans-serif;
  color: #1a2332;
}
.toc-heading {
  font-family: 'Noto Serif CJK SC', serif;
  font-size: 20pt;
  font-weight: 700;
  text-align: center;
  margin: 0 0 10mm 0;
  padding-bottom: 4mm;
  border-bottom: 0.8pt solid #2c5282;
  letter-spacing: 0.2em;
}
.toc-chapter-block {
  margin-top: 5mm;
  break-inside: avoid;
}
.toc-entry {
  display: flex;
  align-items: baseline;
  text-decoration: none;
  color: inherit;
  line-height: 1.65;
  break-inside: avoid;
}
.toc-entry:hover .toc-label { color: #2c5282; }
.toc-label {
  flex: 0 1 auto;
  max-width: 78%;
}
.toc-leader {
  flex: 1 1 auto;
  border-bottom: 0.6pt dotted #aab4c0;
  margin: 0 2mm 1.2mm 2mm;
  min-width: 4mm;
}
.toc-page {
  flex: 0 0 auto;
  font-variant-numeric: tabular-nums;
  min-width: 7mm;
  text-align: right;
  color: #3d4f63;
}
.toc-chapter {
  font-size: 11pt;
  font-weight: 700;
  margin-top: 1mm;
}
.toc-chapter .toc-label { color: #1a2332; }
.toc-section {
  font-size: 9.5pt;
  font-weight: 400;
  padding-left: 8mm;
  color: #3d4f63;
}
.toc-section .toc-leader {
  border-bottom-color: #c8d0d8;
}

@media print {
  .jp-InputPrompt, .jp-OutputPrompt { font-size: 0.8rem; }
  img { max-width: 100%; page-break-inside: avoid; }
  h1, h2 { break-after: avoid; }
}
</style>
"""


@dataclass
class TocSection:
    title: str
    anchor: str
    page: Optional[int] = None


@dataclass
class TocChapter:
    label: str
    title: str
    anchor: str
    page: Optional[int] = None
    sections: list[TocSection] = field(default_factory=list)

    @property
    def display_title(self) -> str:
        if self.label == '前言':
            return '前言'
        if self.label.startswith('附录'):
            return f'{self.label}　{self.title}'
        return f'{self.label}　{self.title}'


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


def parse_headings(html: str) -> list[TocChapter]:
    """解析 h1/h2，按章→节层级组织。"""
    raw: list[tuple[int, str, str]] = []
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
        raw.append((level, title, hid))

    chapters: list[TocChapter] = []
    chapter_idx = 0
    current: Optional[TocChapter] = None

    for level, title, hid in raw:
        if level == 1:
            label = (
                CHAPTER_LABELS[chapter_idx]
                if chapter_idx < len(CHAPTER_LABELS)
                else f'第 {chapter_idx} 章'
            )
            current = TocChapter(label=label, title=title, anchor=hid)
            chapters.append(current)
            chapter_idx += 1
        elif level == 2 and current is not None:
            current.sections.append(TocSection(title=title, anchor=hid))

    return chapters



def find_page_for_anchor(chapters: list[TocChapter], reader: PdfReader) -> dict[str, int]:
    """在第一遍 PDF 中按文档顺序查找各 anchor 所在页（1-based，跳过封面）。"""
    page_texts = [
        (i + 1, re.sub(r'\s+', '', page.extract_text() or ''))
        for i, page in enumerate(reader.pages)
    ]

    def locate(title: str, start_page: int, min_len: int = 4) -> Optional[int]:
        compact_title = re.sub(r'\s+', '', title)
        for n in (min(12, len(compact_title)), min(8, len(compact_title)), len(compact_title)):
            if n < min_len:
                continue
            key = compact_title[:n]
            for pno, text in page_texts:
                if pno < start_page:
                    continue
                if key in text:
                    return pno
        return None

    pages: dict[str, int] = {}
    cursor = 2  # 第 1 页为封面

    for ch in chapters:
        min_len = 2 if ch.label == '前言' else 4
        p = locate(ch.title if ch.label != '前言' else '前言', cursor, min_len=min_len)
        if p:
            pages[ch.anchor] = p
            ch.page = p
            cursor = p
        for sec in ch.sections:
            sp = locate(sec.title, cursor, min_len=4)
            if sp:
                pages[sec.anchor] = sp
                sec.page = sp
                cursor = sp
    return pages


def render_toc_html(chapters: list[TocChapter], toc_page_offset: int = 0) -> str:
    """渲染层级目录 HTML。"""

    def entry(label: str, anchor: str, page: Optional[int], css: str) -> str:
        if page is None:
            pg_str = ''
        else:
            pg_str = str(page + toc_page_offset)
        return (
            f'<a class="toc-entry {css}" href="#{anchor}">'
            f'<span class="toc-label">{label}</span>'
            f'<span class="toc-leader"></span>'
            f'<span class="toc-page">{pg_str}</span>'
            f'</a>'
        )

    blocks = ['<div id="book-toc-page">', '<div class="toc-heading">目　录</div>']
    for ch in chapters:
        blocks.append('<div class="toc-chapter-block">')
        blocks.append(entry(ch.display_title, ch.anchor, ch.page, 'toc-chapter'))
        for sec in ch.sections:
            blocks.append(entry(sec.title, sec.anchor, sec.page, 'toc-section'))
        blocks.append('</div>')
    blocks.append('</div>')
    return '\n'.join(blocks)


def inject_cover_and_toc(html: str, toc_html: str) -> str:
    insert_at = html.find('<body')
    if insert_at == -1:
        return BOOK_STYLE + COVER_HTML + toc_html + html
    body_open_end = html.find('>', insert_at) + 1
    return (
        html[:body_open_end]
        + BOOK_STYLE
        + COVER_HTML
        + toc_html
        + html[body_open_end:]
    )


async def render_pdf(html_path: Path, pdf_path: Path) -> int:
    """渲染 PDF，返回页数。"""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(html_path.resolve().as_uri(), wait_until='networkidle')
        await page.pdf(
            path=str(pdf_path),
            format='A4',
            print_background=True,
            tagged=True,
            outline=True,
            margin={'top': '18mm', 'bottom': '18mm', 'left': '16mm', 'right': '16mm'},
        )
        n = len(PdfReader(str(pdf_path)).pages)
        await browser.close()
        return n


async def build_pdf() -> None:
    if not BOOK.exists():
        raise SystemExit(f'未找到 {BOOK}，请先运行 merge_book.py')

    print('导出 HTML…')
    export_html()
    base_html = HTML.read_text(encoding='utf-8')
    chapters = parse_headings(base_html)
    print(f'  解析到 {len(chapters)} 章，'
          f'{sum(len(c.sections) for c in chapters)} 个小节')

    # 第一遍：封面 + 正文（无目录页），测定各标题在 PDF 中的页码
    print('第一遍渲染（测定页码）…')
    probe_html = inject_cover_and_toc(base_html, '')
    probe_path = PDF_DIR / '_probe.html'
    probe_path.write_text(probe_html, encoding='utf-8')
    probe_pdf = PDF_DIR / '_probe.pdf'
    await render_pdf(probe_path, probe_pdf)
    find_page_for_anchor(chapters, PdfReader(str(probe_pdf)))
    content_only_pages = len(PdfReader(str(probe_pdf)).pages)
    probe_path.unlink(missing_ok=True)
    probe_pdf.unlink(missing_ok=True)

    # 第二遍及校正：插入正式目录，页码 = 第一遍页码 + 目录页数
    entry_count = sum(1 + len(ch.sections) for ch in chapters)
    toc_pages = max(2, entry_count // 26 + 1)

    for attempt in range(5):
        toc_html = render_toc_html(chapters, toc_page_offset=toc_pages)
        HTML.write_text(inject_cover_and_toc(base_html, toc_html), encoding='utf-8')
        print(f'渲染 PDF（目录偏移 {toc_pages} 页，第 {attempt + 1} 次）…')
        await render_pdf(HTML, OUT_PDF)
        total = len(PdfReader(str(OUT_PDF)).pages)
        actual_toc = total - content_only_pages
        if actual_toc == toc_pages:
            break
        print(f'  目录实际 {actual_toc} 页，重新校正页码')
        toc_pages = actual_toc

    size_mb = OUT_PDF.stat().st_size / 1024 / 1024
    pages = len(PdfReader(str(OUT_PDF)).pages)
    print(f'完成: {OUT_PDF}（{pages} 页，{size_mb:.1f} MB）')


def main() -> None:
    asyncio.run(build_pdf())


if __name__ == '__main__':
    main()
