#!/usr/bin/env python3
"""
Build NumPy-Book.pdf from the markdown chapters in content/chapters/.

Usage:
    python3 build/build.py

Two-pass build: pass 1 renders the book to find which physical page each
chapter starts on, pass 2 re-renders with the real page numbers filled
into the table of contents.
"""
import glob
import os
import re
import sys

import markdown
import pdfplumber
import yaml
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(ROOT, "content", "chapters")
STYLES_PATH = os.path.join(ROOT, "styles", "book.css")
ASSETS_DIR = os.path.join(ROOT, "assets")
OUTPUT_DIR = os.path.join(ROOT, "output")
CHROME_PATH = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

BOOK_TITLE = "NumPy Book"
BOOK_SUBTITLE = "Course Notes & Summaries"
COURSE_CREDIT = "JoeTech"
COMPILER = "Youssef"
COMPILED_DATE = "August 2026"

MD_EXTENSIONS = ["fenced_code", "codehilite", "tables", "sane_lists", "attr_list"]
MD_EXT_CONFIG = {"codehilite": {"guess_lang": False}}


def load_chapters():
    files = sorted(glob.glob(os.path.join(CONTENT_DIR, "*.md")))
    if not files:
        sys.exit(f"No chapter files found in {CONTENT_DIR}")
    chapters = []
    for f in files:
        raw = open(f, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n?(.*)$", raw, re.DOTALL)
        if not m:
            sys.exit(f"{f}: missing YAML frontmatter (--- ... ---)")
        meta = yaml.safe_load(m.group(1)) or {}
        if "title" not in meta:
            sys.exit(f"{f}: frontmatter needs a 'title'")
        body_html = markdown.markdown(
            m.group(2), extensions=MD_EXTENSIONS, extension_configs=MD_EXT_CONFIG
        )
        meta["html"] = body_html
        meta["_file"] = os.path.basename(f)
        chapters.append(meta)
    chapters.sort(key=lambda c: (c.get("order", 9999), c["_file"]))
    return chapters


def inject_dropcap(html):
    return re.sub(r"^<p>", '<p class="dropcap">', html, count=1)


def render_cover():
    return f"""
    <section class="cover">
      <div class="cover-inner">
        <div class="cover-eyebrow">A Study Companion</div>
        <div class="cover-ornament"><span class="line"></span><span class="diamond"></span><span class="line"></span></div>
        <h1 class="cover-title">{BOOK_TITLE}</h1>
        <div class="cover-subtitle">{BOOK_SUBTITLE}</div>
        <div class="cover-tagline">Notes &amp; summaries from the <span class="course">NumPy</span> video course by <span class="course">{COURSE_CREDIT}</span></div>
        <div class="cover-footer">Compiled by {COMPILER}<span class="divider">&#10022;</span>2026</div>
      </div>
    </section>
    """


def render_titlepage():
    return f"""
    <section class="page titlepage">
      <p class="label">About this book</p>
      <p>{BOOK_TITLE} is a personal study companion compiled while following the NumPy course by {COURSE_CREDIT} on YouTube.</p>
      <p>Each chapter distills one lesson from the series into readable notes, worked examples, and quick-reference tables.</p>
      <hr class="rule">
      <p>Compiled by {COMPILER} &middot; first compiled {COMPILED_DATE}</p>
      <p>Not an official publication of {COURSE_CREDIT} or the NumPy project.</p>
    </section>
    """


def render_toc(chapters, page_numbers=None):
    rows = []
    for i, ch in enumerate(chapters, start=1):
        pageno = "&mdash;" if not page_numbers else str(page_numbers.get(i, "&mdash;"))
        meta = ch.get("source", "")
        meta_html = f'<span class="meta">{meta}</span>' if meta else ""
        rows.append(
            f"""
        <div class="toc-entry">
          <span class="num">{i:02d}</span>
          <span class="title">{ch['title']}{meta_html}</span>
          <span class="leader"></span>
          <span class="pageno">{pageno}</span>
        </div>"""
        )
    return f"""
    <section class="page toc">
      <h1 class="toc-heading">Contents</h1>
      <hr class="rule-gold">
      {''.join(rows)}
    </section>
    """


def render_chapter(i, ch):
    marker = (
        f'<span id="chmark-{i}" '
        f'style="position:absolute; top:0; left:0; color:#faf7f0; font-size:6pt;">'
        f"CHAPTERMARK{i:03d}</span>"
    )
    source_line = f'<div class="chapter-source">{ch["source"]}</div>' if ch.get("source") else ""
    return f"""
    <section class="page chapter">
      {marker}
      <div class="chapter-open">
        <div class="chapter-eyebrow">Chapter {i:02d}</div>
        <h1 class="chapter-title">{ch['title']}</h1>
        {source_line}
        <div class="chapter-ornament"><span class="line"></span><span class="diamond"></span><span class="line"></span></div>
      </div>
      <div class="chapter-body">{inject_dropcap(ch['html'])}</div>
    </section>
    """


def render_full_html(chapters, page_numbers=None):
    css = open(STYLES_PATH, encoding="utf-8").read()
    parts = [render_cover(), render_titlepage(), render_toc(chapters, page_numbers)]
    parts += [render_chapter(i, ch) for i, ch in enumerate(chapters, start=1)]
    body = "\n".join(parts)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{BOOK_TITLE}</title>
<base href="file://{ASSETS_DIR}/">
<style>{css}</style>
</head>
<body>{body}</body>
</html>"""


HEADER_TEMPLATE = f"""
<div style="font-family: 'EB Garamond', 'Liberation Serif', serif; font-size:8pt;
            width:100%; text-align:center; color:#8a7e6a; letter-spacing:0.15em;
            text-transform:uppercase; padding-top:6mm;">
  {BOOK_TITLE}
</div>
"""
FOOTER_TEMPLATE = """
<div style="font-family: 'EB Garamond', 'Liberation Serif', serif; font-size:9pt;
            width:100%; text-align:center; color:#4a4038; padding-bottom:5mm;">
  <span class="pageNumber"></span>
</div>
"""
PDF_MARGIN = {"top": "30mm", "bottom": "24mm", "left": "30mm", "right": "22mm"}


def print_pdf(browser, html_path, pdf_path, with_header_footer):
    page = browser.new_page()
    page.goto(f"file://{html_path}")
    page.wait_for_timeout(150)
    page.pdf(
        path=pdf_path,
        format="A4",
        print_background=True,
        display_header_footer=with_header_footer,
        header_template=HEADER_TEMPLATE if with_header_footer else "<span></span>",
        footer_template=FOOTER_TEMPLATE if with_header_footer else "<span></span>",
        margin=PDF_MARGIN,
    )
    page.close()


def find_chapter_pages(pdf_path, n_chapters):
    pages = {}
    with pdfplumber.open(pdf_path) as pdf:
        for pno, pg in enumerate(pdf.pages, start=1):
            text = pg.extract_text() or ""
            for i in range(1, n_chapters + 1):
                if i not in pages and f"CHAPTERMARK{i:03d}" in text:
                    pages[i] = pno
    return pages


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    chapters = load_chapters()
    print(f"Loaded {len(chapters)} chapter(s).")

    draft_html_path = os.path.join(OUTPUT_DIR, "_draft.html")
    draft_pdf_path = os.path.join(OUTPUT_DIR, "_draft.pdf")
    final_html_path = os.path.join(OUTPUT_DIR, "_final.html")
    final_pdf_path = os.path.join(OUTPUT_DIR, "NumPy-Book.pdf")

    with open(draft_html_path, "w", encoding="utf-8") as f:
        f.write(render_full_html(chapters, page_numbers=None))

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH)

        print("Pass 1/2: measuring page numbers...")
        print_pdf(browser, draft_html_path, draft_pdf_path, with_header_footer=False)
        page_numbers = find_chapter_pages(draft_pdf_path, len(chapters))

        with open(final_html_path, "w", encoding="utf-8") as f:
            f.write(render_full_html(chapters, page_numbers=page_numbers))

        print("Pass 2/2: rendering final PDF...")
        print_pdf(browser, final_html_path, final_pdf_path, with_header_footer=True)

        browser.close()

    for tmp in (draft_html_path, draft_pdf_path, final_html_path):
        os.remove(tmp)

    print(f"Done -> {final_pdf_path}")


if __name__ == "__main__":
    main()
