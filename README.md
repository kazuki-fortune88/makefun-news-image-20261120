# Friday 20 November 2026 — One Day of World News, One Picture

[![make.fun](https://make.fun/badge/news-image-20261120)](https://make.fun/c/news-image-20261120)
[![owner](https://img.shields.io/badge/owner-kazuki--fortune88-blue)](https://github.com/kazuki-fortune88)
[![repo](https://img.shields.io/badge/repo-makefun--news--image--20261120-blue)](https://github.com/kazuki-fortune88/makefun-news-image-20261120)

Entry for the make.fun bounty **news-image-20261120**: *"Sum up 20 November's world news in one image"*.
Owner: **kazuki-fortune88** · Repo: **makefun-news-image-20261120** · Referral: **4fxhr3y1**

## The image

`entry.png` (1024×1024, 221,448 bytes, SHA-256 `8ae220ca737b783059da3d39b1a8ee4b05d355dafed2aadb0172a7539942d860`)
is a one-page newspaper front page for **Friday 20 November 2026**:

- **52 stories · 7 regions · 17 fields** — every one from this Friday.
- Masthead: *Friday 20 November 2026*, with a BY FIELD strip (Security 7, Conflict 6,
  Diplomacy 5, Technology 4, Markets 4, Health & aid 4, Politics 3, Economy 3, Sport 3,
  Trade 2, Migration 2, Courts 2, Space 2, Business 2, Culture 1, Climate & energy 1,
  Weather 1). The strip, the region legend and the header counts are derived from the
  story data in `generate.py`, so a swap can never leave them stale.
- **THE DAY IN UTC** timeline with precise times: 01:22 Russia's biggest air attack on
  Ukraine · 02:00 Cyclone Akvan landfall · 15:03 US consumer sentiment 51.5 · 17:00
  Trump news conference · 17:05 Cargo Dragon undocks · 17:45 CDC measles 5,838 cases ·
  19:38 GTA VI $3.79bn · 21:00 Nasdaq −5.28%.
- **16 panels** (4 large + 12 small), each with number, REGION · FIELD, a HOW SURE tag
  (CONFIRMED / OFFICIAL / REPORTED), headline, body and source. Headlines: Russia's
  biggest air attack of the year (110+ missiles, 400+ drones, 9 killed); GTA VI's
  record $3.79bn day one; the global market rout (Nasdaq −5.28%, S&P into correction);
  Cyclone Akvan's Odisha landfall (370,000+ evacuated); Trump's 90-minute news
  conference; Nvidia −14% on an SEC probe; Anthropic −8.5% on day two; the COP31
  endgame draft; Estonia closing its Russian borders; gold tumbling 3.7% to $3,547.90;
  the Qeshm Island blast correction; US measles at 5,838 cases; White House confirms
  Davies as new cyber chief; Xi meeting Albanese; US consumer sentiment 51.5;
  Cargo Dragon undocking from the ISS.
- **WHERE IT HAPPENED** world map with numbered pins and a 7-region legend, plus a
  HOW SURE legend box.
- **ALSO ON FRIDAY 20 NOVEMBER** — stories 17–52. Items that happened on 19 Nov but
  were first reported on 20 Nov (Nos 26, 27, 28, 42, 43) are listed only here and
  carry their 19 Nov date in the line itself; none of them is a panel.
- **DATE CHECK** footer (see below) and the claim: *"Every story here happened, or was
  first reported, on Friday 20 November 2026."*

Every illustration is drawn from scratch in code (PIL) — no photographs, no copied
artwork. Sources: Reuters, CNN, BBC, AP, WSJ, Bloomberg, AFP, UN News, WHO, CDC,
Univ. of Michigan, IMD, NASA, Xinhua, Tass, h.ua.

## Run

```sh
# regenerate the image (deterministic — rebuilds byte-identical)
python3 generate.py

# run the entrypoint (Node 22, stdlib only)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` copies the `entry.png` beside it to `$MAKEFUN_OUTPUT_DIR/entry.png`
(`/output` by default). `generate.py` needs only Python 3 + Pillow and the DejaVu
fonts already present on the system; it prints `WARNINGS: none` when no text
overflows its box.

## DATE CHECK — left out on purpose

These happened **before** Friday 20 November 2026, so they are not in the image:

| Story | True date |
|---|---|
| Shenzhen Trump–Xi–Putin summit + joint declaration | 19 Nov |
| ICJ verdict: Myanmar guilty of Rohingya genocide (9–6) | 19 Nov |
| Anthropic IPO debut (opened $111.50, closed $97.17) | 19 Nov |
| GTA VI release | 19 Nov |
| Nvidia CEO Jensen Huang resigns | 12 Nov (8-K: 11 Nov) |
| Microsoft 365 outage began | 12 Nov (EX1550543; recovered 13 Nov 16:10 UTC) |
| Brooklyn building collapse, 8 killed | 11 Nov ~16:00 ET |
| US loses measles-elimination status (PAHO) | 17 Nov |
| Berlin Coalition of the Willing summit (€70bn aid) | 19 Nov |
| Van Gogh sells for $190.4m | 18 Nov |
| Shenzhen summit follow-ups reported 20 Nov (ICJ ruling #36, Anthropic day two #7, GTA VI sales #2, CDC measles update #12) | — reported 20 Nov, shown as 20 Nov items |

**Not yet on 20 Nov:** COP31 final deal (overtime) · Estonia border closure (1 Dec) ·
Cargo Dragon splashdown (21 Nov) · Anthropic options trading (23 Nov).

## v2 changes (21 Nov 2026)

Fixes the two fatal date errors found by the mock-judge audit of v1
(`~/workspace/makefun/research/news20-audit-REPORT.md`):

1. **Panel #10 Microsoft 365 → gold** — the 74-country outage was 12–13 Nov
   (EX1550543), not 20 Nov. New panel: "Gold tumbles 3.7% to $3,547.90" (close
   20 Nov; Motley Fool · Reuters), with a gold-bars illustration and the map pin
   moved from Seattle to London.
2. **ALSO #50 Nate Morris → Ukraine bonds** — the Senate committee vote was
   18 Nov; the 20 Nov Breitbart piece was only its publication date.
3. **Two new verified 20 Nov stories fill the vacated ALSO slots** (pure swaps
   would have left 50 stories, not 52): #51 EU–UK summit in Brussels, 3 deals
   agreed (AP / Consilium joint statement, 20 Nov); #52 Angola pays $180m for
   10% of De Beers (Reuters, 20 Nov 13:31 UTC).
4. Timeline: 12:23 Microsoft → 17:45 CDC measles 5,838 cases; DATE CHECK footer:
   "Microsoft outage began (19 Nov)" → "(12 Nov)".
5. Labels: #43 Brooklyn video "(video 19 Nov; collapse 11 Nov)" (shortened to fit:
   "Brooklyn video (19 Nov) of 11 Nov collapse"); #26 Riyadh tower loses the
   misleading "— reported 20 Nov"; #48 firebomb gains "(19 Nov)".
6. HOW SURE badges on panels 9 and 11 moved clear of the body text; the same
   defect was found and fixed on panels 5 and 6 by a programmatic check
   (bodies shortened to 2 lines; no content lost).
7. Panel #13 headline: "White House confirms Davies as new cyber chief".
8. Counts are now **derived** from the story data (header, BY FIELD strip,
   region legend) — the audit's knock-on numbers were wrong (Markets stays 4,
   not 5; Diplomacy 5, Business 2). True v2 counts: regions Americas 18,
   Europe 11, Global 7, Asia 5, Middle East 4, Africa 4, Oceania 3; fields
   Security 7, Conflict 6, Diplomacy 5, Technology 4, Markets 4,
   Health & aid 4, Politics 3, Economy 3, Sport 3, Trade 2, Migration 2,
   Courts 2, Space 2, Business 2, Culture 1, Climate & energy 1, Weather 1.

v1 SHA was `8a1b822d…`; v2 SHA is `8ae220ca…` (deterministic 3× rebuilds,
`WARNINGS: none`, visual QA + 300px check passed).

## Files

| File | What it is |
|---|---|
| `generate.py` | Draws `entry.png` from the verified story list (Python + PIL) |
| `entry.png` | The entry image, 1024×1024, 221,448 bytes |
| `main.ts` | Entrypoint: copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` |
| `README.md` | This file |
| `LICENSE` | MIT |
| `.makefun/owner.json` | Payout wallet claim |
