# NumPy Book

A real explained textbook built lesson-by-lesson from the NumPy YouTube
course by **JoeTech** — not condensed bullet-point notes. Each lesson is a
full write-up in English, followed section by section by an **Egyptian
Arabic** explanation in its own panel: concept explained in prose, code
walked through line by line, callouts for gotchas/tips, and both an
English "Key Takeaways" and an Arabic "الخلاصة" box at the end.
Modern textbook design: full-bleed pages, Sora headings, Source Serif 4
body text, IBM Plex Sans Arabic for the RTL panels, dark
syntax-highlighted code blocks.

## Workflow

1. You send a summary of one video from the course.
2. Claude expands it into a full lesson — explaining the *why*, not just
   the *what*, using its own NumPy knowledge to fill gaps — and adds it
   as a new file in `content/chapters/`.
3. Rebuild the PDF and review.

**Scope rule:** a lesson only covers what that video actually covered. No
code or concepts from later videos get introduced early, even when they
would make the explanation richer.

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

### Arabic explanation blocks

English is the main text; each section is followed by an Egyptian-Arabic
explanation in an RTL panel. Three variants, all needing `markdown="1"`
and blank lines around the inner Markdown:

```markdown
<div class="ar" markdown="1">

شرح القسم بالعربي — الليبل بيطلع تلقائي "بالعربي".

</div>

<div class="ar code-notes" markdown="1">

- `import numpy as np` — شرح السطر ده.

</div>

<div class="ar summary" markdown="1">

- نقطة من نقط الخلاصة.

</div>
```

## Building the PDF

```bash
python3 build/build.py
```

Output: `output/NumPy-Book.pdf`. The build runs two passes — the first
measures which physical page each lesson starts on, the second fills in
real page numbers in the table of contents.
