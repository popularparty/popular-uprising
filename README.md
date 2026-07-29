# Popular Party — texts

Source and published edition of **Popular Uprising: The Manifesto of the
Popular Party** by Lucas Peters, first published 17 June 2026.

Read it: **https://YOUR-SUBDOMAIN/popular-uprising/**

---

## What is where

Everything in this repository is the web root. A file at `robots.txt` serves
at `https://your-subdomain/robots.txt`; a file at
`popular-uprising/index.html` serves at
`https://your-subdomain/popular-uprising/`.

```
.
├── .nojekyll               empty, and load-bearing — see below
├── LICENSE                 CC BY 4.0, governs the prose
├── LICENSE-CODE            MIT, governs build.py
├── README.md               this file
├── robots.txt              WEB ROOT ONLY. inert anywhere else
├── sitemap.xml             WEB ROOT ONLY
├── build.py                regenerates the edition from the manuscript
├── source-manuscript.txt   the manuscript. edit this, never the HTML
└── popular-uprising/
    ├── index.html          title page and contents
    ├── 01-face-tomorrow.html … 05-american-eschaton.html
    ├── full-text.html      all 14,762 words on one page
    ├── popular-uprising.txt  plain-text mirror
    └── fonts/              four subset woff2 faces + their OFL licenses
```

The book sits one level down rather than at the root so that a second volume
can be added beside it — `money-is-time/` — sharing one host, one sitemap, one
robots.txt, and one accumulation of authority.

## Publishing

**Settings → Pages → Build and deployment.** Source: *Deploy from a branch*.
Branch: `main`, folder: `/ (root)`.

**Settings → Pages → Custom domain.** Enter the subdomain and save. GitHub
writes a `CNAME` file to the repository root. Do not delete it. Only after
that, add the CNAME record at your DNS provider pointing the subdomain at
`<username>.github.io` — without the repository name.

## Before the first upload

Replace the placeholder domain. Every canonical link, Open Graph tag, JSON-LD
`url`, and sitemap entry currently reads `https://example.org`:

```bash
python3 build.py source-manuscript.txt . https://YOUR-SUBDOMAIN
```

Run from the repository root. It rewrites the tree in place from the
manuscript. This is also how you publish revisions — edit
`source-manuscript.txt`, re-run, commit. Never hand-patch the HTML.

## `.nojekyll`

GitHub Pages runs Jekyll over the publishing source by default. Jekyll
silently discards any file or folder whose name begins with an underscore and
attempts to interpret `{{ }}` and `{% %}` inside content. An empty
`.nojekyll` at the root turns all of that off. The file is empty on purpose.

## Licensing

| What | License | File |
|---|---|---|
| The manifesto text | CC BY 4.0 | `LICENSE` |
| `build.py` | MIT | `LICENSE-CODE` |
| Oswald, Libre Baskerville | SIL OFL 1.1 | `popular-uprising/fonts/OFL-*.txt` |

CC BY 4.0 means: copy it, quote it, translate it, reprint it, sell it. Name
the author. That is the whole condition. It is also one-way compatible with
CC BY-SA 4.0, which is what lets Wikipedia incorporate the text directly.

The font licenses must remain alongside the font files. That is the OFL's
only requirement and uploading `fonts/` intact satisfies it.

## Manuscript notes

Three items are documented in full in the earlier build notes: one repaired
line break (source 195–196, a single sentence split by a stray newline), six
straight quote marks among 191 curly ones, and a stray space inside the
compound `constitutional- paraconstitutional` at source line 42. The text is
otherwise verbatim — verified mechanically, all 178 source paragraphs present,
nothing rendered that is absent from the source.
