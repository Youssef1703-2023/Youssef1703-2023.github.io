# NumPy Book

A personal study companion built from summaries of the NumPy YouTube course
by **JoeTech**. Designed like a small academic textbook: serif typography
(Playfair Display + EB Garamond), a formal title page, a table of contents,
drop caps on chapter openers, and styled code/notes/tips boxes.

## Structure

```
numpy-book/
  content/chapters/     one markdown file per video, e.g. 02-broadcasting.md
  styles/book.css        the book's visual design
  assets/fonts/          embedded font files (no internet needed to build)
  build/build.py         builds content/chapters/*.md -> output/NumPy-Book.pdf
  output/                generated PDF (git-ignored except on request)
```

## Adding a new chapter

Create `content/chapters/NN-short-title.md` with frontmatter:

```markdown
---
title: Chapter title shown in the book
order: 2
source: "JoeTech, NumPy Course, Video 2 — Broadcasting"
---

Chapter content in Markdown. Supports headings (`##`, `###`), **bold**,
*italic*, fenced code blocks, tables, and lists.

<div class="box">
  <div class="box-label">Note</div>
  <p>Use this for asides worth calling out.</p>
</div>
```

## Building the PDF

```bash
python3 build/build.py
```

Output: `output/NumPy-Book.pdf`. The build runs two passes — the first
measures which physical page each chapter starts on, the second fills in
real page numbers in the table of contents.
