# Arbeitsanleitung für Claude: Website thomaspoelzler.com und Lebenslauf

Dieses Repository enthält die Website von Thomas Pölzler und die Word-Hauptdatei seines Lebenslaufs.
Thomas gibt Änderungswünsche im Chat; diese Datei beschreibt, wie sie technisch umgesetzt werden.
Kommunikation mit Thomas: Deutsch, kurz, ohne Fachjargon, ohne typische KI-Floskeln.

## Grundregeln

- Änderungen an der Website sofort umsetzen, bauen, prüfen, committen und auf `main` pushen.
  Nur bei echten Unklarheiten vorher nachfragen.
- Sobald der Lebenslauf geändert wird: Word-Datei **und** PDF als Download schicken (SendUserFile),
  das PDF auf der Website austauschen (siehe „Lebenslauf“).
- Betrifft eine Änderung Inhalte, die in Website und CV doppelt vorkommen (Publikationen, Vorträge,
  Positionen, Preise, Lehre, Projekte), und Thomas nennt nur einen der beiden Orte: den genannten Ort
  sofort ändern und in derselben Antwort fragen, ob der andere nachgezogen werden soll.
- Commits: kurze deutsche Beschreibung, Attributionszeilen laut System-Hinweis anhängen.
- Nach dem Push: in ein, zwei Sätzen sagen, was sich geändert hat, und den Link zur Seite nennen
  (`https://www.thomaspoelzler.com/...`). Cloudflare veröffentlicht nach 1–2 Minuten.
- Geheimnisse (EPP-Code, Passwörter, Zugangsdaten) nie wiederholen, speichern oder irgendwo eintragen.

## Aufbau

- `src/pages/*.html` – Inhalte der Seiten (HTML-Fragmente). Seitenliste, Titel, Beschreibungen,
  Navigation, strukturierte Daten: `src/build.py` (`PAGES`, `NAV`, `PERSON_LD`, `BOOKS_LD`).
- `src/papers_data.json` – alle Einträge der Seite /research/papers. Logik: `src/papers.py`.
  Einzelseiten pro Paper (`/research/papers/<slug>`) gibt es seit 10/2026 nicht mehr (Thomas’ Wunsch);
  alte Adressen leiten per `_redirects` auf /research/papers weiter. `build_paper_pages` in build.py wird nicht aufgerufen.
- `src/assets/` – CSS (`css/style.css`), Schriften, Bilder, Skript, PDFs:
  - `files/papers/` – Publikations-PDFs, Dateiname `Pölzler (Jahr) - Titel.pdf`
    (Doppelpunkte und `?` im Titel weglassen; mehrere Autoren: `Pölzler and Paulo (2024) - …`).
  - `files/books/`, `files/CV_Thomas_Poelzler.pdf`, `files/cv/page-NN.webp` (Seitenbilder des CV-Betrachters).
  - `img/papers/<slug>.jpg` – Vorschaubilder (nur für die abgeschalteten Einzelseiten), erzeugt mit `python3 src/make_thumbs.py`
    (nimmt `src/covers/<slug>.pdf`, falls vorhanden, sonst die erste PDF-Seite).
- `dist/` – fertige Website (wird committet; Cloudflare Pages liefert sie aus, ohne Build-Befehl).
- `dist/_redirects` (Weiterleitungen alter Adressen) und `dist/_headers` werden in `src/build.py`
  (`build_site`) geschrieben. Die `noindex`-Regeln für `*.pages.dev` müssen bleiben. `SITE_URL` ist `https://www.thomaspoelzler.com`.
- `cv/CV_Thomas_Poelzler.docx` – **Hauptdatei des Lebenslaufs** (immer diese bearbeiten).
- `tools/cv_build.py` – erzeugt aus der Hauptdatei das PDF mit Originalschriften und aktualisiert die Website.
- `tools/paper_pdf/` – Werkzeuge für selbst gesetzte Publikations-PDFs (siehe unten).

## Ablauf bei jeder Website-Änderung

1. Repository klonen (falls noch nicht geschehen) und auf dem neuesten Stand von `main` arbeiten.
2. Quelle in `src/` ändern (nie direkt in `dist/`).
3. `python3 src/build.py` (schreibt `dist/` und `preview/website-vorschau.html`).
4. Prüfen: geänderte Seite mit Playwright/Chromium aus `dist/` aufrufen (lokaler Server, z. B.
   `python3 -m http.server` in `dist/`) und Screenshots bei 390 px (Handy) und 1440 px (Desktop) ansehen.
   Den Server danach gezielt beenden (nicht mit `pkill -f`, das trifft die eigene Shell).
5. `git add -A && git commit && git push origin main`.

Gestaltung: Überschriften/Fußzeile `--accent #947979`, grauer Text `--grey #6a6a6a`.
Englische Seiten: Anführungszeichen “…”, deutsche Titel „…“.

## Publikation hinzufügen

Website (`src/papers_data.json`, Reihenfolge = Reihenfolge im CV, neueste zuerst):

