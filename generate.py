#!/usr/bin/env python3
"""News Image — Friday 20 November 2026 (news-image-20261120).

Draws entry.png (1024x1024) from the verified research in
~/workspace/makefun/research/news20-stories.md — 52 stories, 7 regions,
17 fields. Written from scratch for this competition; no code or data is
reused from any earlier entry. Deterministic: fixed fonts, fixed layout,
no randomness, no timestamps in the image.
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (20, 20, 20)
RED = (178, 34, 34)
DARKRED = (140, 20, 20)
RULE = (120, 110, 95)
FAINT = (90, 84, 72)
LIGHT = (235, 229, 214)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

WARNINGS = []


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit `width`."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, fnt, width, max_lines, label):
    """Wrap text to at most max_lines; record a warning if it overflows."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) > max_lines:
        WARNINGS.append(f"OVERFLOW {label}: {len(lines)} lines > {max_lines}: {text[:60]!r}")
        lines = lines[:max_lines]
        # trim last line with an ellipsis
        while lines and draw.textlength(lines[-1] + "…", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "…"
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


# Region colours (used for the region dot, panel top rule and map pins)
REGION_COLOR = {
    "Europe": (31, 95, 168),
    "Americas": (176, 58, 46),
    "Global": (52, 73, 94),
    "Asia": (183, 121, 31),
    "Middle East": (125, 60, 152),
    "Africa": (30, 132, 73),
    "Oceania": (20, 143, 119),
}
TAG_FILL = {
    "CONFIRMED": (30, 132, 73),
    "OFFICIAL": (31, 95, 168),
    "REPORTED": (125, 60, 152),
    "CLAIM": (183, 121, 31),
    "FORECAST": (90, 84, 72),
}

# (no, region, field, tag, source, headline, body)
PANELS = [
    (1, "Europe", "Conflict", "CONFIRMED", "CNN · Reuters · AP",
     "Russia launches biggest air attack of the year on Ukraine",
     "110+ missiles and 400+ drones overnight; 9 killed, Kyiv bridges hit, power cut in 11 regions. Zelensky: “biggest this year.”"),
    (2, "Global", "Culture", "OFFICIAL", "Reuters · Rockstar / Take-Two",
     "GTA VI books record $3.79bn in day-one sales",
     "Biggest entertainment launch ever — 32.5m pre-orders. Take-Two announced the figure on Friday; GTA V made $800m on day one."),
    (3, "Global", "Markets", "CONFIRMED", "Reuters · WSJ · AP",
     "Global market rout: Nasdaq −5.28%, S&P into correction",
     "Nasdaq’s 2nd-biggest points drop ever; Dow −950. S&P fell a 7th straight day, its longest slide since 2020; VIX hit 35.89."),
    (4, "Asia", "Weather", "OFFICIAL", "IMD · The Hindu",
     "Cyclone Akvan hits Odisha; 370,000+ evacuated",
     "Landfall near Gopalpur at 02:00 UTC, winds 70–80 km/h. No deaths reported; 9,341 shelters and 423 rescue teams readied."),
    (5, "Americas", "Politics", "CONFIRMED", "Reuters · White House",
     "Trump holds 90-min White House news conference",
     "After his China trip, he hails “very good talks” with Putin and touts trade deals with Thailand and the Philippines."),
    (6, "Americas", "Technology", "REPORTED", "Reuters",
     "Nvidia plunges 14% as SEC scrutinises its accounts",
     "Worst day in ~2 years on reports of a probe into possible accounting issues. Shares closed at $125.53; −23% on the week."),
    (7, "Americas", "Markets", "CONFIRMED", "Nasdaq tape · Finnhub",
     "Anthropic falls 8.5% on day two to $88.91",
     "Nearly erasing its debut gain; shares touched $83.05, five cents above the $83 IPO price. Valuation about $1.16 trillion."),
    (8, "Global", "Climate & energy", "CONFIRMED", "Reuters · UN News",
     "COP31 endgame: draft drops fossil-fuel language",
     "Revised deal drops all fossil-fuel wording and a $120bn adaptation target; talks head for overtime past Friday’s deadline."),
    (9, "Europe", "Security", "OFFICIAL", "Reuters · Estonian MFA",
     "Estonia to shut all road borders with Russia from 1 Dec",
     "Five crossings close for at least six months after a suspected GRU arson attack. Moscow calls it a “new Iron Curtain.”"),
    (10, "Global", "Markets", "CONFIRMED", "Motley Fool · Reuters",
     "Gold tumbles 3.7% to $3,547.90",
     "Investors flee to bonds as the rout deepens; the 10-year yield eases to 5.04%. Consumer staples were the only S&P sector in the green."),
    (11, "Middle East", "Conflict", "REPORTED", "Reuters · Tasnim",
     "Blast on Iran’s Qeshm Island was munitions disposal",
     "Tasnim corrected its own report of a missile strike: the blast was unexploded ordnance being disposed of."),
    (12, "Americas", "Health & aid", "OFFICIAL", "Reuters · CDC",
     "US measles cases hit 5,838, CDC reports",
     "Up 7.9% in a week; six deaths in 2026. First weekly update since the US lost its measles-elimination status on 17 Nov."),
    (13, "Americas", "Security", "CONFIRMED", "Bloomberg · Reuters",
     "White House confirms Davies as new cyber chief",
     "Pentagon CIO Kirsten Davies takes the acting role, replacing Sean Cairncross, fired on Thursday. Senate must confirm her."),
    (14, "Oceania", "Diplomacy", "OFFICIAL", "Xinhua · Reuters",
     "Xi meets Albanese in Shenzhen",
     "China–Australia ties in a “comprehensive turnaround”, Xi says. Albanese pushes for more beef and rice access to China."),
    (15, "Americas", "Economy", "OFFICIAL", "Univ. of Michigan",
     "US consumer sentiment rises to 51.5 in November",
     "Up from 48.0 as one-year inflation expectations ease to 3.7% from 4.7%, the final Michigan survey shows."),
    (16, "Global", "Space", "OFFICIAL", "NASA · Space.com",
     "SpaceX Cargo Dragon undocks from ISS",
     "CRS-35 leaves with time-sensitive science; splashdown is due off California on Saturday 21 November."),
]

# ALSO 17–52: one short line each. Items marked (19 Nov) happened on 19 Nov
# and were first reported on 20 Nov — the 19 Nov date is printed in the line
# itself, so the date claim stays exact. Renumbered for v2: gold (#43) moved
# to panel 10, Ukraine bonds (#22) moved to #50, Morris (#50) removed, and
# two new verified 20 Nov stories added (#51 EU-UK summit, #52 Angola).
ALSO = [
    (17, "Poland: missiles crash in Poland; NATO jets up"),
    (18, "Moldova: Russian drone in airspace 9 min"),
    (19, "Smolensk: drones hit Dorogobuzh chem plant"),
    (20, "Kharkiv: strikes kill 1, injure 39"),
    (21, "Ukraine rail hit; delays up to 10 hours"),
    (22, "Russia rules out Ukraine NATO entry"),
    (23, "Trump: more work on fair Canada deal"),
    (24, "US presses Singapore, Malaysia on Iran"),
    (25, "Houthis cloud Trump–Saudi nuclear pact"),
    (26, "Riyadh tower hit (19 Nov)"),
    (27, "Trump delays Iran decision to 2027 (19 Nov)"),
    (28, "Haiti police kill 34 gang suspects (19 Nov)"),
    (29, "Haiti: 2 Salvadoran soldiers killed"),
    (30, "New migrant caravan of ~300 enters Mexico"),
    (31, "Tesla opens first store in Argentina"),
    (32, "Brazil real slides for 4th straight week"),
    (33, "WHO: DRC Ebola 11,680 cases, 5,715 deaths"),
    (34, "S. Sudan readies as Ebola risk put at 99%"),
    (35, "African ministers push health into COP31"),
    (36, "ICJ Myanmar ruling may aid S. Africa Gaza case"),
    (37, "S. Korea orders exam overhaul after AI cheating"),
    (38, "India fight back in Wellington Test, day 2"),
    (39, "U-17 World Cup: Italy 6–0, Spain 5–0"),
    (40, "Bayern held 1–1 by Köln; Ronaldo scores"),
    (41, "Chip rout: AMD −13%, Micron −14%"),
    (42, "Cyber chief Cairncross fired (19 Nov)"),
    (43, "Brooklyn video (19 Nov) of 11 Nov collapse"),
    (44, "Ex-Nvidia chief Huang to testify at Senate"),
    (45, "NASA: Artemis III stays in low Earth orbit"),
    (46, "Philippines eyes SpaceX launch-site deal"),
    (47, "Australia travel declaration pilot expands"),
    (48, "Firebomb attack at Colombia protests (19 Nov)"),
    (49, "RSF: 30+ journalists attacked in LatAm"),
    (50, "Ukraine bonds fall most in emerging markets"),
    (51, "EU-UK summit in Brussels; 3 deals agreed"),
    (52, "Angola pays $180m for 10% of De Beers"),
]

# ALSO metadata: number -> (region, field). The BY FIELD strip, the region
# legend and the header counts are DERIVED from PANELS + ALSO_META, so a swap
# can never leave the displayed counts stale.
ALSO_META = {
    17: ("Europe", "Security"), 18: ("Europe", "Security"),
    19: ("Europe", "Conflict"), 20: ("Europe", "Conflict"),
    21: ("Europe", "Economy"), 22: ("Europe", "Diplomacy"),
    23: ("Americas", "Trade"), 24: ("Asia", "Trade"),
    25: ("Middle East", "Diplomacy"), 26: ("Middle East", "Conflict"),
    27: ("Middle East", "Diplomacy"), 28: ("Americas", "Security"),
    29: ("Americas", "Security"), 30: ("Americas", "Migration"),
    31: ("Americas", "Business"), 32: ("Americas", "Economy"),
    33: ("Africa", "Health & aid"), 34: ("Africa", "Health & aid"),
    35: ("Africa", "Health & aid"), 36: ("Asia", "Courts"),
    37: ("Asia", "Technology"), 38: ("Oceania", "Sport"),
    39: ("Global", "Sport"), 40: ("Europe", "Sport"),
    41: ("Americas", "Technology"), 42: ("Americas", "Security"),
    43: ("Americas", "Courts"), 44: ("Americas", "Politics"),
    45: ("Global", "Space"), 46: ("Asia", "Technology"),
    47: ("Oceania", "Migration"), 48: ("Americas", "Conflict"),
    49: ("Americas", "Politics"), 50: ("Europe", "Markets"),
    51: ("Europe", "Diplomacy"), 52: ("Africa", "Business"),
}

FIELD_ORDER = ["Security", "Conflict", "Technology", "Markets", "Politics",
               "Health & aid", "Diplomacy", "Economy", "Sport", "Trade",
               "Migration", "Courts", "Space", "Business", "Culture",
               "Climate & energy", "Weather"]
REGION_ORDER = ["Europe", "Middle East", "Americas", "Africa", "Asia",
                "Oceania", "Global"]


def story_counts():
    """Derive (region counts, field counts) from PANELS + ALSO_META."""
    from collections import Counter
    rc, fc = Counter(), Counter()
    for _no, region, field, _tag, _src, _hl, _body in PANELS:
        rc[region] += 1
        fc[field] += 1
    for no, _txt in ALSO:
        region, field = ALSO_META[no]
        rc[region] += 1
        fc[field] += 1
    return rc, fc

# Timeline: (UTC hour as float, time label, short label, above?, align).
# align: 'center' (default), 'left' (label starts at the tick) or 'right'
# (label ends at the tick). The 17:00/17:05/17:45 cluster needs explicit
# alignment: 17:00 right + 17:45 left keep the two below-row labels apart,
# 21:00 left keeps it clear of 17:45, 15:03 right keeps it clear of 17:05.
TIMELINE = [
    (1.37, "01:22", "Russia's biggest air attack", True, "right"),
    (2.00, "02:00", "Cyclone Akvan landfall", False, "left"),
    (15.05, "15:03", "US sentiment 51.5", True, "right"),
    (17.00, "17:00", "Trump news conference", False, "right"),
    (17.08, "17:05", "Dragon undocks", True, "center"),
    (17.75, "17:45", "CDC: 5,838 measles cases", False, "left"),
    (19.63, "19:38", "GTA VI $3.79bn", True, "center"),
    (21.00, "21:00", "Nasdaq −5.28%", False, "left"),
]

DATE_CHECK_LEFT = [
    "Shenzhen Trump–Xi–Putin summit (19 Nov)",
    "ICJ Myanmar genocide verdict (19 Nov)",
    "Anthropic IPO debut (19 Nov)",
    "GTA VI release (19 Nov)",
    "Nvidia CEO Huang resigns (12 Nov)",
    "Microsoft outage began (12 Nov)",
    "Brooklyn building collapse (11 Nov)",
    "US loses measles-elimination status (17 Nov)",
    "Berlin Coalition of the Willing summit (19 Nov)",
    "Van Gogh sells for $190.4m (18 Nov)",
]
DATE_CHECK_NOTYET = [
    "COP31 final deal (overtime)",
    "Estonia border closure (1 Dec)",
    "Cargo Dragon splashdown (21 Nov)",
    "Anthropic options trading (23 Nov)",
]

# ---------------------------------------------------------------- illustrations
def illus(draw, kind, x, y, w, h, no):
    """Small labelled illustration drawn with code inside box (x,y,w,h)."""
    draw.rectangle([x, y, x + w, y + h], outline=RULE, width=1)
    if kind == 1:  # Ukraine air attack: night sky, missile trails, bridge
        draw.rectangle([x, y, x + w, y + h], fill=(24, 32, 54))
        for cx, cy in [(x + 20, y + 12), (x + 90, y + 8), (x + 170, y + 16), (x + 210, y + 10)]:
            draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 255, 255))
        for sx, sy, ex, ey in [(x + 10, y + 56, x + 90, y + 18), (x + 60, y + 58, x + 150, y + 14),
                               (x + 130, y + 56, x + 215, y + 20)]:
            draw.line([sx, sy, ex, ey], fill=(255, 180, 60), width=2)
            draw.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(255, 220, 120))
        draw.arc([x + 30, y + 40, x + 120, y + 68], 180, 360, fill=(200, 200, 200), width=3)
        draw.line([x + 30, y + 58, x + 120, y + 58], fill=(200, 200, 200), width=2)
        draw.text((x + 132, y + 50), "KYIV", font=font(SANS_B, 11), fill=(255, 255, 255))
    elif kind == 2:  # GTA VI: skyline + huge sales figure
        draw.rectangle([x, y, x + w, y + h], fill=(16, 60, 40))
        for bx, bw, bh in [(x + 8, 26, 34), (x + 40, 20, 48), (x + 66, 30, 26), (x + 102, 22, 42)]:
            draw.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(30, 90, 60))
            for wy in range(y + h - bh + 5, y + h - 4, 9):
                for wx in range(bx + 4, bx + bw - 4, 8):
                    draw.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 220, 90))
        draw.text((x + 126, y + 8), "$3.79bn", font=font(SANS_B, 22), fill=(120, 255, 170))
        draw.text((x + 130, y + 36), "DAY ONE", font=font(SANS_B, 11), fill=(255, 255, 255))
        draw.text((x + 130, y + 52), "32.5m PRE-ORDERS", font=font(SANS_B, 9), fill=(200, 255, 210))
    elif kind == 3:  # market rout: red falling chart
        draw.rectangle([x, y, x + w, y + h], fill=(255, 244, 242))
        for gy in range(y + 16, y + h - 8, 14):
            draw.line([x + 6, gy, x + w - 6, gy], fill=(232, 220, 218), width=1)
        pts = [(x + 8, y + 22), (x + 50, y + 30), (x + 90, y + 26), (x + 130, y + 42),
               (x + 170, y + 52), (x + 210, y + 60)]
        draw.line(pts, fill=(178, 34, 34), width=3)
        for px, py in pts:
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(178, 34, 34))
        draw.text((x + 8, y + 4), "NASDAQ −5.28%", font=font(SANS_B, 13), fill=(178, 34, 34))
        draw.text((x + 150, y + 4), "S&P −3.7%", font=font(SANS_B, 11), fill=(178, 34, 34))
    elif kind == 4:  # cyclone spiral over coast
        draw.rectangle([x, y, x + w, y + h], fill=(214, 234, 244))
        draw.rectangle([x + 150, y, x + w, y + h], fill=(232, 220, 190))
        draw.line([x + 150, y, x + 150, y + h], fill=(120, 110, 95), width=1)
        cx, cy = x + 78, y + 36
        for r, a0 in [(30, 0), (23, 90), (16, 180), (9, 270)]:
            draw.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 200, fill=(31, 95, 168), width=3)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(31, 95, 168))
        draw.text((x + 156, y + 8), "ODISHA", font=font(SANS_B, 11), fill=INK)
        draw.text((x + 156, y + 24), "GOPALPUR", font=font(SANS_B, 9), fill=FAINT)
        draw.text((x + 156, y + 42), "370,000+", font=font(SANS_B, 13), fill=(178, 34, 34))
        draw.text((x + 156, y + 56), "EVACUATED", font=font(SANS_B, 9), fill=INK)
    elif kind == 5:  # Trump news conference: podium + flags
        draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 218))
        for fx, col in [(x + 14, (178, 34, 34)), (x + 44, (31, 95, 168))]:
            draw.line([fx, y + 8, fx, y + 40], fill=INK, width=2)
            draw.polygon([(fx, y + 8), (fx + 22, y + 14), (fx, y + 20)], fill=col)
        draw.rectangle([x + 100, y + 34, x + 150, y + h - 6], fill=(90, 60, 40))
        draw.rectangle([x + 96, y + 28, x + 154, y + 36], fill=(120, 80, 50))
        draw.ellipse([x + 118, y + 8, x + 132, y + 26], fill=(232, 190, 150))
        draw.text((x + 162, y + 12), "90 MIN", font=font(SANS_B, 16), fill=INK)
        draw.text((x + 162, y + 32), "WHITE HOUSE", font=font(SANS_B, 10), fill=FAINT)
        draw.text((x + 162, y + 48), "“VERY GOOD", font=font(SANS_B, 10), fill=INK)
        draw.text((x + 162, y + 62), "TALKS”", font=font(SANS_B, 10), fill=INK)
    elif kind == 6:  # Nvidia chip, red -14%
        draw.rectangle([x, y, x + w, y + h], fill=(24, 28, 24))
        draw.rectangle([x + 14, y + 14, x + 74, y + h - 14], fill=(40, 90, 50))
        draw.rectangle([x + 26, y + 26, x + 62, y + h - 26], fill=(120, 200, 90))
        draw.text((x + 30, y + 32), "NVDA", font=font(SANS_B, 10), fill=(20, 40, 20))
        for px in range(x + 22, x + 70, 12):
            draw.line([px, y + 8, px, y + 14], fill=(180, 180, 180), width=2)
            draw.line([px, y + h - 14, px, y + h - 8], fill=(180, 180, 180), width=2)
        draw.text((x + 86, y + 10), "−14%", font=font(SANS_B, 26), fill=(255, 90, 70))
        draw.text((x + 88, y + 42), "SEC PROBE", font=font(SANS_B, 11), fill=(255, 255, 255))
        draw.text((x + 88, y + 58), "$125.53 CLOSE", font=font(SANS_B, 9), fill=(200, 200, 200))
    elif kind == 7:  # Anthropic share chart down
        draw.rectangle([x, y, x + w, y + h], fill=(255, 244, 242))
        pts = [(x + 8, y + 14), (x + 60, y + 20), (x + 110, y + 34), (x + 160, y + 44), (x + 215, y + 62)]
        draw.line(pts, fill=(176, 58, 46), width=3)
        for px, py in pts:
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(176, 58, 46))
        draw.text((x + 8, y + 2), "$97.17 → $88.91", font=font(SANS_B, 12), fill=(176, 58, 46))
        draw.text((x + 150, y + 2), "−8.5%", font=font(SANS_B, 12), fill=(176, 58, 46))
        draw.text((x + 8, y + h - 16), "DAY TWO  ·  LOW $83.05", font=font(SANS_B, 9), fill=FAINT)
    elif kind == 8:  # COP31: globe + thermometer + draft paper
        draw.rectangle([x, y, x + w, y + h], fill=(220, 238, 228))
        draw.ellipse([x + 12, y + 10, x + 72, y + 70], fill=(90, 160, 200), outline=(31, 95, 168), width=2)
        draw.ellipse([x + 24, y + 22, x + 44, y + 38], fill=(60, 140, 80))
        draw.ellipse([x + 46, y + 46, x + 62, y + 60], fill=(60, 140, 80))
        draw.rectangle([x + 130, y + 12, x + 230, y + h - 10], fill=(255, 255, 255), outline=RULE)
        draw.text((x + 138, y + 16), "DRAFT DEAL", font=font(SANS_B, 10), fill=INK)
        draw.line([x + 138, y + 32, x + 222, y + 32], fill=(178, 34, 34), width=2)
        draw.text((x + 138, y + 38), "fossil fuels: —", font=font(SANS, 10), fill=(178, 34, 34))
        draw.text((x + 138, y + 52), "$120bn: —", font=font(SANS, 10), fill=(178, 34, 34))
        draw.text((x + 84, y + 12), "COP31", font=font(SANS_B, 13), fill=INK)
        draw.text((x + 84, y + 30), "OVERTIME", font=font(SANS_B, 11), fill=(178, 34, 34))
        draw.text((x + 84, y + 52), "1.5°C OVERSHOOT", font=font(SANS_B, 8), fill=FAINT)
    elif kind == 9:  # Estonia border barrier + flags
        draw.rectangle([x, y, x + w, y + h], fill=(238, 236, 228))
        draw.rectangle([x + 8, y + 40, x + 110, y + 52], fill=(200, 60, 50))
        draw.rectangle([x + 8, y + 52, x + 110, y + 64], fill=(255, 255, 255), outline=RULE)
        for px in (x + 20, x + 60, x + 95):
            draw.line([px, y + 64, px, y + h - 6], fill=INK, width=2)
        draw.text((x + 120, y + 10), "BORDER", font=font(SANS_B, 14), fill=INK)
        draw.text((x + 120, y + 28), "CLOSED", font=font(SANS_B, 14), fill=(178, 34, 34))
        draw.text((x + 120, y + 48), "FROM 1 DEC", font=font(SANS_B, 10), fill=INK)
        draw.text((x + 120, y + 62), "5 CROSSINGS", font=font(SANS_B, 9), fill=FAINT)
        draw.rectangle([x + 170, y + 8, x + 196, y + 22], fill=(31, 95, 168))
        draw.rectangle([x + 170, y + 22, x + 196, y + 30], fill=(20, 20, 20))
        draw.rectangle([x + 170, y + 30, x + 196, y + 40], fill=(255, 255, 255), outline=RULE)
    elif kind == 10:  # gold tumbles: falling bars + price
        draw.rectangle([x, y, x + w, y + h], fill=(250, 242, 210))
        for i, bh in enumerate([44, 34, 24]):
            bx = x + 12 + i * 30
            draw.rectangle([bx, y + h - 8 - bh, bx + 24, y + h - 8],
                           fill=(212, 175, 55), outline=(150, 120, 30))
        draw.text((x + 116, y + 10), "$3,547.90", font=font(SANS_B, 22), fill=(120, 90, 20))
        draw.text((x + 118, y + 38), "GOLD −3.7%", font=font(SANS_B, 13), fill=(178, 34, 34))
        draw.text((x + 118, y + 54), "10-YEAR YIELD 5.04%", font=font(SANS_B, 9), fill=FAINT)
    elif kind == 11:  # Qeshm: island + blast, corrected
        draw.rectangle([x, y, x + w, y + h], fill=(214, 234, 244))
        draw.ellipse([x + 30, y + 18, x + 150, y + 62], fill=(232, 220, 190), outline=RULE)
        draw.text((x + 58, y + 32), "QESHM", font=font(SANS_B, 11), fill=INK)
        for dx, dy in [(0, -12), (10, -4), (-10, -4), (0, 8)]:
            draw.line([x + 170, y + 34, x + 170 + dx, y + 34 + dy], fill=(255, 170, 40), width=3)
        draw.ellipse([x + 164, y + 28, x + 176, y + 40], fill=(255, 200, 60))
        draw.text((x + 190, y + 10), "NOT A", font=font(SANS_B, 12), fill=INK)
        draw.text((x + 190, y + 26), "MISSILE", font=font(SANS_B, 12), fill=(178, 34, 34))
        draw.text((x + 190, y + 44), "MUNITIONS", font=font(SANS_B, 10), fill=INK)
        draw.text((x + 190, y + 58), "DISPOSAL", font=font(SANS_B, 10), fill=INK)
    elif kind == 12:  # measles bars
        draw.rectangle([x, y, x + w, y + h], fill=(255, 250, 240))
        bars = [("JAN", 12), ("MAR", 22), ("JUN", 34), ("SEP", 46), ("NOV", 58)]
        for i, (lbl, bh) in enumerate(bars):
            bx = x + 12 + i * 40
            draw.rectangle([bx, y + h - 16 - bh, bx + 26, y + h - 16], fill=(176, 58, 46) if i == 4 else (200, 120, 110))
            draw.text((bx + 2, y + h - 14), lbl, font=font(SANS, 8), fill=FAINT)
        draw.text((x + 8, y + 4), "5,838 CASES", font=font(SANS_B, 14), fill=(176, 58, 46))
        draw.text((x + 130, y + 6), "CDC · 19 NOV", font=font(SANS_B, 10), fill=INK)
        draw.text((x + 130, y + 22), "+7.9% IN A WEEK", font=font(SANS, 9), fill=FAINT)
        draw.text((x + 130, y + 36), "6 DEATHS IN 2026", font=font(SANS, 9), fill=FAINT)
    elif kind == 13:  # cyber director shield
        draw.rectangle([x, y, x + w, y + h], fill=(232, 236, 244))
        draw.polygon([(x + 40, y + 8), (x + 74, y + 16), (x + 74, y + 44), (x + 40, y + 68),
                      (x + 6, y + 44), (x + 6, y + 16)], fill=(31, 95, 168))
        draw.text((x + 28, y + 26), "✓", font=font(SANS_B, 22), fill=(255, 255, 255))
        draw.text((x + 90, y + 10), "NEW CYBER", font=font(SANS_B, 13), fill=INK)
        draw.text((x + 90, y + 28), "DIRECTOR", font=font(SANS_B, 13), fill=INK)
        draw.text((x + 90, y + 48), "KIRSTEN DAVIES", font=font(SANS_B, 10), fill=FAINT)
        draw.text((x + 90, y + 62), "PENTAGON CIO", font=font(SANS_B, 9), fill=FAINT)
    elif kind == 14:  # Xi–Albanese: two flags + handshake
        draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 220))
        draw.rectangle([x + 12, y + 12, x + 92, y + 46], fill=(222, 40, 40))
        for sx, sy in [(x + 24, y + 20), (x + 36, y + 16), (x + 36, y + 26), (x + 48, y + 20)]:
            draw.text((sx, sy), "★", font=font(SANS_B, 9), fill=(255, 220, 60))
        draw.rectangle([x + 104, y + 12, x + 184, y + 46], fill=(31, 95, 168))
        for sx in range(x + 112, x + 178, 10):
            draw.text((sx, y + 18), "★", font=font(SANS_B, 8), fill=(255, 255, 255))
        draw.text((x + 12, y + 52), "CHINA × AUSTRALIA", font=font(SANS_B, 10), fill=INK)
        draw.text((x + 150, y + 52), "SHENZHEN", font=font(SANS_B, 10), fill=(178, 34, 34))
    elif kind == 15:  # sentiment gauge
        draw.rectangle([x, y, x + w, y + h], fill=(240, 244, 238))
        draw.arc([x + 30, y + 10, x + 130, y + 74], 180, 360, fill=(120, 120, 120), width=8)
        draw.arc([x + 30, y + 10, x + 130, y + 74], 180, 260, fill=(30, 132, 73), width=8)
        draw.line([x + 80, y + 42, x + 108, y + 22], fill=(178, 34, 34), width=3)
        draw.text((x + 140, y + 8), "51.5", font=font(SANS_B, 22), fill=(30, 132, 73))
        draw.text((x + 140, y + 36), "UP FROM 48.0", font=font(SANS_B, 10), fill=INK)
        draw.text((x + 140, y + 52), "INFLATION 3.7%", font=font(SANS_B, 9), fill=FAINT)
        draw.text((x + 30, y + 60), "CONSUMER SENTIMENT", font=font(SANS_B, 8), fill=FAINT)
    elif kind == 16:  # Cargo Dragon + ISS
        draw.rectangle([x, y, x + w, y + h], fill=(16, 20, 44))
        for cx, cy in [(x + 20, y + 10), (x + 70, y + 16), (x + 140, y + 8), (x + 200, y + 14)]:
            draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 255, 255))
        draw.rectangle([x + 12, y + 34, x + 84, y + 42], fill=(150, 150, 170))
        draw.rectangle([x + 88, y + 30, x + 118, y + 46], fill=(200, 200, 210))
        draw.rectangle([x + 118, y + 34, x + 190, y + 42], fill=(150, 150, 170))
        draw.polygon([(x + 150, y + 52), (x + 170, y + 52), (x + 166, y + 68), (x + 154, y + 68)], fill=(220, 220, 230))
        draw.text((x + 190, y + 52), "DRAGON", font=font(SANS_B, 10), fill=(255, 255, 255))
        draw.text((x + 12, y + 56), "CRS-35 · UNDOCKED 17:05 UTC", font=font(SANS_B, 9), fill=(180, 200, 255))


