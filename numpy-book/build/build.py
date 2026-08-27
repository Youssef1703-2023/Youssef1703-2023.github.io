#!/usr/bin/env python3
"""
Build NumPy-Book.pdf from the markdown lessons in content/chapters/.

Usage:
    python3 build/build.py

Two-pass build: pass 1 renders the book to find which physical page each
lesson starts on, pass 2 re-renders with the real page numbers filled
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
BOOK_SUBTITLE = "Lessons & Explanations"
COURSE_CREDIT = "JoeTech"
COMPILER = "Youssef"
COMPILED_YEAR = "2026"

MD_EXTENSIONS = ["fenced_code", "codehilite", "tables", "sane_lists", "attr_list"]
MD_EXT_CONFIG = {"codehilite": {"guess_lang": False}}


def load_lessons():
    files = sorted(glob.glob(os.path.join(CONTENT_DIR, "*.md")))
    if not files:
        sys.exit(f"No lesson files found in {CONTENT_DIR}")
    lessons = []
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
        lessons.append(meta)
    lessons.sort(key=lambda c: (c.get("order", 9999), c["_file"]))
    return lessons


def render_cover():
    return f"""
    <section class="cover">
      <div class="cover-kicker">A Course Companion</div>
      <div class="cover-bar"></div>
      <h1 class="cover-title">{BOOK_TITLE}</h1>
      <div class="cover-subtitle">{BOOK_SUBTITLE}</div>
      <div class="cover-tagline">A lesson-by-lesson walkthrough of <span class="course">NumPy</span>,
        built from the YouTube course by <span class="course">{COURSE_CREDIT}</span>.</div>
      <div class="cover-footer">
        <span>Compiled by {COMPILER}</span>
        <span>{COMPILED_YEAR}</span>
      </div>
    </section>
    """


def render_toc(lessons, page_numbers=None):
    rows = []
    for i, ch in enumerate(lessons, start=1):
        pageno = "&ndash;" if not page_numbers else str(page_numbers.get(i, "&ndash;"))
        meta = ch.get("source", "")
        meta_html = f'<span class="meta">{meta}</span>' if meta else ""
        rows.append(
            f"""
        <div class="toc-entry">
          <span class="num">{i:02d}</span>
          <div class="body">
            <span class="title">{ch['title']}</span>
            {meta_html}
          </div>
          <span class="pageno">{pageno}</span>
        </div>"""
        )
    return f"""
    <section class="page toc">
      <div class="toc-kicker">Contents</div>
      <h1 class="toc-heading">What's inside</h1>
      {''.join(rows)}
    </section>
    """


def render_lesson(i, ch):
    marker = (
        f'<span id="lsmark-{i}" '
        f'style="position:absolute; top:0; left:0; color:#ffffff; font-size:6pt;">'
        f"LESSONMARK{i:03d}</span>"
    )
    source_line = f'<div class="lesson-source">{ch["source"]}</div>' if ch.get("source") else ""
    return f"""
    <section class="page lesson">
      {marker}
      <div class="lesson-open">
        <div class="lesson-kicker">
          <span class="index">{i:02d}</span>
          <span class="label">Lesson {i:02d}</span>
        </div>
        <h1 class="lesson-title">{ch['title']}</h1>
        {source_line}
      </div>
      <div class="lesson-body">{ch['html']}</div>
    </section>
    """


def render_full_html(lessons, page_numbers=None):
    css = open(STYLES_PATH, encoding="utf-8").read()
    parts = [render_cover(), render_toc(lessons, page_numbers)]
    parts += [render_lesson(i, ch) for i, ch in enumerate(lessons, start=1)]
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


FOOTER_TEMPLATE = """
<div style="font-family: 'Sora', sans-serif; font-size:8.5pt; width:100%;
            text-align:right; color:#9aa3af; padding-right:18mm; padding-bottom:6mm;">
  <span class="pageNumber"></span>
</div>
"""
PDF_MARGIN = {"top": "18mm", "bottom": "16mm", "left": "18mm", "right": "18mm"}


def print_pdf(browser, html_path, pdf_path, with_footer):
    page = browser.new_page()
    page.goto(f"file://{html_path}")
    page.wait_for_timeout(150)
    page.pdf(
        path=pdf_path,
        format="A4",
        print_background=True,
        display_header_footer=with_footer,
        header_template="<span></span>",
        footer_template=FOOTER_TEMPLATE if with_footer else "<span></span>",
        margin=PDF_MARGIN,
    )
    page.close()


def find_lesson_pages(pdf_path, n_lessons):
    pages = {}
    with pdfplumber.open(pdf_path) as pdf:
        for pno, pg in enumerate(pdf.pages, start=1):
            text = pg.extract_text() or ""
            for i in range(1, n_lessons + 1):
                if i not in pages and f"LESSONMARK{i:03d}" in text:
                    pages[i] = pno
    return pages


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    lessons = load_lessons()
    print(f"Loaded {len(lessons)} lesson(s).")

    draft_html_path = os.path.join(OUTPUT_DIR, "_draft.html")
    draft_pdf_path = os.path.join(OUTPUT_DIR, "_draft.pdf")
    final_html_path = os.path.join(OUTPUT_DIR, "_final.html")
    final_pdf_path = os.path.join(OUTPUT_DIR, "NumPy-Book.pdf")

    with open(draft_html_path, "w", encoding="utf-8") as f:
        f.write(render_full_html(lessons, page_numbers=None))

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH)

        print("Pass 1/2: measuring page numbers...")
        print_pdf(browser, draft_html_path, draft_pdf_path, with_footer=False)
        page_numbers = find_lesson_pages(draft_pdf_path, len(lessons))

        with open(final_html_path, "w", encoding="utf-8") as f:
            f.write(render_full_html(lessons, page_numbers=page_numbers))

        print("Pass 2/2: rendering final PDF...")
        print_pdf(browser, final_html_path, final_pdf_path, with_footer=True)

        browser.close()

    for tmp in (draft_html_path, draft_pdf_path, final_html_path):
        os.remove(tmp)

    print(f"Done -> {final_pdf_path}")


if __name__ == "__main__":
    main()
