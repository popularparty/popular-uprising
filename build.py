#!/usr/bin/env python3
"""
Build a crawlable static HTML edition of POPULAR UPRISING from the plain-text
manuscript.

Usage:
    python3 build.py SOURCE.txt OUTDIR [BASE_URL]

BASE_URL defaults to https://example.org and appears in canonical links,
Open Graph tags, JSON-LD, and sitemap.xml. Change it to the real domain.
"""

import html
import os
import re
import sys
from datetime import date

SRC = sys.argv[1] if len(sys.argv) > 1 else "popularuprising.txt"
OUT = sys.argv[2] if len(sys.argv) > 2 else "site"
BASE = (sys.argv[3] if len(sys.argv) > 3 else "https://example.org").rstrip("/")

ROOT = "/popular-uprising"          # path the edition lives at on the domain
LICENSE_NAME = "CC BY-NC 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-nc/4.0/"
ORANGE = "#E8590C"

# ---------------------------------------------------------------- parsing ---

raw = open(SRC, encoding="utf-8").read()
lines = [l.rstrip() for l in raw.split("\n")]

TITLE = lines[0].strip()
SUBTITLE = lines[1].strip()
AUTHOR = lines[2].strip()
PUBLINE = lines[4].strip()
COPYRIGHT = lines[6].strip()
DEDICATION = lines[9].strip()
PUBDATE = "2026-06-17"

CH_RE = re.compile(r"^(.*?)\s*\(chapter\s+(\d+)\)\s*$", re.I)

chapters, cur = [], None
for i, line in enumerate(lines[11:], start=12):
    s = line.strip()
    m = CH_RE.match(s)
    if m:
        cur = {"n": int(m.group(2)), "title": m.group(1).strip(), "blocks": []}
        chapters.append(cur)
        continue
    if cur is None:
        continue
    if not s:
        # blank line inside a chapter = thematic break (skip leading/trailing)
        if cur["blocks"] and cur["blocks"][-1]["type"] != "break":
            cur["blocks"].append({"type": "break"})
        continue
    # MECHANICAL REPAIR: source line 196 is the tail of the sentence begun on
    # line 195. Rejoin rather than emit a dangling lowercase fragment.
    if s[0].islower() and cur["blocks"] and cur["blocks"][-1]["type"] == "p":
        cur["blocks"][-1]["text"] += " " + s
        continue
    kind = "quote" if (s.startswith("\u201c") and s.endswith("\u201d")
                       and s.count("\u201c") == 1) else "p"
    cur["blocks"].append({"type": kind, "text": s})

for c in chapters:
    while c["blocks"] and c["blocks"][-1]["type"] == "break":
        c["blocks"].pop()
    n = 0
    for b in c["blocks"]:
        if b["type"] in ("p", "quote"):
            n += 1
            b["id"] = f"c{c['n']}p{n}"

ORDINALS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
            6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"}


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s


for c in chapters:
    c["slug"] = f"{c['n']:02d}-{slugify(c['title'])}"
    c["file"] = c["slug"] + ".html"
    c["url"] = f"{BASE}{ROOT}/{c['file']}"
    c["ordinal"] = ORDINALS.get(c["n"], str(c["n"]))
    first = next(b["text"] for b in c["blocks"] if b["type"] == "p")
    sents = re.split(r"(?<=[.!?])\s+", first)
    d = ""
    for sent in sents:
        if len(d) + len(sent) > 155:
            break
        d = (d + " " + sent).strip()
    c["desc"] = d or first[:150]

# ------------------------------------------------------------------- css ---

