#!/usr/bin/env python3
"""Generate assets/stage/*.svg and README.md from profile.config.json + assets/profile.json.
Stdlib only. Theme: CodeLovers (near-black #05060f, rose accent, mono type)."""
import json, os, textwrap
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "profile.config.json")))
try:
    DATA = json.load(open(os.path.join(ROOT, "assets", "profile.json")))
except FileNotFoundError:
    DATA = {"stats": {"repos": 0, "stars": 0, "followers": 0}, "posts": []}
OUT = os.path.join(ROOT, "assets", "stage")
os.makedirs(OUT, exist_ok=True)

BG, PANEL, LINE = "#05060f", "#0b0d1c", "#1e2236"
FG, MUTED, ROSE, ROSE_L = "#ededed", "#8b93ad", "#e11d48", "#fb7185"
MONO = "ui-monospace,'Geist Mono',SFMono-Regular,Menlo,Consolas,monospace"
SANS = "'Geist',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif"
W = 900

STYLE = f"""<style>
text{{font-family:{MONO}}}
.s{{font-family:{SANS}}}
.in{{animation:in .6s ease-out both}}
@keyframes in{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
.blink{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.glow{{animation:glow 4s ease-in-out infinite alternate}}
@keyframes glow{{from{{opacity:.55}}to{{opacity:1}}}}
.mq{{animation:mq 28s linear infinite}}
@keyframes mq{{to{{transform:translateX(-50%)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""

DEFS = f"""<defs>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{LINE}" stroke-width="1" opacity=".55"/></pattern>
<radialGradient id="g1" cx="85%" cy="0%" r="70%"><stop offset="0" stop-color="{ROSE}" stop-opacity=".38"/><stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></radialGradient>
<radialGradient id="g2" cx="0%" cy="100%" r="60%"><stop offset="0" stop-color="#6366f1" stop-opacity=".22"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></radialGradient>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{ROSE}"/><stop offset="1" stop-color="{ROSE_L}"/></linearGradient>
</defs>"""


def svg(name, h, body, label):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" '
         f'aria-label="{escape(label, {chr(34): "&quot;"})}"><title>{escape(label)}</title>{STYLE}{DEFS}'
         f'<rect width="{W}" height="{h}" rx="14" fill="{BG}"/>{body}'
         f'<rect x=".5" y=".5" width="{W-1}" height="{h-1}" rx="14" fill="none" stroke="{LINE}"/></svg>')
    open(os.path.join(OUT, name), "w").write(s)


def wrap(text, width, max_lines=None):
    lines = textwrap.wrap(text, width)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,; ")[: width - 1] + "…"
    return lines


def lines_svg(lines, x, y, size, fill, lh, cls="", sans=False):
    c = ' class="s"' if sans else ""
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text{c} x="{x}" y="{y + i*lh}" font-size="{size}" fill="{fill}">{escape(ln)}</text>')
    return f'<g class="{cls}">' + "".join(out) + "</g>"


# ---------- hero ----------
def hero():
    st = DATA["stats"]
    h = 340
    first, last = CFG["name"]
    b = f'<rect width="{W}" height="{h}" fill="url(#grid)"/><rect width="{W}" height="{h}" fill="url(#g1)" class="glow"/><rect width="{W}" height="{h}" fill="url(#g2)"/>'
    b += f'<text x="48" y="58" font-size="14" fill="{ROSE_L}" letter-spacing="3" class="in">&gt; {escape(CFG["role"])} · {escape(CFG["location"])}<tspan class="blink">_</tspan></text>'
    b += f'<text class="s in" x="46" y="140" font-size="68" font-weight="800" fill="{FG}" letter-spacing="-2" style="animation-delay:.1s">{first}</text>'
    b += f'<text class="s in" x="46" y="212" font-size="68" font-weight="800" fill="{ROSE}" letter-spacing="-2" style="animation-delay:.2s">{last}</text>'
    # stack chips
    x = 48
    for t in CFG["stack"]:
        w = 20 + len(t) * 9
        b += f'<g class="in" style="animation-delay:.35s"><rect x="{x}" y="240" width="{w}" height="28" rx="14" fill="{PANEL}" stroke="{LINE}"/><text x="{x + w/2}" y="259" font-size="12" fill="{FG}" text-anchor="middle" letter-spacing="1">{t}</text></g>'
        x += w + 10
    # stats panel
    items = [("YEARS", CFG["metrics"][0]["value"]), ("PROJECTS", CFG["metrics"][1]["value"]),
             ("SAAS", CFG["metrics"][2]["value"]), ("PUBLIC REPOS", str(st["repos"]))]
    if st["stars"] > 0:
        items.append(("STARS", str(st["stars"])))
    px, py = 640, 70
    b += f'<rect x="{px}" y="{py}" width="216" height="{len(items)*40+24}" rx="12" fill="{PANEL}" fill-opacity=".85" stroke="{LINE}"/>'
    for i, (k, v) in enumerate(items):
        yy = py + 40 + i * 40
        b += f'<text x="{px+18}" y="{yy}" font-size="11" fill="{MUTED}" letter-spacing="2">{k}</text>'
        b += f'<text class="s" x="{px+198}" y="{yy+2}" font-size="22" font-weight="700" fill="{FG}" text-anchor="end">{escape(v)}</text>'
        if i < len(items) - 1:
            b += f'<line x1="{px+18}" x2="{px+198}" y1="{yy+14}" y2="{yy+14}" stroke="{LINE}"/>'
    b += f'<rect x="0" y="{h-6}" width="{W}" height="6" fill="url(#bar)" opacity=".9"/>'
    svg("hero.svg", h, b, f"{first.title()} {last.title()}, {CFG['role'].title()}. {st['repos']} public repos.")


# ---------- about ----------
def about():
    ls = wrap(CFG["about"], 88)
    h = 70 + len(ls) * 28
    b = f'<rect x="0" y="0" width="6" height="{h}" fill="url(#bar)"/>'
    b += f'<text x="40" y="42" font-size="12" fill="{ROSE_L}" letter-spacing="3">// ABOUT</text>'
    b += lines_svg(ls, 40, 78, 17, FG, 28, "in", sans=True)
    svg("about.svg", h, b, CFG["about"])


# ---------- section heading ----------
def heading(name, idx, title):
    b = f'<rect width="{W}" height="64" fill="url(#grid)"/>'
    b += f'<text x="28" y="40" font-size="13" fill="{ROSE_L}" letter-spacing="3">{idx}</text>'
    b += f'<text class="s" x="76" y="42" font-size="24" font-weight="700" fill="{FG}" letter-spacing="1">{escape(title)}</text>'
    b += f'<rect x="{W-120}" y="31" width="92" height="3" rx="1.5" fill="url(#bar)"/>'
    svg(name, 64, b, title)


# ---------- target card ----------
def target(i, t):
    h = 112
    desc = wrap(t["desc"], 80, 2)
    b = f'<rect x="0" y="0" width="{W}" height="{h}" fill="{PANEL}" rx="14"/><rect x="0" y="0" width="5" height="{h}" fill="{ROSE}"/>'
    b += f'<text x="32" y="38" font-size="12" fill="{MUTED}" letter-spacing="2">{i+1:02d}</text>'
    b += f'<text class="s" x="70" y="42" font-size="22" font-weight="700" fill="{FG}" letter-spacing=".5">{escape(t["label"])}</text>'
    tag = t["tag"]
    tw = 22 + len(tag) * 8
    b += f'<rect x="{W-tw-28}" y="22" width="{tw}" height="26" rx="13" fill="none" stroke="{ROSE}"/><text x="{W-tw/2-28}" y="39" font-size="11" fill="{ROSE_L}" text-anchor="middle" letter-spacing="1.5">{escape(tag)}</text>'
    b += lines_svg(desc, 70, 72, 14, MUTED, 22, sans=True)
    b += f'<text x="{W-32}" y="{h-18}" font-size="12" fill="{ROSE_L}" text-anchor="end" letter-spacing="2">OPEN →</text>'
    svg(f"target-{i}.svg", h, b, f'{t["label"]}: {t["desc"]}')


# ---------- post ----------
def post(i, p):
    h = 84
    ttl = wrap(p["title"], 62, 1)[0]
    b = f'<rect width="{W}" height="{h}" fill="{PANEL}" rx="14"/>'
    b += f'<text x="28" y="34" font-size="11" fill="{ROSE_L}" letter-spacing="2">NEW · {escape(p["date"].upper())}</text>'
    b += f'<text class="s" x="28" y="62" font-size="19" font-weight="600" fill="{FG}">{escape(ttl)}</text>'
    b += f'<text x="{W-28}" y="50" font-size="18" fill="{ROSE}" text-anchor="end">→</text>'
    svg(f"post-{i}.svg", h, b, p["title"])


def all_posts():
    b = f'<rect width="{W}" height="52" fill="{PANEL}" rx="14"/><text x="{W/2}" y="32" font-size="13" fill="{ROSE_L}" text-anchor="middle" letter-spacing="3">ALL POSTS · WEARECODELOVERS.COM/BLOG →</text>'
    svg("all-posts.svg", 52, b, "All posts on wearecodelovers.com")


def contact(c):
    w = 30 + len(c["label"]) * 10
    name = "contact-" + c["label"].lower().replace(" ", "-") + ".svg"
    b = f'<rect x="1" y="1" width="{w-2}" height="44" rx="22" fill="{PANEL}" stroke="{ROSE}"/><text x="{w/2}" y="28" font-size="13" fill="{FG}" text-anchor="middle" letter-spacing="2">{escape(c["label"])}</text>'
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 46" width="{w}" height="46" role="img" aria-label="{escape(c["label"])}">'
         f'<style>text{{font-family:{MONO}}}</style>{b}</svg>')
    open(os.path.join(OUT, name), "w").write(s)
    return name


def ticker():
    st = DATA["stats"]
    seg = ["SHIPPING FROM MOROCCO", "MULTI-TENANT SAAS", "IOT · MQTT · REAL-TIME", f"{st['repos']} PUBLIC REPOS",
           "REACT · TANSTACK", "POSTGRES RLS", "FASTAPI · NESTJS", "BUILDING, LEARNING, SHARING"]
    unit = "".join(f'<text x="{k*0}" y="0"></text>' for k in [])  # placeholder to keep structure simple
    xs, x = [], 0
    for s in seg:
        xs.append(f'<text x="{x}" y="34" font-size="13" fill="{MUTED}" letter-spacing="3">{escape(s)}</text><text x="{x + len(s)*10.2 + 20}" y="34" font-size="13" fill="{ROSE}">◆</text>')
        x += len(s) * 10.2 + 60
    row = "".join(xs)
    b = (f'<rect width="{W}" height="52" fill="{PANEL}" rx="14"/><clipPath id="c"><rect width="{W}" height="52" rx="14"/></clipPath>'
         f'<g clip-path="url(#c)"><g class="mq">{row}<g transform="translate({x},0)">{row}</g></g></g>')
    # marquee shifts by -50% of group width; group width = 2*x, so use explicit distance
    b = b.replace("@@", "")
    s = ""
    svg("ticker.svg", 52, b.replace('class="mq"', f'class="mq" style="--d:-{x}px"'), "Stats ticker")
    # fix keyframes distance to exactly one unit
    p = os.path.join(OUT, "ticker.svg")
    t = open(p).read().replace("to{transform:translateX(-50%)}", f"to{{transform:translateX(-{x}px)}}")
    open(p, "w").write(t)


def readme():
    r = ["<!--", "  GENERATED by scripts/gen_profile.py. Do not edit by hand.",
         "  Edit profile.config.json and run: python3 scripts/gen_profile.py", "-->", ""]
    img = lambda f, alt, extra='width="100%"': f'<img src="assets/stage/{f}" {extra} alt="{escape(alt, {chr(34): "&quot;"})}" />'
    r.append(f'<p align="center">{img("hero.svg", "Zakaria Boutchamir, founder of CodeLovers")}</p>\n')
    r.append(f'<p align="center">{img("about.svg", CFG["about"])}</p>\n')
    r.append(f'<p align="center">{img("h-targets.svg", "Selected work")}<br>')
    for i, t in enumerate(CFG["targets"]):
        r.append(f'<a href="{t["url"]}">{img(f"target-{i}.svg", t["label"] + ": " + t["desc"])}</a><br>')
    r.append("</p>\n")
    if DATA["posts"]:
        r.append(f'<p align="center">{img("h-posts.svg", "Latest posts")}<br>')
        for i, p in enumerate(DATA["posts"]):
            r.append(f'<a href="{p["url"]}">{img(f"post-{i}.svg", p["title"])}</a><br>')
        r.append(f'<a href="{CFG["posts"]["all_posts_url"]}">{img("all-posts.svg", "All posts")}</a>\n</p>\n')
    r.append(f'<p align="center">{img("h-contact.svg", "Contact")}<br>')
    for c in CFG["contacts"]:
        r.append(f'<a href="{c["url"]}"><img src="assets/stage/{contact(c)}" height="46" alt="{c["label"]}" /></a>')
    r.append("</p>\n")
    r.append(f'<p align="center">{img("ticker.svg", "Stats ticker")}</p>\n')
    open(os.path.join(ROOT, "README.md"), "w").write("\n".join(r))


hero(); about()
heading("h-targets.svg", "01", "SELECTED WORK")
for i, t in enumerate(CFG["targets"]):
    target(i, t)
if DATA["posts"]:
    heading("h-posts.svg", "02", "LATEST FROM THE BLOG")
    for i, p in enumerate(DATA["posts"]):
        post(i, p)
    all_posts()
heading("h-contact.svg", "03", "CONTACT")
ticker()
readme()
print("generated")
