"""Graue Original-Seitenzahlen am linken Rand selbst gesetzter PDFs.

anchors(): Anfangstext jeder Originalseite (ab der zweiten) aus dem Original-PDF.
locate(): findet diese Stellen im selbst gesetzten PDF (Buchstabenfolge, robust gegen
          Trennungen, Zeichensetzung und kleine Textabweichungen).
stamp():  setzt die Zahlen und einen Hinweis unter den grauen Kopfvermerk auf Seite 1.
"""
import re, unicodedata, pymupdf

LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", "ß": "ss"}
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
# Kopfvermerk und Randzahlen: gleiche Schrift, Größe und Farbe
HS, PITCH = 9, 11.4
HCOL = (0x77 / 255,) * 3
NOTICE = {
    ("en", False): "The numbers in the left margin indicate the page numbers of the published version.",
    ("en", True): "The numbers in the left margin indicate the approximate page numbers of the published version.",
    ("de", False): "Die Zahlen am linken Rand geben die Seitenzahlen der publizierten Fassung an.",
    ("de", True): "Die Zahlen am linken Rand geben die ungefähren Seitenzahlen der publizierten Fassung an.",
}


def norm(s):
    for k, v in LIG.items():
        s = s.replace(k, v)
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if c.isascii() and c.isalnum())


def page_lines(page, x_split=None, half=None):
    L = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"])
            if not t.strip():
                continue
            x0 = l["bbox"][0]
            if x_split is not None:
                h = 0 if x0 < x_split else 1
                if h != half:
                    continue
            L.append((l["bbox"][1], x0, l["spans"][0]["size"], t))
    L.sort()
    return L


def anchors(pdf, pages, top, bottom=None, skip=None, spread=None, n=6, col=False):
    """pages: Liste (pdf-Seite 1-basiert, Label[, Hälfte]). Liefert [(Label, Text)]."""
    d = pymupdf.open(pdf)
    out = []
    for item in pages:
        pno, label = item[0], item[1]
        p = d[pno - 1]
        if spread:
            L = page_lines(p, p.rect.width / 2 - 5, item[2])
        else:
            L = page_lines(p)
        L = [x for x in L if x[0] >= top and (bottom is None or x[0] <= bottom)]
        if col:  # zweispaltig: Seite beginnt oben in der linken Spalte
            L = [x for x in L if x[1] < p.rect.width / 2 - 10]
        if skip:
            L = [x for x in L if not re.match(skip, x[3].strip())]
        txt = " ".join(x[3] for x in L[:n])
        out.append((label, txt))
    return out


def stream(doc):
    """Buchstabenfolge des selbst gesetzten PDFs mit Zeilenposition je Buchstabe (ohne graue Kopfzeile)."""
    S, pos = [], []
    for pi, p in enumerate(doc):
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                spans = [s for s in l["spans"] if s["text"].strip()]
                if not spans:
                    continue
                if all(s["color"] in (0x7F7F7F, 0x808080, 0x7E7E7E, 0x7F7F7E) or 0x707070 <= s["color"] <= 0x8F8F8F for s in spans):
                    continue  # grauer Kopfvermerk
                txt = "".join(s["text"] for s in spans)
                if re.fullmatch(r"\s*\d+\s*", txt) and l["bbox"][1] > p.rect.height * 0.85:
                    continue  # Seitenzahl unten
                info = (pi, l["bbox"], spans[0]["origin"][1], spans[0]["size"])
                for c in norm(txt):
                    S.append(c); pos.append(info)
    return "".join(S), pos


def locate(doc, anchs, title_label=None):
    S, pos = stream(doc)
    from collections import Counter
    body_size = Counter(round(p[3]) for p in pos).most_common(1)[0][0]
    res = []
    last = 0
    if title_label is not None:
        # Erste Originalseite: Titelzeile (größte Schrift auf Seite 1)
        p = doc[0]
        best = None
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                sp = [s for s in l["spans"] if s["text"].strip()]
                if sp and (best is None or sp[0]["size"] > best[3] + 0.5):
                    best = (0, l["bbox"], sp[0]["origin"][1], sp[0]["size"])
        res.append((title_label, best, "title"))
    for label, txt in anchs:
        A = norm(txt)
        hit = None
        for k in (70, 50, 35):
            if len(A) >= k:
                i = S.find(A[:k], last)
                if i >= 0:
                    hit = (i, "exact%d" % k); break
        if not hit:  # Abschnitt an anderer Stelle (z. B. Literatur vor Danksagung): eindeutiger Treffer im ganzen Text
            for k in (70, 50):
                if len(A) >= k and S.count(A[:k]) == 1:
                    i = S.find(A[:k])
                    if pos[i][3] >= body_size - 1:  # nicht in Fußnoten (dort stehen bei mir die Endnoten des Originals)
                        hit = (i, "anywhere%d" % k)
                    break
        if not hit:
            for off in range(0, max(1, min(len(A) - 22, 500)), 6):
                w = A[off:off + 22]
                i = S.find(w, last)
                if i >= 0 and i - off >= last - 5:
                    hit = (max(i - off, last), "window@%d" % off); break
        if not hit:
            res.append((label, None, "NOT FOUND: " + txt[:60])); continue
        i, how = hit
        last = i + 1
        res.append((label, pos[i], how))
    return res