CSS = """
/* Oswald and Libre Baskerville, SIL OFL 1.1. Self-hosted, subset to Latin.
   See fonts/OFL-Oswald.txt and fonts/OFL-LibreBaskerville.txt. */
@font-face{font-family:"Oswald SH";src:url(fonts/oswald-700.woff2) format("woff2");
  font-weight:700;font-style:normal;font-display:swap}
@font-face{font-family:"Libre Baskerville SH";src:url(fonts/lb-400.woff2) format("woff2");
  font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"Libre Baskerville SH";src:url(fonts/lb-700.woff2) format("woff2");
  font-weight:700;font-style:normal;font-display:swap}
@font-face{font-family:"Libre Baskerville SH";src:url(fonts/lb-400i.woff2) format("woff2");
  font-weight:400;font-style:italic;font-display:swap}

:root{
  --ink:#141414; --paper:#ffffff; --muted:#6a6a6a; --rule:#e4e2df;
  --orange:__ORANGE__; --wash:#faf9f7;
  --text:"Libre Baskerville SH",Baskerville,"Baskerville Old Face","Times New Roman",Georgia,serif;
  --display:"Oswald SH","Oswald",Haettenschweiler,"Arial Narrow Bold","Arial Narrow",Impact,sans-serif;
  --measure:41rem;
}
@media (prefers-color-scheme:dark){
  :root{--ink:#e8e6e3;--paper:#131313;--muted:#9a9691;--rule:#2e2c2a;--wash:#191919;--orange:#ff8a3d}
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--text);font-size:1.0625rem;line-height:1.62;
  font-kerning:normal;font-variant-ligatures:common-ligatures;
  text-rendering:optimizeLegibility;
}
.wrap{max-width:var(--measure);margin:0 auto;padding:0 1.5rem}
@media (max-width:30rem){
  body{font-size:1rem;line-height:1.6}
  .wrap{padding:0 1.05rem}
}
.wide{max-width:48rem}

/* Libre Baskerville has a large x-height and a wide set; utility labels are
   set in it uppercase and tracked out rather than in a second sans face. */
.label{
  font-family:var(--text);font-size:.66rem;font-weight:700;letter-spacing:.19em;
  text-transform:uppercase;line-height:1.4
}

/* ---- masthead ------------------------------------------------------- */
.masthead{border-bottom:1px solid var(--rule);margin-bottom:3.5rem}
.masthead .wrap{padding-top:1.15rem;padding-bottom:1.15rem;
  display:flex;gap:1rem;justify-content:space-between;align-items:baseline;flex-wrap:wrap}
.masthead a{
  font-family:var(--display);font-weight:700;font-size:.9rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink);text-decoration:none
}
.masthead a:hover{color:var(--orange)}
.masthead .loc{font-family:var(--text);font-size:.66rem;font-weight:700;letter-spacing:.19em;
  text-transform:uppercase;color:var(--muted)}

/* ---- title page ------------------------------------------------------ */
.titlepage{padding:3rem 0 4rem;border-bottom:4px solid var(--orange)}
.titlepage h1{
  font-family:var(--display);font-weight:700;font-size:clamp(3.2rem,12.5vw,6rem);
  line-height:.9;letter-spacing:.005em;text-transform:uppercase;margin:0 0 1.15rem
}
.titlepage .sub{font-size:1.06rem;font-style:italic;color:var(--ink);margin:0 0 2rem;line-height:1.45}
.titlepage .byline{
  font-family:var(--display);font-weight:700;font-size:1.15rem;letter-spacing:.13em;
  text-transform:uppercase;margin:0 0 .5rem
}
.imprint{font-family:var(--text);font-size:.78rem;line-height:2;color:var(--muted);margin:2.5rem 0 0}
.dedication{font-style:italic;color:var(--muted);margin:3rem 0 0;text-align:center;font-size:.95rem}

/* ---- contents -------------------------------------------------------- */
.contents{margin:3.5rem 0}
.contents h2,.frontmatter h2{
  font-family:var(--text);font-size:.66rem;font-weight:700;letter-spacing:.19em;
  text-transform:uppercase;color:var(--muted);margin:0 0 1.4rem
}
.toc{list-style:none;margin:0;padding:0}
.toc li{border-top:1px solid var(--rule)}
.toc li:last-child{border-bottom:1px solid var(--rule)}
.toc a{
  display:grid;grid-template-columns:2.8rem 1fr;gap:1rem;align-items:baseline;
  padding:1rem 0;text-decoration:none;color:var(--ink)
}
.toc a:hover{color:var(--orange)}
.toc .num{font-family:var(--display);font-weight:700;font-size:1.05rem;color:var(--orange);
  letter-spacing:.04em}
.toc .name{font-family:var(--display);font-weight:700;font-size:1.5rem;line-height:1.15;
  font-variant-caps:small-caps;letter-spacing:.02em}
.toc .blurb{grid-column:2;font-family:var(--text);font-size:.78rem;color:var(--muted);
  line-height:1.6;margin-top:.4rem}

/* ---- chapter openers ------------------------------------------------- */
.opener{margin:0 0 2.6rem;padding-top:.5rem}
.opener .eyebrow{
  font-family:var(--text);font-size:.66rem;font-weight:700;letter-spacing:.19em;
  text-transform:uppercase;color:var(--orange);display:block;margin:0 0 .8rem
}
/* Oswald ships no true small-cap glyphs, so the browser synthesises them.
   The heading stays one clean text node -- no per-letter spans -- because an
   extractor must read "Face Tomorrow", not fragments of it. */
.opener h1,.opener h2{
  font-family:var(--display);font-weight:700;letter-spacing:.022em;line-height:1.04;
  font-size:clamp(2.3rem,8vw,3.6rem);margin:0 0 1.15rem;
  font-variant-caps:small-caps;font-feature-settings:"smcp" 1
}
.opener .rule{border:0;border-top:4px solid var(--orange);margin:0 0 1.6rem;width:100%}
article + article .opener{margin-top:5.5rem;padding-top:3.5rem;border-top:1px solid var(--rule)}

/* ---- body ------------------------------------------------------------ */
article p{margin:0 0 1.3em;position:relative;hyphens:auto}
blockquote{
  margin:2.1rem 0;padding:0 0 0 1.3rem;border-left:3px solid var(--orange);
  font-style:italic;color:var(--ink)
}
blockquote p{margin:0}
hr.break{border:0;margin:2.6rem 0;text-align:center;overflow:visible;height:0}
hr.break::after{
  content:"\\2666";display:block;margin-top:-.75em;color:var(--orange);
  font-size:.75rem;letter-spacing:.6em;text-indent:.6em
}

/* ---- paragraph permalinks (the citation affordance) ------------------ */
.pl{
  position:absolute;left:-2.2rem;top:.1em;width:1.6rem;text-align:right;
  font-family:var(--text);font-size:.8rem;color:var(--orange);text-decoration:none;
  opacity:0;transition:opacity .12s ease
}
p:hover > .pl,.pl:focus{opacity:1}
.pl:focus-visible{outline:2px solid var(--orange);outline-offset:2px;opacity:1}
:target{background:color-mix(in srgb,var(--orange) 14%,transparent)}
@media (max-width:58rem){.pl{display:none}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}

/* ---- pagination + footer -------------------------------------------- */
.pager{
  display:flex;justify-content:space-between;gap:1.5rem;flex-wrap:wrap;
  margin:4.5rem 0 0;padding-top:1.6rem;border-top:4px solid var(--orange)
}
.pager a{
  font-family:var(--display);font-weight:700;font-size:1.15rem;letter-spacing:.02em;
  font-variant-caps:small-caps;text-decoration:none;color:var(--ink);max-width:16rem
}
.pager a:hover{color:var(--orange)}
.pager .dir{display:block;font-family:var(--text);font-size:.64rem;letter-spacing:.19em;
  text-transform:uppercase;color:var(--muted);margin-bottom:.35rem;font-weight:700;
  font-variant-caps:normal}
.pager .next{text-align:right;margin-left:auto}
footer.site{
  margin-top:5rem;border-top:1px solid var(--rule);background:var(--wash);
  font-family:var(--text);font-size:.78rem;line-height:1.85;color:var(--muted)
}
footer.site .wrap{padding-top:2.2rem;padding-bottom:3rem}
footer.site a{color:var(--muted)}
footer.site a:hover{color:var(--orange)}
a{color:inherit}
a:focus-visible{outline:2px solid var(--orange);outline-offset:2px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:1rem;top:1rem;position:fixed;background:var(--paper);color:var(--ink);
  padding:.6rem 1rem;border:2px solid var(--orange);z-index:9;font-family:var(--text)}

/* ---- print ----------------------------------------------------------- */
@media print{
  :root{--ink:#000;--paper:#fff;--muted:#444;--rule:#bbb}
  body{font-size:10.5pt;line-height:1.45}
  .masthead,.pager,.pl,footer.site{display:none}
  .wrap{max-width:none;padding:0}
  article{page-break-before:always}
  article:first-of-type{page-break-before:avoid}
  .opener h1,.opener h2{font-size:22pt}
  a{text-decoration:none}
}
""".replace("__ORANGE__", ORANGE)

