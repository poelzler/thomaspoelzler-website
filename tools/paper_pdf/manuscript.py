"""Baut PDFs im Layout des Camus-Manuskripts: Markdown -> pandoc (Vorlage ref.docx) -> LibreOffice -> PDF.
Kopf: schlüssel: wert, dann '---', dann Markdown (Fußnoten [^n], Überschriften #/##)."""
import os, re, subprocess, sys, tempfile, pypdf
HERE = os.path.dirname(os.path.abspath(__file__))
AFF = {"de": "Institut für Philosophie, Universität Graz, Österreich", "en": "Department of Philosophy, University of Graz, Austria"}
NOTE = {"en": "© {year} {publisher} | This version may not exactly replicate the published version. It is not the copy of record. | Published as: {cite} | For the published version please contact me at thomas.poelzler@uni-graz.at.",
        "de": "© {year} {publisher} | Diese Fassung entspricht möglicherweise nicht exakt der publizierten Version. | Publiziert als: {cite} | Für die publizierte Version kontaktieren Sie mich bitte unter thomas.poelzler@uni-graz.at."}
PAGENOTE = {("en", "exact"): "The numbers in the left margin indicate the page numbers of the published version.",
            ("en", "approx"): "The numbers in the left margin indicate the approximate page numbers of the published version.",
            ("de", "exact"): "Die Zahlen am linken Rand geben die Seitenzahlen der publizierten Fassung an.",
            ("de", "approx"): "Die Zahlen am linken Rand geben die ungefähren Seitenzahlen der publizierten Fassung an."}
LABEL = {"en": ("Abstract", "Key Words"), "de": ("Abstract", "Schlüsselwörter")}
REFS = r"^#+\s*(References|Literatur|Literaturverzeichnis|Bibliography|Bibliografie|Works Cited)\s*$"


def div(style, text):
    return '::: {custom-style="%s"}\n%s\n:::\n' % (style, text)


def build(src, outdir):
    raw = open(src, encoding="utf-8").read()
    head, body = raw.split("\n---\n", 1)
    m = {}
    for l in head.strip().splitlines():
        k, v = l.split(": ", 1); m[k] = v
    lang = m.get("lang", "en")
    note = m.get("note") or NOTE[lang].format(**m)
    if m.get("pagenote"):  # Hinweis auf die Randzahlen direkt im Kopfvermerk
        note += " | " + PAGENOTE[(lang, m["pagenote"])]
    parts = [div("Note", note), div("Title", m["title"])]
    for a in m["authors"].split(";"):
        parts.append(div("Author", a.strip().upper()))
    parts.append(div("Affiliation", m.get("affiliation", AFF[lang])))
    if m.get("abstract"):
        la, lk = LABEL[lang]
        ab = "[%s:]{.smallcaps} %s" % (la.upper(), m["abstract"])
        if m.get("keywords"):
            parts.append(div("Abstract", ab))
            parts.append(div("AbstractLast", "[%s:]{.smallcaps} %s" % (lk.upper(), m["keywords"])))
        else:
            parts.append(div("AbstractLast", ab))
    # Literaturverzeichnis als eigene Absatzvorlage
    lines = body.strip("\n").split("\n")
    out = []; inrefs = False; buf = []; first = [True]; indiv = [False]
    def flush():
        if buf:
            txt = " ".join(x.strip() for x in buf)
            if indiv[0]: out.append(txt + "\n")
            elif inrefs: out.append(div("Reference", txt))
            elif first[0] and not txt.startswith(("::: ", ">")): out.append(div("First Paragraph", txt)); first[0] = False
            else: out.append(txt + "\n")
            buf.clear()
    tab = []
    for l in lines:
        if l.startswith(("+-", "+=", "|")):
            flush(); tab.append(l); continue
        if tab:
            out.append("\n".join(tab) + "\n"); tab.clear()
        if l.startswith(":::"):
            flush(); out.append(l + "\n"); indiv[0] = not indiv[0]; first[0] = False; continue
        if re.match(r"^\[\^\w+\]:", l):
            flush(); out.append(l + "\n"); continue
        if re.match(REFS, l.strip()):
            flush(); out.append(l + "\n"); inrefs = True; continue
        if l.startswith("#"):
            flush(); out.append(l + "\n"); inrefs = False; first[0] = False; continue
        if not l.strip():
            flush(); continue
        if l.startswith("    ") and out and re.match(r"^\[\^\w+\]:", out[-1]):
            out[-1] = out[-1].rstrip("\n") + " " + l.strip() + "\n"; continue
        buf.append(l)
    flush()
    if tab:
        out.append("\n".join(tab) + "\n")
    if lang == "en":
        out = [re.sub(r"„([^“”„]*?)“", r"“\1”", x).replace("„", "“") for x in out]
    out = [x.replace("IMG/", os.path.join(HERE, "img") + "/") for x in out]
    md = "\n".join(parts) + "\n" + "\n".join(out)
    tmp = tempfile.mkdtemp()
    mdf = os.path.join(tmp, "doc.md"); open(mdf, "w", encoding="utf-8").write(md)
    dx = os.path.join(tmp, "doc.docx")
    subprocess.run(["pandoc", mdf, "-f", "markdown+smart-auto_identifiers", "-o", dx, "--reference-doc", os.path.join(HERE, "ref.docx")], check=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, dx], check=True, capture_output=True)
    dest = os.path.join(outdir, m["filename"])
    w = pypdf.PdfWriter(clone_from=os.path.join(tmp, "doc.pdf"))
    w.add_metadata({"/Title": m["title"], "/Author": m["authors"].replace(";", ",")})
    w.write(dest)
    print(dest, len(w.pages), "Seiten")


if __name__ == "__main__":
    for f in sys.argv[2:]:
        build(f, sys.argv[1])
