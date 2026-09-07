# Anime article cross-posting pipeline

## What this repo does
Takes one source `.docx` article (plus WhatsApp image exports) and produces five
publish-ready markdown files: Medium, DEV, Quora, Substack, LinkedIn.
Images are hosted in this repo and hotlinked from the published articles.

Owner: Rehan — GitHub RehanKhilji47, hello@maddigi.co

## Hard rules

- **Medium is verbatim.** Never rewrite it. Only strip pandoc artifacts and swap
  image paths for hosted URLs. Keep the author's original title.
- **No Hashnode.** Five platforms only.
- **Every other platform gets its own title** and genuinely rewritten prose.
  Target: under ~20% identical sentences for the worst pair. Check with
  `scripts/qa_check.py`.
- **Tables always become PNGs.** No platform gets a markdown table.
- **Never delete or rename an image** already in `images/`. Published articles
  hotlink them. Only add.
- **Image sequence in every variant must match Medium exactly.** Force-align and
  verify after building, never trust the builder.

## The blank-line rule (most important)

Every image must have a **blank line before it**. An image on the line directly
after text is parsed as part of that paragraph, not as its own block, and will
silently fail to render on LinkedIn.

This caused days of misdiagnosis. `scripts/qa_check.py` checks for it.

## LinkedIn image URLs

Use this exact format — it is the only one confirmed working:

```
https://raw.githubusercontent.com/RehanKhilji47/poster/main/images/<slug>/<name>.png?v=1
```

raw host, **folder root** (not `/web/`), **.png**, **`?v=1`**.

Other platforms use the smaller web JPEGs:
`https://rehankhilji47.github.io/poster/images/<slug>/web/<name>.jpg`

Do not "improve" the LinkedIn URLs. github.io and `/web/` JPEGs have both failed.
LinkedIn also fetches images unreliably in bursts — always ship a numbered image
zip alongside so images can be inserted manually.

## Source doc conventions

- Images sitting **side by side in one paragraph** are a comparison figure.
  Composite them into a single PNG (see `scripts/composite.py`). Markdown cannot
  do side-by-side, so keeping them separate loses the pairing.
  Caption is usually `Left: Source. Right: Edited Image.`
- Images in **separate paragraphs** with text between stay separate.
- **Always render the .docx to PDF and look at it** before assuming a layout.
  Getting this wrong has cost several rebuilds.
- A repeated source image is normal — it's one file referenced many times.

## Image resolution

Compare the docx-embedded copy against the WhatsApp upload and use whichever is
larger. It varies per article. When compositing, resize to the **smaller** of the
pair's heights so nothing gets upscaled.

## Pandoc artifacts to clean

`<span class="mark">`, `<u>`, stray `**` after images, `***Caption*`,
images glued to text, loose lists (use `scripts/tighten_lists.py`).

## Build order

1. Extract docx, inventory images, check for tables
2. Render docx to PDF and inspect layout
3. Match uploads to docx images (`scripts/match_images.py`)
4. Build composites and table PNGs
5. Commit + push images, verify URLs return 200
6. Build Medium verbatim
7. Write four variants with distinct titles and prose
8. Run `scripts/qa_check.py` — fix anything it flags before delivering
9. Build numbered image zip

## Outstanding

- Medium articles are set to `noindex,nofollow` — needs fixing in Medium settings
- Featured images missing across the back catalogue
