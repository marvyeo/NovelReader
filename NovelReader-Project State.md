# NovelReader - Project State

Handoff version: 20 -> 21
Last updated: 2026-10-23
**Next chat name: NovelReader ver 21**

## What this project is
Converts light novels (Yen On ebook PDFs) into structured JSON reference packs for import into the Marvin app (marvyeo.github.io/NovelReader/). One volume per chat, numbered sequentially.

## Pack contents
- Chapters (scene-level summaries), characters (reuse IDs from earlier volumes), terms, timeline, recap, cover image.
- Validate all cross-references are in range before delivery.

## Locations
- Repo: github.com/marvyeo/NovelReader (PROJECT_STATE.md is the canonical log)
- Local: C:\Users\USER\Documents\LightNovels (source PDFs + sao-v0X.json packs + PROJECT_STATE.md; folder copy can be newer than the repo copy)

## Workflow per volume
1. Stage target PDF + all prior packs of that series (to reuse character IDs).
2. Extract text with pdftotext (no -layout), reflow paragraphs; chapter boundary regex `^\d{1,2} [A-Z"]`.
3. Read in chunks, saving working notes after each.
4. Build pack, validate, write to LightNovels folder, update PROJECT_STATE.md, commit/push.
5. Recommend a fresh chat for the next volume.

## Cost rules (user preference: frugality)
- Use Sonnet, not Opus, for volume processing (~90-105k tokens of book text per volume).
- One volume per chat; compact and move to a new chat when history is heavy.
- Candidate saving: convert PDF/EPUB to Markdown locally with MarkItDown (`pip install 'markitdown[all]'`, `markitdown vol.pdf -o vol.md`), then read the .md instead of re-extracting. Avoid its LLM-OCR/Azure options (billable).

## Known open items
- Possible duplicate character Kanamoto / Johnny Black (SAO v6/v8/v9) - merge in Marvin.
- This handoff was written in ver 20 WITHOUT access to the repo's PROJECT_STATE.md (GitHub access was denied). Volume-by-volume status for v10-v19 is NOT recorded here. Merge with the repo/folder PROJECT_STATE.md before relying on it.

## Next step
Open "NovelReader ver 21", confirm which series/volume is next (check the latest PROJECT_STATE.md in the LightNovels folder), then process it.
