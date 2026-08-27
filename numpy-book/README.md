# NumPy Book

A real explained textbook built lesson-by-lesson from the NumPy YouTube
course by **JoeTech** — not condensed bullet-point notes. Each lesson is a
full write-up (in English): concept explained in prose, worked code
examples, callouts for gotchas/tips, and a "Key Takeaways" box at the end.
Modern textbook design: full-bleed pages, Sora headings, Source Serif 4
body text, dark syntax-highlighted code blocks.

## Workflow

1. You send a summary of one video from the course (any language).
2. Claude expands it into a full lesson — explaining the *why*, not just
   the *what*, using its own NumPy knowledge to fill gaps and add
   examples the summary didn't spell out — and adds it as a new file in
   `content/chapters/`.
3. Rebuild the PDF and review.

## Structure

```
numpy-book/
  content/chapters/     one markdown file per video, e.g. 02-broadcasting.md
  styles/book.css        the book's visual design
  assets/fonts/          embedded font files (no internet needed to build)
  build/build.py         builds content/chapters/*.md -> output/NumPy-Book.pdf
  output/                generated PDF
```

## Adding a new lesson

Create `content/chapters/NN-short-title.md` with frontmatter:

```markdown
---
title: Lesson title shown in the book
order: 2
source: "JoeTech, NumPy Course, Video 2 — Broadcasting"
---

Lesson content in Markdown. Supports headings (`##`, `###`), **bold**,
*italic*, fenced code blocks, tables, and lists.

<div class="box">
  <div class="box-label">Tip</div>
  <p>Use this for a positive aside worth calling out.</p>
</div>

<div class="box warn">
  <div class="box-label">Watch out</div>
  <p>Use this (amber) for gotchas and common mistakes.</p>
</div>

<div class="takeaways">
  <div class="box-label">Key takeaways</div>
  <ul>
    <li>One line per core idea from the lesson.</li>
  </ul>
</div>
```

## Building the PDF

```bash
python3 build/build.py
```

Output: `output/NumPy-Book.pdf`. The build runs two passes — the first
measures which physical page each lesson starts on, the second fills in
real page numbers in the table of contents.
