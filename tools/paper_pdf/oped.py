"""Erzeugt PDFs im Layout des Camus-Manuskripts (Word, A4) aus einfachen Textdateien.
Aufbau der Textdatei: Kopfzeilen 'schluessel: wert', dann '---', dann Text.
Im Text: '> ' = Vorspann (grauer Kasten), '## ' = Zwischenüberschrift, Leerzeile = neuer Absatz,
*kursiv*, **fett**."""
import html, os, re, sys
from playwright.sync_api import sync_playwright

AFF = {"de": "Institut für Philosophie, Universität Graz, Österreich",
       "en": "Department of Philosophy, University of Graz, Austria"}
HEAD = {"de": ("Dieser Text erschien als", "Online verfügbar unter"),
        "en": ("This text was published as", "Available online at")}

CSS = """
@page { size: A4; margin: 70.8pt 70.8pt 82pt 70.8pt; }
html { -webkit-print-color-adjust: exact; }
body { margin: 0; font: 12pt/20.7pt 'Liberation Serif', 'Times New Roman', serif; color: #000; }
.note { font: 9pt/11.4pt 'Liberation Sans', Arial, sans-serif; color: #777777; margin: 0 0 22pt; }
.note a { color: #777777; text-decoration: none; }
h1 { font: bold 23pt/30.4pt 'Liberation Sans', Arial, sans-serif; margin: 0 0 15pt; }
.author { font: 11pt/16.6pt 'Liberation Sans', Arial, sans-serif; margin: 0; text-indent: 0 !important; text-transform: uppercase; }
.aff { font: 11pt/16.6pt 'Liberation Sans', Arial, sans-serif; margin: 0 0 22pt; text-indent: 0 !important; }
.lead { background: #f2f2f2; border-top: .5pt solid #a6a6a6; border-bottom: .5pt solid #a6a6a6;
        padding: 6pt 5pt 7pt; margin: 0 0 30pt; text-align: justify; hyphens: auto; }
.body { margin-top: 30pt; }
.lead + .body { margin-top: 0; }
p { margin: 0; text-align: justify; hyphens: auto; }
p + p { text-indent: 22.7pt; }
h2 { font: bold 12pt/20.7pt 'Liberation Serif', 'Times New Roman', serif; margin: 20.7pt 0 0; break-after: avoid; }
h2 + p { text-indent: 0; }
p.q { margin: 6pt 0 6pt 22.7pt; text-indent: 0; font-size: 11pt; line-height: 16pt; }
p.q + p { text-indent: 0; }
ul { margin: 0; padding-left: 22.7pt; }
li { text-align: justify; }
ul + p { text-indent: 0; }
p.qq { margin-top: 10pt; text-indent: 0 !important; }
p.qq + p { text-indent: 0; }
p.ref { padding-left: 22.7pt; text-indent: -22.7pt !important; font-size: 11pt; line-height: 16pt; margin-bottom: 4pt; text-align: left; }
"""


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    return t


def build(src, outdir):
    raw = open(src, encoding="utf-8").read()
    meta_s, body = raw.split("\n---\n", 1)
    meta = dict(l.split(": ", 1) for l in meta_s.strip().splitlines())
    lang = meta["lang"]
    a, b = HEAD[lang]
    note = "© %s %s | %s: %s | %s: %s" % (meta["year"], meta["publisher"], a, inline(meta["cite"]), b, html.escape(meta["url"]))
    authors = "".join('<p class="author">%s</p>' % html.escape(x.strip()) for x in meta["authors"].split(";"))
    out = ['<div class="note">%s</div>' % note, "<h1>%s</h1>" % inline(meta["title"]), authors,
           '<p class="aff">%s</p>' % AFF[lang]]
    blocks = [x.strip() for x in re.split(r"\n\s*\n", body.strip()) if x.strip()]
    lead = [x[2:] for x in blocks if x.startswith("> ")]
    if lead:
        out.append('<div class="lead"><p>%s</p></div>' % inline(" ".join(lead)))
    out.append('<div class="body">')
    inlist = False
    for x in blocks:
        x = " ".join(l.strip() for l in x.splitlines())
        if x.startswith("> "):
            continue
        if x.startswith("- "):
            if not inlist:
                out.append("<ul>"); inlist = True
            out.append("<li>%s</li>" % inline(x[2:])); continue
        if inlist:
            out.append("</ul>"); inlist = False
        if x.startswith("## "):
            out.append("<h2>%s</h2>" % inline(x[3:]))
        elif re.fullmatch(r"\*\*[^*]+\*\*", x):
            out.append('<p class="qq">%s</p>' % inline(x))
        elif x.startswith("§ "):
            out.append('<p class="ref">%s</p>' % inline(x[2:]))
        elif x.startswith("| "):
            out.append('<p class="q">%s</p>' % inline(x[2:]))
        else:
            out.append("<p>%s</p>" % inline(x))
    if inlist:
        out.append("</ul>")
    out.append("</div>")
    doc = '<!doctype html><html lang="%s"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>%s</body></html>' % (
        lang, html.escape(meta["title"]), CSS, "\n".join(out))
    dest = os.path.join(outdir, meta["filename"])
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page()
        pg.set_content(doc)
        pg.evaluate("document.fonts.ready")
        pg.pdf(path=dest, format="A4", prefer_css_page_size=True, display_header_footer=True,
               header_template="<span></span>",
               footer_template='<div style="width:100%;font:12pt \'Liberation Serif\',serif;text-align:right;padding:0 70.8pt 0 0;margin-bottom:45pt"><span class="pageNumber"></span></div>')
        br.close()
    # Titel und Autor in die PDF-Metadaten
    import pypdf
    r = pypdf.PdfReader(dest); w = pypdf.PdfWriter(clone_from=r)
    w.add_metadata({"/Title": meta["title"], "/Author": meta["authors"].replace(";", ",")})
    w.write(dest)
    print(dest)


if __name__ == "__main__":
    for f in sys.argv[2:]:
        build(f, sys.argv[1])
