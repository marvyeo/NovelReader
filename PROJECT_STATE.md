# NovelReader — Project State

> **Next chat name: `NovelReader ver 26`**
> Claude: your FIRST reply in a new chat must start with "Rename this chat to: **NovelReader ver N**" (always the number on the Next chat name line) (you can't rename chats yourself). In your first commit this session, bump the number here by 1.

**State version:** 25 (token diagnosis + `nr_tools` built 2026-10-24 in "NovelReader ver 25"; SAO vol 20 notes done in ver 24; vols 2-19 done in earlier chats, older details in `PROJECT_STATE-archive-ver23.md`)
**Where this lives:** `PROJECT_STATE.md` in the repo (root; folder copy in LightNovels should match). New chats `git pull` and read it; no uploads needed.

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

**5. Token budget (added ver 25; the reason vol 19-20 cost ~300k vs ~125k of book text).** Cost is turns x context, not just reading: every call replays the whole chat, so 40+ small turns on a 150k context cost far more than the book itself.
- Use `nr_tools` (below). Read book text with **Read, one 45k-char chunk per call** (about 8 calls per volume), never 9-line Bash prints.
- After each chunk, save its notes at once as one small `dN.py` (`from lib import *`), then move on. No narration or thinking between calls, no re-reading, no printing packs, ids maps or the archive file.
- **Notes budget: at most ~11k tokens per volume** (build.py prints the figure). Vol 18-20 ran 15-17k, which is mostly extra output tokens. A person gets an entry only if recurring or plot-relevant; at most ~4 facts each (main cast may have more); at most 4 points per chapter; merge scenes into at most ~35 chapters.
- Model: Sonnet. Do not escalate to Opus for volume notes.
- If the chat context passes ~150k before the build, pause with a RESUME HERE block rather than finishing.

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
1. Stage the PDF from the LightNovels folder (device bridge) and run `nr_tools/prep.py` (it does pdftotext, compaction, chunking, id map and cover). Read every chunk with Read.
2. Write notes in Claude's own words (no long quotes; keep intimate scenes non-explicit). Reuse ids and group names from earlier packs of the same series.
3. Cover: made by `prep.py` (pdfimages, 480x720; never `pdftoppm`).
4. Deliver the pack file to Marvin; he imports it.
5. **Budget:** one volume is an **L** job (~90k tokens of reading on Opus, much less on Sonnet). One volume per checkpoint; update "Library status" below after each, and pause per the Session Rules. Online research is a fallback for volume-level notes only (no chapter detail, spoiler leaks).

## Library status (2026-10-23)
| Series | Published (main) | Owned (folder) | Notes |
|---|---|---|---|
| Sword Art Online | 29 (vol 29 Japan only) | 1–27 | Vols 1–20 (packs `sao-v02` to `sao-v20.json` delivered into the LightNovels folder; Marvin to import). Vol 21 next. |
| Accel World | 28 (vol 28 Japan only; English due Dec 2026) | 1–3, 5–27 (vol 4 missing) | none |
| High School DxD | 25, complete (sequel True DxD: 4 in Japan) | 1–25 | none |

## Open items
- [x] Repo created (Marvin, 2026-10-22); code pushed to `main`.
- [ ] Marvin: Settings → Pages → Deploy from branch → `main` / root.
- [ ] Marvin: add `https://marvyeo.github.io/NovelReader/` under Authorized redirect URIs (shared client, project 669494100250). The JS origin `https://marvyeo.github.io` is already there.
- [ ] First run: import `sao-series.json`, `aw-series.json`, `dxd-series.json` and `sao-v01.json`.
- [ ] Marvin: import `sao-v02.json` to `sao-v20.json`; check vol 3’s person ids against the app (see archive).
- [ ] Next volume: SAO vol 21 (`Sword Art Online/Sword Art Online Volume 21.pdf`, only ~84k tokens of text, 8 chunks), fresh chat on Sonnet, tools in `LightNovels\nr_tools` (identical copy in the repo under `tools/`, code only). Recipe (about 12 calls): (1) stage the PDF, all `sao-vNN.json` and `nr_tools/*` (staging is free); (2) `python3 prep.py "<pdf>" WORK PACKDIR sao` makes `WORK/chunks/c01..c08.txt`, `WORK/ids.txt` (199 known people, read once, ~3.5k tokens) and `WORK/cover.b64.txt`; (3) Read each chunk, then write `d1.py`, `d2.py`... (`from lib import *`; `meta()` first with n=21, subtitle, recap; `ch()` per scene-chapter; `f/al/st` auto-register ids found in ids.txt, `person(id,name,group,role)` only for NEW people; `term`, `tl`); (4) `NR_IDMAP=WORK/idmap.json python3 build.py d8 sao-v21.json WORK/cover.b64.txt` (the last module imports the earlier ones); (5) `device_commit_files` the pack into LightNovels, update this file, done. Vol 20 ended 27 Feb 382 HE; vol 21 starts a new arc, so check ids.txt before inventing new ids.
- [ ] Marvin: in the app, merge or accept that `kanamoto` (vol 6) and `johnny_black` (vol 8) are the same person (vol 9 ch 8 confirms); both cards got a vol 9 fact.
## Change log
- **2026-10-24 (ver 25):** Token diagnosis, no volume processed. Book text per volume is flat (85-160k tokens, vol 21 is only ~84k); what grew was everything around it: (1) ~16 reads of ≤9 lines (~4k tokens) each plus a write after each meant 40+ turns, and each turn replays the whole growing context (cache reads, quadratic); (2) notes output grew 2.4x, from ~6.6k tokens (vol 1) to ~15-17k (vols 18-20), because people entries went 13 to 71 per pack and people are 55-65% of the notes; output tokens cost the most; (3) every chat re-wrote `lib.py`/`build.py` and rebuilt the id map from scratch (none were saved); (4) the recipe itself grew long. Fixes: `LightNovels\nr_tools\{prep,lib,build}.py` (tested on vol 21's PDF: 0.6 s, 8 chunks), Session Rule 5 (Read in 45k-char chunks, notes cap ~11k tokens, known ids auto-registered), shorter recipe above. Expected: roughly half the turns and ~35% fewer output tokens, so about 40-50% lower cost per volume (estimate; check the meter on vol 21).
- **2026-10-24 (ver 24):** Processed SAO vol 20 (Moon Cradle, part 2) as 37 scene-chapters: Prologue (dream of the throne room, 1), Ch 1 (2-4 dawn sword, council scolding, past-scrying report and apprentice list), Ch 2 (5-8 lunch at the Lookout, hemp paper, paper-baked fish, Law of Power), Ch 3 (9-12 over the Everlasting Wall, Hollow Sphere, scrying Room 211, goblins gone), Ch 4 (13 dragon stable), Ch 5 (14 night in the room), Ch 6 (15-20 Lake Norkia, mansion, dungeon, Cruiga’s face), Ch 7 (21-22 search and flight), Ch 8 (23-25 Tsukigake’s run), Ch 9 (26-33 break-out, Zeppos, fusion minions, Moonbeam Sword, mansion dismantled, red jewel), Ch 10 (34-36 tea party, Blue Rose Sword, arrival of Frenica and Selka), 37 Afterword. Pack `sao-v20.json`, series id `sao`, 37 people (11 new: cruiga, hozaika, zeppos, nergius, entokia, ayuha, soness, xiao, hana, hainag, natsu), 29 terms, 17 timeline items; no new groups. Spoiler gating: the Obsidia `kidnapper` is revealed as Hozaika at ch 30 and set to dead; `cruiga` is alive at ch 20 and dead at ch 32; `zeppos` dead at ch 28; `aldares` unknown; Eugeo and Chudelkin set to dead; afterword facts (Ronie’s descendant Laurannei, the Abyssal Horror) filed last at ch 37 on purpose. Cost: about 300k tokens on the session meter, one chat; reading dominated. Vol 19 scene list and earlier details are in `sao-v19.json` and the archive file.
- **2026-10-24 (ver 22):** SAO vol 18 (Alicization Lasting) as 58 scene-chapters; pack `sao-v18.json`, 71 people, 32 terms, 20 timeline items. Underworld deaths set at ch 48 (see ver 23 note). Cost about 125k tokens of book text on Sonnet.
- **2026-10-24 (ver 21):** Tested the md route on vol 18: no real saving (raw pdftotext, ~120k tokens; compacted ~114k). The `.md` files are not in the folder. One-liner to compact: `python3 -c "import re,sys;t=open(sys.argv[1],encoding='utf-8').read().replace('\x0c','');t=re.sub(r'(?<!\n)\n(?!\n)',' ',t);t=re.sub(r'[ \t]+',' ',t);print(re.sub(r'\n{2,}','\n',t))" in.txt > out.txt`.
- **2026-10-21 to 10-24 (ver 1-20):** Built the app (v1.0, pushed live 2026-10-22) and processed SAO vols 2-17 one per chat. Per-volume details (scene-chapter lists, ids, spoiler-gating choices, cost) are in `PROJECT_STATE-archive-ver23.md`.