```json
{
  "sec": "Journal Articles",            // Seite Papers: Journal Articles | Chapters | Conference Articles | Edited Volumes |
                                        // Commentaries | Introductions | Book Reviews
                                        // Seite Public Philosophy (/research/public-philosophy):
                                        // Opinion Essays | Review Essays | Interviews and Reflections
  "title": "Titel",
  "pdf": "Pölzler (2026) - Titel.pdf",  // Datei in src/assets/files/papers/; weglassen, wenn kein PDF
  "venue": "<i>Zeitschrift</i> 12 (3), 45-67. 2026.",   // Zeile unter dem Titel; endet mit ". Jahr."
  "with_": "(with Vorname Nachname and Vorname Nachname)",  // nur bei Koautoren
  "cv": "Pölzler, Thomas; Koautor, Vorname (2026): Titel. *Zeitschrift* 12 (3), 45-67.",  // CV-Zitat, *kursiv*
  "authors": ["Pölzler, Thomas", "Koautor, Vorname"],
  "year": 2026,
  "journal": "Zeitschrift", "volume": "12", "issue": "3", "pages": "45-67",
  "doi": "10.xxxx/xxxx",                // oder "url" für Online-Version ohne DOI
  "lang": "de",                         // nur bei deutschen Texten
  "kind": "chapter",                    // chapter | conference | issue | review | oped (sonst Artikel)
  "book": "Buchtitel", "publisher": "Verlag",  // bei Kapiteln
  "abstract": "…"                       // für Metadaten/Bibliografie (Einzelseiten derzeit abgeschaltet)
}
```

Weitere Felder bei Bedarf: `extra` (zusätzliche Zeile in der Liste, z. B. „Republished in …“;
`@PDF:Dateiname` und `@PAGE:Titel` werden zu Links), `cv_extra`, `note`, `href`, `abstract_lang`.
Danach: PDF ablegen, `python3 src/make_thumbs.py`, `python3 src/build.py`, prüfen, pushen.
Die Bücher stehen nicht in der JSON-Datei, sondern in `src/pages/books.html` (und `BOOKS_LD` in build.py).

Lebenslauf: Eintrag in der passenden Rubrik unter „Publications“ ergänzen (Format siehe unten),
neuester Eintrag oben als [1], alle folgenden Nummern der Rubrik um eins erhöhen.
Rubriken im CV: Books, Journal Articles, Chapters, Conference Articles, Edited Volumes, Introductions,
Comments, Book Reviews, Science to Public (auf der Website eigene Seite „Public Philosophy“ mit den Rubriken
Opinion Essays, Review Essays, Interviews and Reflections; der CV bleibt bei einer Rubrik).
Sicherungsstand vor dieser Umstellung: Branch `stand-vor-public-philosophy`.

Selbst gesetzte PDFs (Manuskriptfassungen) in Thomas’ Stil: `tools/paper_pdf/manuscript.py`
(Markdown mit Kopfzeilen → pandoc mit `ref.docx` → LibreOffice). Kopfvermerk grau
(Arial 9 pt, Zeilenabstand 11,4 pt, #777777), Text des Vermerks wie bei den vorhandenen PDFs.
Originalseitenzahlen am linken Rand: `tools/paper_pdf/pagemarks.py` (Beispielaufrufe in
`example_pagemarks_jobs.py`). Kurze Zeitungstexte: `tools/paper_pdf/oped.py`. Verlags-Deckblätter
nicht ins Download-PDF übernehmen; ein Deckblatt mit Cover kann als `src/covers/<slug>.pdf`
für das Vorschaubild dienen.

## Lebenslauf

Hauptdatei: `cv/CV_Thomas_Poelzler.docx`. Bearbeitung direkt im XML (docx-Skill: entpacken,
`word/document.xml` ändern, wieder zippen, validieren). Format nicht verändern:

- Abschnittsüberschrift: eigener Absatz, Verdana, Farbe `E36C0A`, Größe `31` (Halbpunkte),
  `spacing before=480 after=80`, `keepNext`.
- Einträge: Tabulator bei `2126`, hängender Einzug `left=2126 hanging=2126`, `line=288`.
  Linke Spalte (Datum oder Rubrik) + `<w:tab/>` + Text; Folgeeinträge beginnen mit `<w:tab/>`.
  Abstand vor dem ersten Eintrag nach einer Überschrift 0, vor der ersten Zeile einer neuen
  Publikationsrubrik 300, zwischen Einträgen 240, Folgezeilen eines Eintrags 60–120.
  Zusatzzeilen („Republished in …“, „Accompanied by: …“, „Reviewed by:“) mit `<w:br/>` im selben Absatz.
- Zu lange Texte für die linke Spalte auf zwei Absätze verteilen (z. B. „Existential“ / „Philosophy“).
- Kursiv: Zeitschriften- und Buchtitel; Satzzeichen danach aufrecht.
- „Reviewed by“-Absätze unter den Büchern: Farbe `6A6A6A` (wie auf der Website).
- Datumsformat MM/DD/YYYY; englische Anführungszeichen “…”, deutsche „…“.

PDF erzeugen (nur mit Originalschriften Arial und Verdana):

```
python3 tools/cv_build.py --fonts <Ordner mit den Schriftdateien> --out <Ordner für Downloads>
```

Die Schriften (ARIAL.TTF, ARIALI.TTF, ARIALBD.TTF, ARIALBI.TTF, Verdana.ttf, VERDANAI.TTF) liegen in
den Projektdateien bzw. Chat-Anhängen, nicht im Repository (Lizenz, öffentliches Repository).
Sind sie nicht auffindbar: Thomas bitten, sie anzuhängen. Nie mit Ersatzschriften exportieren.
Das Skript ersetzt `src/assets/files/CV_Thomas_Poelzler.pdf`, die Seitenbilder und die Bildliste in
`src/pages/cv.html` und legt `CV_Thomas_Poelzler_<Datum>.docx/.pdf` im Download-Ordner ab.
Danach: PDF-Seiten ansehen (Seitenumbrüche, neue Stellen), `python3 src/build.py`, beide Download-
Dateien schicken, Hauptdatei und Website committen und pushen.

## Werkzeuge in der Arbeitsumgebung

Python 3 mit pymupdf, Pillow, pypdf; pandoc; LibreOffice (`soffice`); Playwright mit Chromium
(`NODE_PATH=$(npm root -g) node …`). Fehlendes mit `pip install --break-system-packages` nachinstallieren.
