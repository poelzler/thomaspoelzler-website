"""Lebenslauf: aus cv/CV_Thomas_Poelzler.docx das PDF mit den Originalschriften erzeugen
und auf der Website austauschen (PDF, Seitenbilder für den Betrachter, cv.html).

Aufruf (vom Repository-Hauptordner aus):
    python3 tools/cv_build.py --fonts ORDNER [--out ORDNER] [--date JJJJ-MM-TT]

--fonts  Ordner (oder ZIP-Dateien darin) mit ARIAL.TTF, ARIALI.TTF, Verdana.ttf usw.
         Die Schriften werden nach ~/.fonts kopiert. Ohne Arial, Arial Italic und Verdana
         bricht das Skript ab: Das PDF darf nie mit Ersatzschriften erzeugt werden.
--out    Ordner für die Download-Kopien CV_Thomas_Poelzler_<Datum>.docx/.pdf (Standard: ./cv-out)
Danach: python3 src/build.py, prüfen, committen, pushen.
"""
import argparse, datetime, glob, io, os, re, shutil, subprocess, sys, tempfile, zipfile

import pymupdf
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX = os.path.join(ROOT, "cv", "CV_Thomas_Poelzler.docx")
SITE_PDF = os.path.join(ROOT, "src", "assets", "files", "CV_Thomas_Poelzler.pdf")
PAGES_DIR = os.path.join(ROOT, "src", "assets", "files", "cv")
CV_HTML = os.path.join(ROOT, "src", "pages", "cv.html")
W, H = 1600, 2264  # Seitenbilder (A4)
NEED = [("Arial", "Regular"), ("Arial", "Italic"), ("Verdana", "Regular")]


def install_fonts(src):
    dest = os.path.expanduser("~/.fonts")
    os.makedirs(dest, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for z in glob.glob(os.path.join(src, "**", "*.zip"), recursive=True):
        with zipfile.ZipFile(z) as f:
            for n in f.namelist():
                if n.lower().endswith(".ttf") and not n.startswith("__MACOSX"):
                    f.extract(n, tmp)
    files = glob.glob(os.path.join(src, "**", "*.[tT][tT][fF]"), recursive=True) + \
        glob.glob(os.path.join(tmp, "**", "*.[tT][tT][fF]"), recursive=True)
    # nur die Grundschnitte, damit Narrow/Medium/CE die Auswahl nicht verfälschen
    keep = re.compile(r"(?i)^(arial|ariali|arialbd|arialbi|verdana|verdanai|verdanab|verdanaz)(\b|[ _-]?\d*)?\.ttf$")
    n = 0
    for f in files:
        b = os.path.basename(f)
        plain = re.sub(r"(?i)^[0-9a-f]{6,}-", "", b).replace(" 1.TTF", ".TTF")  # Upload-Präfix entfernen
        if keep.match(plain):
            shutil.copy(f, os.path.join(dest, b)); n += 1
    subprocess.run(["fc-cache", "-f"], check=True)
    print("Schriften kopiert:", n)


def check_fonts():
    bad = []
    for fam, style in NEED:
        q = fam + (":italic" if style == "Italic" else "")
        got = subprocess.run(["fc-match", "-f", "%{family[0]}|%{style[0]}", q], capture_output=True, text=True).stdout
        if not got.startswith(fam + "|") or (style == "Italic") != ("Italic" in got):
            bad.append("%s %s (gefunden: %s)" % (fam, style, got))
    if bad:
        sys.exit("FEHLER: Originalschrift fehlt: " + "; ".join(bad) + "\nBitte die Schriften aus den Projektdateien mit --fonts angeben.")


def to_pdf(docx):
    tmp = tempfile.mkdtemp()
    shutil.copy(docx, os.path.join(tmp, "cv.docx"))
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, os.path.join(tmp, "cv.docx")],
                   check=True, capture_output=True, timeout=300)
    d = pymupdf.open(os.path.join(tmp, "cv.pdf"))
    fonts = {f[3].split("+")[-1] for p in d for f in p.get_fonts()}
    if not all(any(x in f for f in fonts) for x in ("ArialMT", "Arial-ItalicMT", "Verdana")) or \
            any("Liberation" in f or "DejaVu" in f for f in fonts):
        sys.exit("FEHLER: PDF enthält nicht die Originalschriften: %s" % sorted(fonts))
    d.set_metadata({"title": "CV Thomas Pölzler", "author": "Thomas Pölzler", "creator": "", "producer": ""})
    out = os.path.join(tmp, "final.pdf")
    d.save(out, garbage=4, deflate=True)
    return out


def update_site(pdf):
    shutil.copy(pdf, SITE_PDF)
    d = pymupdf.open(pdf)
    n = len(d)
    for i, p in enumerate(d):
        pix = p.get_pixmap(matrix=pymupdf.Matrix(W / p.rect.width, H / p.rect.height))
        Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB").save(
            os.path.join(PAGES_DIR, "page-%02d.webp" % (i + 1)), "WEBP", quality=60, method=6)
    for f in glob.glob(os.path.join(PAGES_DIR, "page-*.webp")):
        if int(re.search(r"(\d+)", os.path.basename(f)).group(1)) > n:
            os.remove(f)
    html = open(CV_HTML, encoding="utf-8").read()
    imgs = "\n".join('        <img src="/files/cv/page-%02d.webp" width="%d" height="%d" alt="Curriculum vitae of Thomas Pölzler, page %d of %d"%s>'
                     % (k, W, H, k, n, "" if k == 1 else ' loading="lazy"') for k in range(1, n + 1))
    html = re.sub(r'(<div class="pdf-pages"[^>]*>\n)(?:\s*<img src="/files/cv/page-\d+\.webp"[^\n]*\n)+', lambda m: m.group(1) + imgs + "\n", html)
    open(CV_HTML, "w", encoding="utf-8").write(html)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts")
    ap.add_argument("--out", default=os.path.join(ROOT, "cv-out"))
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    if a.fonts:
        install_fonts(a.fonts)
    check_fonts()
    pdf = to_pdf(DOCX)
    n = update_site(pdf)
    os.makedirs(a.out, exist_ok=True)
    base = os.path.join(a.out, "CV_Thomas_Poelzler_%s" % a.date)
    shutil.copy(DOCX, base + ".docx")
    shutil.copy(pdf, base + ".pdf")
    print("PDF: %d Seiten. Website-PDF, Seitenbilder und cv.html aktualisiert." % n)
    print("Download-Kopien:", base + ".docx", base + ".pdf")


if __name__ == "__main__":
    main()