def body_left(page):
    xs = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            if "".join(s["text"] for s in l["spans"]).strip():
                xs.append(round(l["bbox"][0]))
    from collections import Counter
    return Counter(xs).most_common(1)[0][0]


def stamp(src, dest, res, lang, approx=False, notice=True):
    doc = pymupdf.open(src) if isinstance(src, str) else src
    font = pymupdf.Font(fontfile=FONT)
    if notice:  # Hinweis als weitere Zeile unter dem grauen Kopfvermerk
        p = doc[0]
        head = []
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                sp = [s for s in l["spans"] if s["text"].strip()]
                if sp and l["bbox"][1] < p.rect.height * 0.25 and 0x707070 <= sp[0]["color"] <= 0x8F8F8F:
                    head.append((l["bbox"], sp[0]["origin"][1]))
        head.sort(key=lambda h: h[1])
        x0 = min(h[0][0] for h in head)
        p.insert_text((x0, head[-1][1] + PITCH), NOTICE[(lang, approx)], fontsize=HS, fontname="arialx", fontfile=FONT, color=HCOL)
    for label, info, how in res:
        if info is None:
            continue
        pi, bbox, base, fsz = info
        p = doc[pi]
        left = body_left(p)
        txt = str(label)
        w = font.text_length(txt, fontsize=HS)
        y = base if fsz <= 14 else bbox[1] + HS + 2
        p.insert_text((left - 10 - w, y), txt, fontsize=HS, fontname="arialx", fontfile=FONT, color=HCOL)
    doc.save(dest, garbage=3, deflate=True)


def restyle_header(doc, html_text, notice_text=None):
    """Kopfvermerk eines in Word gesetzten PDFs im neuen Stil neu setzen (Text unverändert)."""
    p = doc[0]
    lines, title_top = [], None
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            sp = [s for s in l["spans"] if s["text"].strip()]
            if not sp:
                continue
            if l["bbox"][1] < 140 and 0x707070 <= sp[0]["color"] <= 0x8F8F8F:
                lines.append(pymupdf.Rect(l["bbox"]))
            elif sp[0]["size"] > 15 and (title_top is None or l["bbox"][1] < title_top):
                title_top = l["bbox"][1]
    x0 = min(r.x0 for r in lines); y0 = min(r.y0 for r in lines)
    for r in lines:
        p.add_redact_annot(r + (-0.5, -0.5, 0.5, 0.5))
    for k in p.get_links():
        if k["from"].y1 < title_top - 2:
            p.delete_link(k)
    p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    body = html_text + (" | " + notice_text if notice_text else "")
    css = ("@font-face {font-family: LS; src: url(LiberationSans-Regular.ttf);} "
           "@font-face {font-family: LS; src: url(LiberationSans-Italic.ttf); font-style: italic;} "
           "* {font-family: LS; font-size: %spt; line-height: %spt; color: #777777; margin: 0;}" % (HS, PITCH))
    arch = pymupdf.Archive("/usr/share/fonts/truetype/liberation")
    W = p.rect.width - 2 * x0
    top = y0 - 1
    while True:
        r = pymupdf.Rect(x0, top, x0 + W, title_top - 14)
        # Probesatz in einem Wegwerf-Dokument, um die Höhe zu messen
        t = pymupdf.open(); tp = t.new_page(width=p.rect.width, height=p.rect.height)
        spare, scale = tp.insert_htmlbox(r, body, css=css, archive=arch, scale_low=1)
        t.close()
        if spare >= 0 or top < 40:
            break
        top -= 4
    spare, scale = p.insert_htmlbox(pymupdf.Rect(x0, top, x0 + W, title_top - 14), body, css=css, archive=arch, scale_low=1)
    return top, spare
