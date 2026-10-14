# thomaspoelzler.com

Quelldateien der persönlichen Website von Thomas Pölzler.

## Aufbau

- `src/pages/` – Inhalt der einzelnen Seiten (HTML-Fragmente)
- `src/assets/` – Stylesheets, Schriften, Bilder, Skript, Lebenslauf (PDF)
- `src/build.py` – setzt Vorlage und Inhalte zu fertigen Seiten zusammen (nur Python-Standardbibliothek)
- `dist/` – fertige Website, die Cloudflare Pages ausliefert

## Neu bauen

```
python3 src/build.py
```

Das Skript schreibt `dist/` neu und legt zusätzlich eine Vorschau-Datei in `preview/` an (wird nicht ins Repository übernommen).

## Cloudflare Pages

- Build command: leer
- Build output directory: `dist`
