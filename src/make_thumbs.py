"""Vorschaubilder (erste PDF-Seite) für die Einzelseiten der Papers.

Aufruf nach Änderungen an den PDFs: python3 src/make_thumbs.py  (braucht PyMuPDF und Pillow)
"""
import io
import os
import pymupdf
from PIL import Image

import papers

ROOT = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(ROOT, "assets", "img", "papers")
WIDTH = 300

os.makedirs(DEST, exist_ok=True)
keep = set()
sizes = {}
for e in papers.load():
    if not e.get("pdf"):
        continue
    out = os.path.join(DEST, e["slug"] + ".jpg")
    keep.add(os.path.basename(out))
    page = pymupdf.open(os.path.join(ROOT, "assets", "files", "papers", e["pdf"]))[0]
    pm = page.get_pixmap(matrix=pymupdf.Matrix(WIDTH * 2 / page.rect.width, WIDTH * 2 / page.rect.width), alpha=False)
    img = Image.open(io.BytesIO(pm.tobytes("png"))).convert("RGB")
    img = img.resize((WIDTH, round(img.height * WIDTH / img.width)), Image.LANCZOS)
    img.save(out, "JPEG", quality=84, optimize=True, progressive=True)
    sizes[e["slug"]] = img.size
for f in os.listdir(DEST):
    if f not in keep:
        os.remove(os.path.join(DEST, f))
import json
json.dump(sizes, open(os.path.join(ROOT, "papers_thumbs.json"), "w"), indent=0, sort_keys=True)
print(len(keep), "Vorschaubilder")
