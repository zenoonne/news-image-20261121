# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/zenoonne/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/zenoonne/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

An illustrated newspaper front page that sums up **Saturday 21 November 2026**: a masthead carrying the date huge and red, a numbers strip giving the 33-story count per region (Middle East 5 · Europe 11 · Asia 8 · Americas 5 · Oceania 2 · Africa 1 · Space 1) plus six verified statistics from the day, a "HOW SURE ARE WE?" line, **three big illustrated features** each with a detailed code-drawn scene, **ten medium illustrated stories** (each with a scene, a location label, a coloured region tag, a bold headline, a sourced one-line subline and a confidence tag), and the remaining **twenty stories** in a compact numbered list. A **world map** ("WHERE IT HAPPENED") carries numbered pins matching the thirteen features, and a **DATE CHECK** box names the stories left off the page because they actually happened on other days. Every illustrated story is tagged **REPORTED**, **FORECAST** or **CLAIM** so the page is honest about what is asserted versus asserted-by-someone. Every one of the 33 items is an *event of that day* (not merely a 21 November report), verified against a primary outlet and recorded with its event date in `SOURCES.md` (the FTA signing, the mercury-orbit insertion, the Gulf of Finland drone strike, the Gaza aid-truck strike, the COP31 deadlock, the Manipur alcohol poisonings, the Basra fire, the Houthi missiles over Riyadh, and more). Two optional boxes were deliberately dropped: **MARKETS & MONEY**, because Saturday is a non-trading day for the major exchanges and no genuine same-day figure could be verified, and **THE DAY BY HOURS**, because fewer than four event clock-times could be pinned to a primary outlet. The renderer (`render.py`, Python + Pillow, with `worldmap.py` for the simplified continent polygons) draws the whole page offline and deterministically from embedded data — no external images and no network — and the graded entrypoint (`main.ts`) copies the rendered `entry.png` to the output directory.

## Run it

```sh
node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