# ---------------------------------------------------------------- helpers ---


def esc(s):
    return html.escape(s, quote=False)


def attr(s):
    return html.escape(s, quote=True)


def render_blocks(blocks, page_path):
    out = []
    for b in blocks:
        if b["type"] == "break":
            out.append('    <hr class="break" role="separator">')
            continue
        pid = b["id"]
        anchor = (f'<a class="pl" href="{page_path}#{pid}" '
                  f'aria-label="Permalink to paragraph {pid}">&#182;</a>')
        body = esc(b["text"])
        if b["type"] == "quote":
            out.append(f'    <blockquote id="{pid}"><p>{anchor}{body}</p></blockquote>')
        else:
            out.append(f'    <p id="{pid}">{anchor}{body}</p>')
    return "\n".join(out)


def page(*, title, desc, canonical, body, extra_head="", wide=False, loc=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{attr(desc)}">
<meta name="author" content="{attr(AUTHOR)}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<link rel="canonical" href="{attr(canonical)}">
<meta name="license" content="{attr(LICENSE_URL)}">
<link rel="license" href="{attr(LICENSE_URL)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{attr(TITLE.title())}">
<meta property="og:title" content="{attr(title)}">
<meta property="og:description" content="{attr(desc)}">
<meta property="og:url" content="{attr(canonical)}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{attr(title)}">
<meta name="twitter:description" content="{attr(desc)}">
<link rel="preload" href="fonts/lb-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/oswald-700.woff2" as="font" type="font/woff2" crossorigin>
{extra_head}<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to text</a>
<nav class="masthead">
  <div class="wrap{' wide' if wide else ''}">
    <a href="{ROOT}/">{esc(TITLE.title())}</a>
    <span class="loc">{esc(loc)}</span>
  </div>
</nav>
<main id="main" class="wrap{' wide' if wide else ''}">
{body}
</main>
<footer class="site">
  <div class="wrap{' wide' if wide else ''}">
    <p><strong>{esc(TITLE.title())}: {esc(SUBTITLE)}</strong><br>
    By {esc(AUTHOR)}. {esc(PUBLINE)}.<br>
    {esc(COPYRIGHT)}. Released under
    <a rel="license" href="{LICENSE_URL}">{LICENSE_NAME}</a> &mdash; copy it, quote it, translate it,
    reprint it, teach it. Credit the author and don't sell it.</p>
    <p><a href="{ROOT}/">Contents</a> &middot;
       <a href="{ROOT}/full-text.html">Read in one page</a> &middot;
       <a href="{ROOT}/popular-uprising.txt">Plain text</a></p>
  </div>
</footer>
</body>
</html>
"""


def jsonld(obj_str):
    return f'<script type="application/ld+json">\n{obj_str}\n</script>\n'


# ------------------------------------------------------------------ build ---

# OUT is the WEB ROOT. robots.txt, sitemap.xml and .nojekyll live here.
# The edition itself lives one level down, under ROOT, so a second volume can
# sit beside it later.
PAGES = os.path.join(OUT, ROOT.strip("/")) if ROOT.strip("/") else OUT
os.makedirs(PAGES, exist_ok=True)

# Disable Jekyll on GitHub Pages: it silently drops files beginning with an
# underscore and tries to interpret {{ }} and {% %} in content.
open(os.path.join(OUT, ".nojekyll"), "w").close()

# Self-hosted webfonts. Copied from ./fonts next to this script if present, so
# the built site makes no third-party requests.
import shutil
_fdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
if os.path.isdir(_fdir):
    os.makedirs(os.path.join(PAGES, "fonts"), exist_ok=True)
    for f in sorted(os.listdir(_fdir)):
        shutil.copy2(os.path.join(_fdir, f), os.path.join(PAGES, "fonts", f))

BOOK_URL = f"{BASE}{ROOT}/"
WORDS = sum(len(b["text"].split()) for c in chapters for b in c["blocks"] if "text" in b)

book_ld = f"""{{
  "@context": "https://schema.org",
  "@type": "Book",
  "@id": "{BOOK_URL}#book",
  "name": "{attr(TITLE.title())}",
  "alternateName": "{attr(TITLE.title())}: {attr(SUBTITLE)}",
  "headline": "{attr(SUBTITLE)}",
  "author": {{"@type": "Person", "name": "{attr(AUTHOR)}"}},
  "publisher": {{"@type": "Organization", "name": "Popular Party"}},
  "datePublished": "{PUBDATE}",
  "inLanguage": "en",
  "genre": ["Political manifesto", "Political philosophy"],
  "numberOfPages": {len(chapters)},
  "wordCount": {WORDS},
  "license": "{LICENSE_URL}",
  "isAccessibleForFree": true,
  "url": "{BOOK_URL}",
  "workExample": {{
    "@type": "Book",
    "bookFormat": "https://schema.org/EBook",
    "url": "{BASE}{ROOT}/full-text.html"
  }},
  "hasPart": [
{",".join(chr(10) + '    {"@type": "Chapter", "position": %d, "name": "%s", "url": "%s"}'
          % (c["n"], attr(c["title"]), c["url"]) for c in chapters)}
  ]
}}"""

# ---- index -----------------------------------------------------------------

toc = []
for c in chapters:
    toc.append(
        f'    <li><a href="{c["file"]}">'
        f'<span class="num">{c["n"]:02d}</span>'
        f'<span class="name">{esc(c["title"])}</span>'
        f'<span class="blurb">{esc(c["desc"])}</span></a></li>'
    )

index_body = f"""<header class="titlepage">
  <h1>{esc(TITLE.title())}</h1>
  <p class="sub">{esc(SUBTITLE)}</p>
  <p class="byline">{esc(AUTHOR)}</p>
  <p class="imprint">{esc(PUBLINE)}<br>{esc(COPYRIGHT)}<br>
    Released under <a rel="license" href="{LICENSE_URL}">{LICENSE_NAME}</a>.
    {WORDS:,} words.</p>
  <p class="dedication">{esc(DEDICATION)}</p>
</header>

<section class="contents">
  <h2>Contents</h2>
  <ol class="toc">
{chr(10).join(toc)}
  </ol>
</section>

<section class="frontmatter">
  <h2>Other formats</h2>
  <p><a href="full-text.html">The complete manifesto on one page</a> &mdash; every chapter,
  {WORDS:,} words, no pagination.<br>
  <a href="popular-uprising.txt">Plain text</a> &mdash; unformatted, for reprinting,
  translation, and machine reading.</p>
</section>"""

open(os.path.join(PAGES, "index.html"), "w", encoding="utf-8").write(
    page(title=f"{TITLE.title()}: {SUBTITLE}",
         desc=f"{SUBTITLE}. By {AUTHOR}. {PUBLINE}. The complete text, free to read and reprint.",
         canonical=BOOK_URL,
         extra_head=jsonld(book_ld),
         loc="Contents",
         body=index_body))

# ---- chapter pages ---------------------------------------------------------

for i, c in enumerate(chapters):
    prev_c = chapters[i - 1] if i > 0 else None
    next_c = chapters[i + 1] if i < len(chapters) - 1 else None

    head = ""
    if prev_c:
        head += f'<link rel="prev" href="{prev_c["file"]}">\n'
    if next_c:
        head += f'<link rel="next" href="{next_c["file"]}">\n'
    ch_ld = f"""{{
  "@context": "https://schema.org",
  "@type": "Chapter",
  "position": {c['n']},
  "name": "{attr(c['title'])}",
  "url": "{c['url']}",
  "author": {{"@type": "Person", "name": "{attr(AUTHOR)}"}},
  "datePublished": "{PUBDATE}",
  "inLanguage": "en",
  "license": "{LICENSE_URL}",
  "isAccessibleForFree": true,
  "isPartOf": {{
    "@type": "Book",
    "@id": "{BOOK_URL}#book",
    "name": "{attr(TITLE.title())}",
    "url": "{BOOK_URL}"
  }}
}}"""
    head += jsonld(ch_ld)

    pager = ['<nav class="pager">']
    if prev_c:
        pager.append(f'  <a class="prev" href="{prev_c["file"]}">'
                     f'<span class="dir">Previous</span>{esc(prev_c["title"])}</a>')
    if next_c:
        pager.append(f'  <a class="next" href="{next_c["file"]}">'
                     f'<span class="dir">Next</span>{esc(next_c["title"])}</a>')
    if not next_c:
        pager.append('  <a class="next" href="./"><span class="dir">Back to</span>Contents</a>')
    pager.append("</nav>")

    body = f"""<article>
  <header class="opener">
    <hr class="rule">
    <span class="eyebrow">Chapter {c['ordinal']}</span>
    <h1>{esc(c['title'])}</h1>
  </header>
{render_blocks(c['blocks'], c['file'])}
</article>

{chr(10).join(pager)}"""

    open(os.path.join(PAGES, c["file"]), "w", encoding="utf-8").write(
        page(title=f"{c['title']} \u2014 {TITLE.title()}",
             desc=c["desc"],
             canonical=c["url"],
             extra_head=head,
             loc=f"Chapter {c['n']} of {len(chapters)}",
             body=body))

# ---- full text -------------------------------------------------------------

arts = []
for c in chapters:
    arts.append(f"""<article>
  <header class="opener">
    <hr class="rule">
    <span class="eyebrow">Chapter {c['ordinal']}</span>
    <h2>{esc(c['title'])}</h2>
  </header>
{render_blocks(c['blocks'], 'full-text.html')}
</article>""")

full_body = f"""<header class="titlepage">
  <h1>{esc(TITLE.title())}</h1>
  <p class="sub">{esc(SUBTITLE)}</p>
  <p class="byline">{esc(AUTHOR)}</p>
  <p class="imprint">{esc(PUBLINE)}<br>{esc(COPYRIGHT)}<br>
    Released under <a rel="license" href="{LICENSE_URL}">{LICENSE_NAME}</a>.
    {WORDS:,} words.</p>
  <p class="dedication">{esc(DEDICATION)}</p>
</header>

{chr(10) + chr(10).join(arts)}

<nav class="pager">
  <a class="next" href="./"><span class="dir">Back to</span>Contents</a>
</nav>"""

open(os.path.join(PAGES, "full-text.html"), "w", encoding="utf-8").write(
    page(title=f"{TITLE.title()}: {SUBTITLE} \u2014 complete text",
         desc=f"The complete text of {TITLE.title()}, the manifesto of the Popular Party, by {AUTHOR}. All {len(chapters)} chapters on one page.",
         canonical=f"{BASE}{ROOT}/full-text.html",
         extra_head=jsonld(book_ld),
         loc="Complete text",
         body=full_body))

# ---- plain-text mirror -----------------------------------------------------

txt = [TITLE, SUBTITLE, AUTHOR, "", PUBLINE, "", COPYRIGHT, "",
       f"Released under {LICENSE_NAME} <{LICENSE_URL}>", "", DEDICATION, ""]
for c in chapters:
    txt += ["", "", f"{c['title'].upper()} (chapter {c['n']})", ""]
    for b in c["blocks"]:
        txt.append("* * *" if b["type"] == "break" else b["text"])
        txt.append("")
open(os.path.join(PAGES, "popular-uprising.txt"), "w",
     encoding="utf-8", newline="\n").write("\n".join(txt).rstrip() + "\n")

# ---- robots.txt ------------------------------------------------------------

crawlers = ["CCBot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot",
            "Claude-Web", "Claude-SearchBot", "anthropic-ai", "Google-Extended",
            "PerplexityBot", "Perplexity-User", "Applebot-Extended", "Bytespider",
            "Amazonbot", "meta-externalagent", "FacebookBot", "cohere-ai",
            "Diffbot", "Timpibot", "omgili", "AI2Bot"]
robots = ["# Every crawler, including AI training crawlers, is welcome here.",
          "# The text is CC BY 4.0. Take it.", ""]
for c in crawlers:
    robots += [f"User-agent: {c}", "Allow: /", ""]
robots += ["User-agent: *", "Allow: /", "",
           f"Sitemap: {BASE}/sitemap.xml"]
open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8", newline="\n").write(
    "\n".join(robots) + "\n")

# ---- sitemap ---------------------------------------------------------------

urls = [BOOK_URL, f"{BASE}{ROOT}/full-text.html"] + [c["url"] for c in chapters]
today = date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    sm += ["  <url>", f"    <loc>{u}</loc>", f"    <lastmod>{today}</lastmod>", "  </url>"]
sm.append("</urlset>")
open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(
    "\n".join(sm) + "\n")

print(f"{len(chapters)} chapters, {WORDS:,} words")
for base, _, files in os.walk(OUT):
    rel = os.path.relpath(base, OUT)
    print(f"  {'' if rel == '.' else rel + '/'}")
    for f in sorted(files):
        print(f"      {f:34} {os.path.getsize(os.path.join(base, f)):>7,}")
