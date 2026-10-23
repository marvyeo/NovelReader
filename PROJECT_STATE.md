# NovelReader — Project State

> **Next chat name: `NovelReader ver 6`**
> Claude: your FIRST reply in a new chat must start with "Rename this chat to: **NovelReader ver 6**" (you can't rename chats yourself). In your first commit this session, bump the number here by 1.

**State version:** 5 (SAO vol 4 notes done 2026-10-23 in "NovelReader ver 5"; SAO vol 3 notes done 2026-10-23 in "NovelReader ver 4"; SAO vol 2 notes done 2026-10-23 in "NovelReader Session 1"; v1.0 built 2026-10-21 by the conductor chat "Life Plan Roadmap ver 2"; pushed live 2026-10-22 by "Life Plan Roadmap ver 3")
**Where this lives:** `PROJECT_STATE.md` in the repo. New chats `git pull` and read it; no uploads needed.

## ⚙ Session Rules (every chat that works on this app follows these)

**1. Pick the cheapest model that can do the job.** At the start of every session Claude names the model it recommends and the estimated size (below). If the chat is on a pricier model than needed, Claude says so before starting.

| Model | Use for |
|---|---|
| **Haiku** | State-file edits, text or label changes, small data packs, lookups, "where is X" questions |
| **Sonnet** (default) | Features, bug fixes, refactors, data processing (e.g. novel volumes, PullList), most app work |
| **Opus** | Only for new-app builds, cross-app architecture, or a bug Sonnet has failed on twice. Claude says why before using it |

**2. Every push updates this file in the same commit.** No exceptions, including PR branches and one-line fixes.
- `git pull` before starting, so you build on the latest state.
- Add a dated line to the change log (what changed and why, in plain words) and update any section the change made wrong.
- If a session ends without a push, nothing changes here.

**3. Size the work first, and plan the pause points.**
- Before starting, Claude lists the steps and sizes the job: **S** (under ~20k tokens), **M** (~20–60k), **L** (over ~60k).
- **M and L jobs are split into checkpoints.** Each checkpoint ends with a commit and a state update, so a cut-off session loses nothing.
- **Pause** when usage is around half the window, when the chat has grown long (heavy file reads, ~30+ turns), or before a step that won't finish in what's left. Claude can't see the remaining credit directly, so on L jobs it asks Marvin to check usage at each checkpoint.
- **On pause,** Claude writes a `▶ RESUME HERE` block at the top of this file: what's done, the exact next step, branch and files, and the first command to run. It also gives Marvin a one-line restart prompt ("Continue <App> ver X from RESUME HERE"). The next session starts from that block and deletes it once the step is done.

**4. Chat naming.** Use the **Next chat name** line at the top of this file; tell Marvin in the first reply, then bump it.

## What it is
A reading companion for Marvin's light novels. Claude reads the books (PDFs in `C:\Users\USER\Documents\LightNovels`) and writes notes; the app shows them with spoiler gating.

| Item | Value |
|---|---|
| Repo | `marvyeo/NovelReader` (public: **code only, never book notes, covers or art**) |
| Live URL | https://marvyeo.github.io/NovelReader/ |
| Stack | `index.html` (vanilla JS, own CSS, Literata + IBM Plex), `sw.js` (network-first, cache `novelreader-v1`), `manifest.json` (id `/NovelReader/`), `icons/` (ecosystem icon set) |
| Data | Google Drive folder `NovelReader`: `novelreader-data.json` (library, progress, picture index), one notes file per volume `novelreader-<series>-vNN.json`, covers `…-cover.jpg`, pictures `nr-art-…jpg` + `-thumb.jpg`. Scope `drive.file`, shared OAuth client `669494100250-…`. |
| Sign-in | Google token pop-up, plus redirect fallback for iPhone home-screen use (needs the URL under Authorized redirect URIs). |
| Life Plan | No `upcoming[]` items (empty array). Not on the dashboard. |
| Preview | Artifact "NovelReader Preview" = the same code with demo data injected as `window.NR_DEMO`. The live app never ships that block. |

## Screens
- **Library:** each series with owned/total, number with notes, reading position.
- **Series:** cover, owned/notes/to-get counts, "to get" pills (Japan-only flagged). A **volume slider** sets "I've read up to volume N". Tabs: **Who's who**, **What's what**, **Timeline** (all consolidated across every volume with notes, gated by the slider) and **Shelf** (every published volume: notes ready / owned, no notes yet / to get; dimmed past your position).
- **Volume:** cover, recap (unlocks at the end), chapter-by-chapter, and that volume's who's who, what's what and timeline. A **chapter slider** sets the same reading position (volume N, chapter C).
- **Character:** latest status, aliases, every fact grouped by volume, and **Pictures**: upload from the device (multi-select), tag each upload to a volume or as fan art, add a caption. Pictures tagged to volumes past your position stay hidden (count shown); fan art always shows. Cards in Who's who use the newest unlocked picture as the portrait.

## Spoiler rule
Reading position is one pointer per series, `{v, ch}`. An item from volume `n`, chapter `c` shows when `n < v`, or `n == v` and `c <= ch`.

## Pack formats (Claude produces these; import from the Library)
- `novelreader-series`: `{format, series:{id, title, author, note, volumes:[{n, subtitle, jp, en, owned}]}}`. Sets published volumes and what's owned.
- `novelreader-volume`: `{format, formatVersion:1, series:{id,title,author}, volume:{n, subtitle, chapters, source, processedOn}, recap:[para], chapters:[{n,title,where,summary,points[]}], people:[{id,name,group,from,role,aka:[[ch,text]],facts:[[ch,text]],status:[[ch,'alive|dead|unknown',label]]}], terms:[{kind,name,at,text}], timeline:[{at,when,what}], cover:'data:image/jpeg;base64,…'}`. **Keep person `id`s stable across volumes**; that's what merges a character's history.

## How Claude processes a volume (NovelReader chat, **Sonnet**)
1. Stage the PDF from the LightNovels folder (device bridge), `pdftotext`, split by chapter, read every chapter.
2. Write notes in Claude's own words (no long quotes; keep intimate scenes non-explicit). Reuse ids and group names from earlier packs of the same series.
3. Cover: `pdftoppm -f 1 -l 1 -jpeg -scale-to-x 480`.
4. Deliver the pack file to Marvin; he imports it.
5. **Budget:** one volume is an **L** job (~90k tokens of reading on Opus, much less on Sonnet). One volume per checkpoint; update "Library status" below after each, and pause per the Session Rules. Online research is a fallback for volume-level notes only (no chapter detail, spoiler leaks).

## Library status (2026-10-23)
| Series | Published (main) | Owned (folder) | Notes |
|---|---|---|---|
| Sword Art Online | 29 (vol 29 Japan only) | 1–27 | Vols 1–4 (packs `sao-v02/03/04.json` delivered into the LightNovels folder; Marvin to import) |
| Accel World | 28 (vol 28 Japan only; English due Dec 2026) | 1–3, 5–27 (vol 4 missing) | none |
| High School DxD | 25, complete (sequel True DxD: 4 in Japan) | 1–25 | none |

## Open items
- [x] Repo created (Marvin, 2026-10-22); code pushed to `main`.
- [ ] Marvin: Settings → Pages → Deploy from branch → `main` / root.
- [ ] Marvin: add `https://marvyeo.github.io/NovelReader/` under Authorized redirect URIs (shared client, project 669494100250). The JS origin `https://marvyeo.github.io` is already there.
- [ ] First run: import `sao-series.json`, `aw-series.json`, `dxd-series.json` and `sao-v01.json`.
- [ ] Marvin: import `sao-v02.json`, `sao-v03.json` and `sao-v04.json`; check vol 3's person ids against the app (see change log).
- [ ] Next volume: SAO vol 5 (Alfheim Online/Phantom Bullet start; Marvin's call), in "NovelReader ver 6" on Sonnet. Read ids only from `sao-v01/02/03/04.json` for id reuse, not the whole files.

## Change log
- **2026-10-23 (ver 5):** Processed SAO vol 4 (Fairy Dance conclusion): 18 sequential scene-chapters (1-4 Jotunheim/Tonky/Alne; 5 Asuna's lab escape; 6-12 hospital visit, first and second World Tree assaults, Suguha's reveal and duel; 13-14 reunion and Sugou's defeat, Kayaba's Seed; 15 hospital car park; 16-18 spring 2025 epilogue: school, Aincrad Conquest Celebration, Aincrad appears). Pack `sao-v04.json`, series id `sao`. Reused 15 ids from vol 3 (`kirito, asuna, yui, suguha, recon, sugou, shouzou, kayaba, klein, agil, silica, lisbeth, sakuya, alicia, eugene`); new ids: `tonky, rinko, thinker, yuriel, sasha`. Book gives no exact dates for vol 4, so the timeline uses 'Jan 2025' / 'Spring 2025'. Cost: about 85k tokens of book text on Sonnet.
- **2026-10-23 (ver 4):** Processed SAO vol 3 (Fairy Dance): prologue plus 3 long chapters split into 21 sequential scene-chapters (1 prologue; 2-6 real world and the dive; 7-11 first ALO day; 12 Asuna's cage; 13 Swilvane and Sigurd; 14 mirror code; 15-20 journey to Alne; 21 Asuna's escape). Pack `sao-v03.json`, series id `sao`. Reused ids `kirito, asuna, yui, agil, kayaba, klein, silica, lisbeth`. New ids: `suguha` (Leafa shown as an alias from ch 11, where the book reveals it; her in-game facts are filed at ch 11 to avoid a spoiler), `midori, minetaka, shouzou, sugou` (Oberon alias from ch 12), `recon` (Nagata alias from ch 11), `sigurd, sakuya, alicia, eugene, kagemune, mortimer`. Book dates are inconsistent (9 Jan duel, then 'Monday 20 Jan' for the next day), so later chapters use 20/21 Jan 2025 as printed. Cost: about 160k tokens of book text on Sonnet; the chat is now long, so start SAO vol 4 in a fresh chat.
- **2026-10-23:** Processed SAO vol 2 (Aincrad, 4 side stories, numbered as 15 sequential chapters: Silica 1–3, Lisbeth 4–7, Yui 8–11, Christmas 12–15). Pack `sao-v02.json`, series id `sao`. Vol 1's pack wasn't available in this chat, so person ids (`kirito`, `asuna`, `klein`, `heathcliff`, `kayaba`, `argo`) are the obvious slugs; **check them against vol 1's ids when importing and rename if they differ**. Reading cost ~95k tokens of book text on Sonnet.
- **v1.0 (2026-10-21):** Initial build from the SAO vol 1 test.
- **2026-10-22:** pushed live. Production page = the preview minus the demo block, plus the Google sign-in script, manifest, service worker and icons. Smoke-tested: opens to the sign-in screen, no script errors. Added Session Rules and `CLAUDE.md`.