def small_illus(draw, kind, x, y, w, h):
    """Compact icon strip for the 12 small panels (same kinds, simpler)."""
    bg = {1: (24, 32, 54), 2: (16, 60, 40), 3: (255, 244, 242), 4: (214, 234, 244),
          5: (238, 232, 218), 6: (24, 28, 24), 7: (255, 244, 242), 8: (220, 238, 228),
          9: (238, 236, 228), 10: (250, 242, 210), 11: (214, 234, 244), 12: (255, 250, 240),
          13: (232, 236, 244), 14: (238, 232, 220), 15: (240, 244, 238), 16: (16, 20, 44)}[kind]
    draw.rectangle([x, y, x + w, y + h], fill=bg, outline=RULE)
    cx = x + w // 2
    if kind in (1, 19):
        draw.line([x + 6, y + h - 8, cx, y + 8], fill=(255, 180, 60), width=2)
        draw.line([cx, y + 8, x + w - 6, y + h - 8], fill=(255, 180, 60), width=2)
        draw.text((x + 6, y + h - 16), "110+ MISSILES", font=font(SANS_B, 8), fill=(255, 255, 255))
    elif kind == 5:
        draw.rectangle([cx - 14, y + 18, cx + 14, y + h - 4], fill=(90, 60, 40))
        draw.ellipse([cx - 8, y + 4, cx + 8, y + 18], fill=(232, 190, 150))
        draw.text((x + 4, y + h - 14), "90 MIN", font=font(SANS_B, 8), fill=INK)
    elif kind == 6:
        draw.rectangle([cx - 22, y + 8, cx + 22, y + h - 8], fill=(40, 90, 50))
        draw.text((cx - 14, y + 12), "NVDA", font=font(SANS_B, 9), fill=(120, 200, 90))
        draw.text((cx - 14, y + 26), "−14%", font=font(SANS_B, 11), fill=(255, 90, 70))
    elif kind == 7:
        draw.line([(x + 6, y + 10), (x + w // 2, y + 22), (x + w - 6, y + h - 8)], fill=(176, 58, 46), width=3)
        draw.text((x + 6, y + h - 14), "$88.91", font=font(SANS_B, 9), fill=(176, 58, 46))
    elif kind == 8:
        draw.ellipse([cx - 16, y + 6, cx + 16, y + 38], fill=(90, 160, 200))
        draw.text((x + 4, y + h - 14), "DRAFT: NO FOSSIL FUELS", font=font(SANS_B, 7), fill=INK)
    elif kind == 9:
        draw.rectangle([x + 8, y + 12, x + w - 8, y + 20], fill=(200, 60, 50))
        draw.text((x + 8, y + 24), "CLOSED 1 DEC", font=font(SANS_B, 9), fill=INK)
    elif kind == 10:
        for i, bh in enumerate([30, 22, 14]):
            bx = x + 10 + i * 26
            draw.rectangle([bx, y + h - 8 - bh, bx + 18, y + h - 8],
                           fill=(212, 175, 55), outline=(150, 120, 30))
        draw.text((x + 94, y + 6), "$3,547.90", font=font(SANS_B, 10), fill=(120, 90, 20))
        draw.text((x + 94, y + 22), "GOLD −3.7%", font=font(SANS_B, 9), fill=(178, 34, 34))
    elif kind == 11:
        draw.ellipse([cx - 26, y + 8, cx + 26, y + 30], fill=(232, 220, 190), outline=RULE)
        draw.text((cx - 18, y + 14), "QESHM", font=font(SANS_B, 8), fill=INK)
        draw.text((x + 4, y + h - 14), "NOT A MISSILE", font=font(SANS_B, 8), fill=(178, 34, 34))
    elif kind == 12:
        for i, bh in enumerate([8, 14, 20, 28]):
            bx = x + 10 + i * 22
            draw.rectangle([bx, y + h - 8 - bh, bx + 16, y + h - 8], fill=(176, 58, 46))
        draw.text((x + 6, y + 2), "5,838", font=font(SANS_B, 11), fill=(176, 58, 46))
    elif kind == 13:
        draw.polygon([(cx, y + 4), (cx + 14, y + 10), (cx + 14, y + 26), (cx, y + 38),
                      (cx - 14, y + 26), (cx - 14, y + 10)], fill=(31, 95, 168))
        draw.text((cx - 4, y + 12), "✓", font=font(SANS_B, 12), fill=(255, 255, 255))
    elif kind == 14:
        draw.rectangle([x + 8, y + 8, x + w // 2 - 2, y + 28], fill=(222, 40, 40))
        draw.rectangle([x + w // 2 + 2, y + 8, x + w - 8, y + 28], fill=(31, 95, 168))
        draw.text((x + 6, y + h - 14), "SHENZHEN", font=font(SANS_B, 8), fill=INK)
    elif kind == 15:
        draw.arc([cx - 24, y + 6, cx + 24, y + 40], 180, 360, fill=(30, 132, 73), width=5)
        draw.text((cx - 16, y + 12), "51.5", font=font(SANS_B, 12), fill=(30, 132, 73))
    elif kind == 16:
        draw.rectangle([x + 8, y + 16, x + w - 8, y + 24], fill=(150, 150, 170))
        draw.polygon([(cx - 8, y + 28), (cx + 8, y + 28), (cx + 5, y + 40), (cx - 5, y + 40)], fill=(220, 220, 230))
        draw.text((x + 4, y + 2), "CRS-35", font=font(SANS_B, 8), fill=(255, 255, 255))

SHORT_BODY = {
    5: "Hails “very good talks” with Putin; touts Thai, Philippine deals.",
    6: "Worst day in ~2 years on reports of an SEC probe. Closed at $125.53.",
    7: "Nearly erasing its debut gain; touched $83.05, five cents above the $83 IPO price. Worth ~$1.16 trillion.",
    8: "Revised deal drops all fossil-fuel wording and a $120bn adaptation target; talks head for overtime.",
    9: "Five crossings shut for six months; Moscow cries “new Iron Curtain.”",
    10: "Investors flee to bonds; the 10-year yield eases to 5.04%.",
    11: "Tasnim: the blast was unexploded ordnance, not a missile strike.",
    12: "Up 7.9% in a week; six deaths in 2026. First update since the US lost measles-elimination status on 17 Nov.",
    13: "Pentagon CIO Kirsten Davies takes the acting role, replacing Sean Cairncross, fired on Thursday.",
    14: "“Comprehensive turnaround” in China–Australia ties, Xi says. Albanese pushes beef and rice.",
    15: "Up from 48.0 as one-year inflation expectations ease to 3.7% from 4.7%, the final Michigan survey shows.",
    16: "CRS-35 leaves with time-sensitive science; splashdown is due off California on Saturday 21 November.",
}

# ---------------------------------------------------------------- world map
EURASIA = [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (10, 59), (18, 56), (24, 59),
           (30, 60), (35, 66), (45, 68), (60, 69), (75, 73), (95, 76), (115, 73), (135, 72),
           (155, 70), (170, 66), (178, 65), (165, 60), (158, 52), (142, 45), (135, 43),
           (128, 38), (122, 30), (118, 24), (108, 18), (105, 9), (100, 7), (97, 15),
           (92, 21), (88, 22), (82, 16), (77, 8), (74, 15), (70, 20), (66, 25), (61, 25),
           (57, 26), (52, 28), (48, 30), (43, 29), (39, 31), (36, 36), (30, 36), (27, 40),
           (23, 36), (19, 40), (12, 44), (3, 43), (-2, 37), (-9, 37)]
N_AMERICA = [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60), (-55, 47),
             (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
             (-125, 40), (-125, 49), (-145, 60), (-165, 60)]
GREENLAND = [(-55, 60), (-45, 60), (-40, 70), (-55, 75), (-60, 70)]
S_AMERICA = [(-80, 10), (-70, 12), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
             (-58, -35), (-65, -45), (-70, -52), (-73, -40), (-80, -20), (-80, -5)]
AFRICA = [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15),
          (43, 11), (48, 10), (51, 2), (40, -5), (40, -15), (35, -25), (28, -33), (20, -35),
          (15, -27), (12, -18), (13, -10), (9, 4), (-8, 4)]
AUSTRALIA = [(114, -22), (114, -30), (115, -35), (120, -34), (129, -32), (135, -35), (140, -38),
             (145, -38), (150, -37), (153, -27), (146, -19), (142, -11), (136, -12), (132, -12),
             (126, -14), (122, -17), (118, -20)]
# (lat, lon, dx, dy) for panels 1–16
PINS = {
    1: (50.45, 30.52, 0, 0), 2: (55.95, -3.19, 0, 0), 3: (40.71, -74.0, 0, 0),
    4: (19.27, 84.92, 0, 0), 5: (38.9, -77.04, 0, 0), 6: (37.35, -121.95, 0, 0),
    7: (37.77, -122.42, -12, 10), 8: (36.9, 30.7, 0, 0), 9: (59.44, 24.75, 0, 0),
    10: (51.51, -0.13, 10, 10), 11: (26.95, 56.27, 0, 0), 12: (33.75, -84.39, 0, 0),  # 10: London (LBMA gold); offset clears pin 2
    13: (38.9, -77.04, 14, -10), 14: (22.55, 114.06, 0, 0), 15: (42.28, -83.74, 0, 0),
    16: (28.5, -80.6, 0, 0),
}


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(216, 232, 240), outline=RULE)
    def proj(lon, lat):
        px = x + (lon + 180) / 360.0 * w
        py = y + (75 - lat) / 135.0 * h
        return (px, py)
    for poly in (EURASIA, N_AMERICA, GREENLAND, S_AMERICA, AFRICA, AUSTRALIA):
        draw.polygon([proj(lon, lat) for lon, lat in poly], fill=(232, 224, 196), outline=(150, 140, 120))
    for no, (lat, lon, dx, dy) in PINS.items():
        px, py = proj(lon, lat)
        px += dx
        py += dy
        region = [pp[1] for pp in PANELS if pp[0] == no][0]
        col = REGION_COLOR[region]
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=col, outline=(255, 255, 255), width=1)
        t = str(no)
        tw = draw.textlength(t, font=font(SANS_B, 8))
        draw.text((px - tw / 2, py - 6), t, font=font(SANS_B, 8), fill=(255, 255, 255))


# ---------------------------------------------------------------- panels
def tag_pill(draw, x, y, tag, fnt):
    tw = draw.textlength(tag, font=fnt) + 8
    draw.rounded_rectangle([x, y, x + tw, y + 12], radius=6, fill=TAG_FILL[tag])
    draw.text((x + 4, y + 1), tag, font=fnt, fill=(255, 255, 255))
    return tw


def big_panel(draw, p, x, y, w, h):
    no, region, field, tag, src, headline, body = p
    col = REGION_COLOR[region]
    draw.rectangle([x, y, x + w, y + h], outline=RULE, width=1)
    draw.rectangle([x, y, x + w, y + 3], fill=col)
    illus(draw, no, x + 4, y + 7, w - 8, 62, no)
    my = y + 73
    draw.ellipse([x + 4, my, x + 18, my + 14], fill=col)
    t = str(no)
    tw = draw.textlength(t, font=font(SANS_B, 10))
    draw.text((x + 11 - tw / 2, my + 1), t, font=font(SANS_B, 10), fill=(255, 255, 255))
    draw.text((x + 22, my + 1), f"{region.upper()} · {field.upper()}",
              font=font(SANS_B, 9), fill=INK)
    tag_pill(draw, x + w - 78, my + 1, tag, font(SANS_B, 8))
    hy = my + 17
    lines = fit(draw, headline, font(SERIF_B, 12), w - 10, 2, f"big headline {no}")
    draw_lines(draw, lines, x + 5, hy, font(SERIF_B, 12), INK, 14.5)
    by = hy + len(lines) * 14.5 + 2
    blines = fit(draw, body, font(SANS, 9), w - 10, 3, f"big body {no}")
    draw_lines(draw, blines, x + 5, by, font(SANS, 9), (45, 45, 45), 11.5)
    draw.text((x + 5, y + h - 12), src, font=font(SANS, 8), fill=FAINT)


def small_panel(draw, p, x, y, w, h):
    no, region, field, tag, src, headline, body = p
    col = REGION_COLOR[region]
    draw.rectangle([x, y, x + w, y + h], outline=RULE, width=1)
    draw.rectangle([x, y, x + w, y + 3], fill=col)
    small_illus(draw, no, x + 4, y + 6, w - 8, 42)
    my = y + 52
    draw.ellipse([x + 4, my, x + 16, my + 12], fill=col)
    t = str(no)
    tw = draw.textlength(t, font=font(SANS_B, 9))
    draw.text((x + 10 - tw / 2, my), t, font=font(SANS_B, 9), fill=(255, 255, 255))
    draw.text((x + 19, my + 1), f"{region.upper()} · {field.upper()}",
              font=font(SANS_B, 7.5), fill=INK)
    hy = my + 14
    lines = fit(draw, headline, font(SERIF_B, 10.5), w - 8, 3, f"small headline {no}")
    draw_lines(draw, lines, x + 4, hy, font(SERIF_B, 10.5), INK, 12.5)
    by = hy + len(lines) * 12.5 + 1
    sbody = SHORT_BODY[no]
    blines = fit(draw, sbody, font(SANS, 8), w - 8, 3, f"small body {no}")
    draw_lines(draw, blines, x + 4, by, font(SANS, 8), (45, 45, 45), 10)
    # tag pill + source at the bottom (short outlet only — full source in README)
    ty = y + h - 13
    twp = tag_pill(draw, x + 4, ty, tag, font(SANS_B, 7))
    s = SHORT_SRC[no]
    draw.text((x + 8 + twp, ty + 1), s, font=font(SANS, 7.5), fill=FAINT)


SHORT_SRC = {5: "Reuters", 6: "Reuters", 7: "Nasdaq tape", 8: "Reuters",
             9: "Reuters", 10: "Motley Fool", 11: "Reuters", 12: "CDC",
             13: "Bloomberg", 14: "Xinhua", 15: "U. Michigan", 16: "NASA"}


# ---------------------------------------------------------------- whole image
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # counts are derived from the story data; a swap can never leave them stale
    rc, fc = story_counts()
    n_total = len(PANELS) + len(ALSO)
    if (n_total, len(rc), len(fc)) != (52, 7, 17):
        WARNINGS.append(
            f"COUNT MISMATCH: {n_total} stories, {len(rc)} regions, "
            f"{len(fc)} fields (expected 52/7/17)")

    # kicker
    d.text((10, 6), "ONE DAY OF WORLD NEWS, ONE PICTURE", font=font(SANS_B, 10.5), fill=RED)
    right = (f"{n_total} STORIES · {len(rc)} REGIONS · {len(fc)} FIELDS · "
             "EVERY ONE FROM THIS FRIDAY")
    d.text((W - 10 - d.textlength(right, font=font(SANS_B, 10.5)), 6), right,
           font=font(SANS_B, 10.5), fill=INK)
    d.line([10, 22, W - 10, 22], fill=RULE, width=1)

    # masthead
    mast = "Friday 20 November 2026"
    mf = font(SERIF_B, 52)
    d.text(((W - d.textlength(mast, font=mf)) / 2, 24), mast, font=mf, fill=INK)

    # BY FIELD strip (two lines)
    fy = 80
    d.rectangle([10, fy, 82, fy + 22], fill=INK)
    d.text((15, fy + 5), "BY FIELD", font=font(SANS_B, 10), fill=(255, 255, 255))
    fields = sorted(
        ((f, fc[f]) for f in FIELD_ORDER if fc[f] > 0),
        key=lambda t: (-t[1], FIELD_ORDER.index(t[0])))
    line1 = "  ·  ".join(f"{n} {c}" for n, c in fields[:9])
    line2 = "  ·  ".join(f"{n} {c}" for n, c in fields[9:])
    d.text((88, fy), line1, font=font(SANS, 9.5), fill=INK)
    d.text((88, fy + 11), line2, font=font(SANS, 9.5), fill=INK)
    d.line([10, fy + 24, W - 10, fy + 24], fill=RULE, width=1)

    # timeline
    ty = 104
    d.rectangle([10, ty, 84, ty + 36], fill=RED)
    d.text((14, ty + 4), "THE DAY", font=font(SANS_B, 10), fill=(255, 255, 255))
    d.text((14, ty + 17), "IN UTC", font=font(SANS_B, 10), fill=(255, 255, 255))
    ax0, ax1 = 92, W - 10
    ay = ty + 24
    d.line([ax0, ay, ax1, ay], fill=INK, width=2)
    for hh in (0, 6, 12, 18, 24):
        tx = ax0 + hh / 24 * (ax1 - ax0)
        d.line([tx, ay - 4, tx, ay + 4], fill=INK, width=1)
    # event ticks with staggered labels (above/below + align per event)
    for hr, tlab, desc, is_above, align in TIMELINE:
        tx = ax0 + hr / 24 * (ax1 - ax0)
        d.line([tx, ay - 6, tx, ay + 6], fill=RED, width=2)
        d.ellipse([tx - 3, ay - 3, tx + 3, ay + 3], fill=RED)
        tf = font(SANS_B, 9.5)
        df = font(SANS, 8.5)
        dw = max(d.textlength(tlab, font=tf), d.textlength(desc, font=df))
        if align == "right":
            lx = tx - dw - 4
        elif align == "left":
            lx = tx + 4
        else:
            lx = tx - dw / 2
        lx = max(ax0, min(lx, ax1 - dw))
        if is_above:
            d.text((lx, ty), tlab, font=tf, fill=RED)
            d.text((lx, ty + 11), desc, font=df, fill=INK)
        else:
            d.text((lx, ay + 8), tlab, font=tf, fill=RED)
            d.text((lx, ay + 19), desc, font=df, fill=INK)
    d.line([10, ty + 56, W - 10, ty + 56], fill=RULE, width=1)

    # 4 big panels
    bx, by, bw, bh, gap = 10, 164, 246, 168, 6
    for i, p in enumerate(PANELS[:4]):
        big_panel(d, p, bx + i * (bw + gap), by, bw, bh)

    # 12 small panels, 2 rows x 6
    sx, sw, sh = 10, 162, 140
    for r in range(2):
        for c in range(6):
            p = PANELS[4 + r * 6 + c]
            small_panel(d, p, sx + c * (sw + gap), 336 + r * (sh + 4), sw, sh)

    # bottom: map + ALSO
    bot_y = 624
    d.text((10, bot_y), "WHERE IT HAPPENED", font=font(SANS_B, 11), fill=RED)
    d.text((308, bot_y), "ALSO ON FRIDAY 20 NOVEMBER", font=font(SANS_B, 11), fill=RED)
    d.line([10, bot_y + 16, 300, bot_y + 16], fill=RULE, width=1)
    d.line([308, bot_y + 16, W - 10, bot_y + 16], fill=RULE, width=1)
    draw_map(d, 10, bot_y + 20, 290, 158)
    # region legend
    ly = bot_y + 182
    regs = [(r, rc[r]) for r in REGION_ORDER if rc[r] > 0]
    for i, (rn, cnt) in enumerate(regs):
        cx = 10 + (i % 4) * 74
        cy = ly + (i // 4) * 13
        d.ellipse([cx, cy + 1, cx + 8, cy + 9], fill=REGION_COLOR[rn])
        d.text((cx + 11, cy), f"{rn} {cnt}", font=font(SANS, 8.5), fill=INK)
    # HOW SURE box
    hy = bot_y + 210
    d.rectangle([10, hy, 300, hy + 62], outline=RULE, width=1)
    d.text((16, hy + 3), "HOW SURE", font=font(SANS_B, 9), fill=RED)
    sure = ("CONFIRMED  2+ outlets   ·   OFFICIAL  the body itself   ·   "
            "REPORTED  one outlet   ·   CLAIM  one side   ·   FORECAST  expected")
    slines = fit(d, sure, font(SANS, 8), 278, 3, "how sure")
    draw_lines(d, slines, 16, hy + 16, font(SANS, 8), INK, 11)
    d.text((16, hy + 50), "Tags on every panel. CLAIM and FORECAST not used today.",
           font=font(SANS, 7.5), fill=FAINT)

    # ALSO 17–52 in 3 columns x 12 rows
    ax, ay0, acw = 308, bot_y + 20, 230
    for col_i in range(3):
        items = ALSO[col_i * 12:(col_i + 1) * 12]
        for ri, (no, txt) in enumerate(items):
            iy = ay0 + ri * 21.5
            d.text((ax + col_i * (acw + 8), iy), str(no), font=font(SANS_B, 9), fill=RED)
            nx = ax + col_i * (acw + 8) + (20 if no < 100 else 20)
            lines = fit(d, txt, font(SANS, 8.5), acw - 22, 1, f"also {no}")
            d.text((nx, iy), lines[0], font=font(SANS, 8.5), fill=INK)

    # DATE CHECK footer
    dy = 900
    d.rectangle([10, dy, W - 10, dy + 62], outline=RED, width=2)
    d.rectangle([10, dy, 128, dy + 16], fill=RED)
    d.text((16, dy + 2), "DATE CHECK", font=font(SANS_B, 10), fill=(255, 255, 255))
    left_txt = "Left out on purpose — they happened before Friday 20 November:  " + \
        "  ·  ".join(f"{t}" for t in DATE_CHECK_LEFT) + "."
    ll = fit(d, left_txt, font(SANS, 8.5), W - 32, 2, "date check left")
    draw_lines(d, ll, 16, dy + 19, font(SANS, 8.5), INK, 11)
    notyet = "Not yet:  " + "  ·  ".join(DATE_CHECK_NOTYET) + "."
    nl = fit(d, notyet, font(SANS, 8.5), W - 32, 1, "date check notyet")
    d.text((16, dy + 19 + len(ll) * 11 + 2), nl[0], font=font(SANS_B, 8.5), fill=DARKRED)

    # claim + sources
    cy = 968
    claim = "Every story here happened, or was first reported, on Friday 20 November 2026."
    d.text(((W - d.textlength(claim, font=font(SERIF, 11))) / 2, cy), claim,
           font=font(SERIF, 11), fill=INK)
    srcs = ("Sources: Reuters, CNN, BBC, AP, WSJ, Bloomberg, AFP, UN News, WHO, CDC, "
            "Univ. of Michigan, IMD, NASA, Xinhua, Tass, h.ua. Original drawings.")
    d.text(((W - d.textlength(srcs, font=font(SANS, 8))) / 2, cy + 15), srcs,
           font=font(SANS, 8), fill=FAINT)
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = build()
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"entry.png: {size} bytes, sha256 {sha}")
    print(f"size ok (<=1048576): {size <= 1048576}")
    if WARNINGS:
        print(f"WARNINGS ({len(WARNINGS)}):")
        for wmsg in WARNINGS:
            print("  " + wmsg)
    else:
        print("WARNINGS: none — no overflow detected")


if __name__ == "__main__":
    main()
