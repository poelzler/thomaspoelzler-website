"""Papers: Liste für /research/papers und eine eigene Seite pro Eintrag (/research/papers/<slug>).

Alle Angaben stehen in papers_data.json (Reihenfolge und Zitierweise wie im Lebenslauf).
Die Einzelseiten werden nirgends auf der Website verlinkt; Suchmaschinen finden sie über die Sitemap.
"""
import html
import json
import os
import re
import unicodedata
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "papers_data.json")
SECTIONS = ["Journal Articles", "Chapters", "Conference Articles", "Edited Volumes", "Commentaries",
            "Introductions", "Book Reviews"]
# Seite /research/outreach (früher Rubrik „Op-eds, Blog Posts, etc.“ auf der Papers-Seite)
PUBLIC_SECTIONS = ["Opinion Essays", "Review Essays", "Interviews and Reflections"]
LABEL = {"Journal Articles": "Article", "Chapters": "Chapter", "Conference Articles": "Conference article",
         "Edited Volumes": "Special issue", "Commentaries": "Commentary", "Introductions": "Introduction",
         "Book Reviews": "Book review", "Opinion Essays": "Essay", "Review Essays": "Review essay",
         "Interviews and Reflections": "Interview", None: "Article"}


def load():
    E = json.load(open(DATA, encoding="utf-8"))
    seen = set()
    for e in E:
        s = slugify(e["title"])
        assert s not in seen, s
        seen.add(s)
        e["slug"] = s
        e["path"] = "/research/papers/" + s
    return E


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def slugify(title):
    t = unicodedata.normalize("NFKD", plain(title).replace("ß", "ss"))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    if len(t) > 90:
        t = t[:90].rsplit("-", 1)[0]
    return t


def pdf_url(fn):
    return "/files/papers/" + quote(fn)


def esc(s):
    """HTML-Text, in dem nur <i>…</i> und <a href="…">…</a> erlaubt sind."""
    keep = []
    def hold(m):
        keep.append(m.group(0)); return "\x00%d\x00" % (len(keep) - 1)
    s = re.sub(r'</?i>|<a href="[^"]*">|</a>', hold, s)
    s = html.escape(s, quote=False)
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], s)


def cv_html(s):
    """Literaturangabe wie im CV: *kursiv* wird innerhalb der kursiven Zeile aufrecht gesetzt."""
    s = esc(s)
    s = re.sub(r"\*([^*]+)\*", r'<span class="up">\1</span>', s)
    return s


def links(e, by_title):
    out = []
    if e.get("pdf"):
        out.append('&gt; <a href="%s">Download</a>' % pdf_url(e["pdf"]))
    url = e.get("url") or ("https://doi.org/" + e["doi"] if e.get("doi") else None)
    if url:
        out.append('&gt; <a href="%s">Online Version</a>' % html.escape(url))
    return out


def resolve(s, by_title):
    s = re.sub(r"@PDF:([^\"]+)", lambda m: pdf_url(m.group(1)), s)
    return re.sub(r"@PAGE:([^\"]+)", lambda m: by_title[m.group(1)]["path"], s)


def list_html(sections=None):
    """Inhalt der Seite /research/papers bzw. /research/outreach (gleiches Format)."""
    sections = sections or SECTIONS
    E = load()
    by_title = {plain(e["title"]): e for e in E}
    out = []
    for sec in sections:
        items = [e for e in E if e.get("sec") == sec]
        out.append('    <h2 class="sec">%s</h2>' % html.escape(sec))
        for n, e in enumerate(items, 1):
            if e.get("pdf"):
                t = '<a href="%s">%s</a>' % (pdf_url(e["pdf"]), esc(e["title"]))
            elif e.get("href"):
                t = '<a href="%s">%s</a>' % (html.escape(e["href"]), esc(e["title"]))
            else:
                t = '<span class="u">%s</span>' % esc(e["title"])
            w = (" " + e["with_"]) if e.get("with_") else ""
            p = "[%d] %s%s<br>%s" % (n, t, w, e["venue"])
            if e.get("extra"):
                p += "<br>" + resolve(e["extra"], by_title)
            out.append("    <p>%s</p>" % p)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def describe(e):
    """Kurzbeschreibung für Suchmaschinen: Anfang des Abstracts oder bibliografische Angabe."""
    ab = e.get("abstract")
    if isinstance(ab, list):
        ab = " ".join(ab)
    if ab:
        t = plain(ab)
        if len(t) > 158:
            t = t[:155].rsplit(" ", 1)[0].rstrip(",;:") + " …"
        return t
    venue = plain(re.sub(r"\.\s*\d{4}\.\s*$", "", e["venue"])) if e.get("venue") else ""
    kind = LABEL.get(e.get("sec"), "Article").lower()
    lead = kind.capitalize()
    if venue:
        lead += " in " + venue.rstrip(".")
    return "%s (%s). %s" % (lead, e["year"], "Download the PDF." if e.get("pdf") else "")


def pages_split(p):
    m = re.fullmatch(r"(\w+)-(\w+)", p or "")
    return (m.group(1), m.group(2)) if m else ((p, None) if p else (None, None))


def meta_tags(e, site):
    """Google-Scholar-Metadaten (Highwire Press)."""
    if e.get("kind") == "oped":
        return ""
    m = [("citation_title", plain(e["title"]))]
    for a in e.get("authors", []):
        m.append(("citation_author", a))
    m.append(("citation_publication_date", str(e["year"])))
    if e.get("journal"):
        m.append(("citation_journal_title", e["journal"]))
    if e.get("book"):
        m.append(("citation_inbook_title" if e.get("kind") == "chapter" else "citation_conference_title" if e.get("kind") == "conference" else "citation_book_title", e["book"]))
    if e.get("publisher"):
        m.append(("citation_publisher", e["publisher"]))
    for k in ("volume", "issue"):
        if e.get(k):
            m.append(("citation_" + k, e[k]))
    fp, lp = pages_split(e.get("pages"))
    if fp:
        m.append(("citation_firstpage", fp))
    if lp:
        m.append(("citation_lastpage", lp))
    if e.get("doi"):
        m.append(("citation_doi", e["doi"]))
    if e.get("pdf"):
        m.append(("citation_pdf_url", site + pdf_url(e["pdf"])))
    m.append(("citation_language", e.get("lang", "en")))
    m.append(("citation_abstract_html_url", site + e["path"]))
    return "".join('<meta name="%s" content="%s">\n' % (k, html.escape(v, quote=True)) for k, v in m)


def json_ld(e, site, person_ref, desc):
    url = site + e["path"]
    kind = e.get("kind")
    typ = {"chapter": "Chapter", "issue": "PublicationIssue", "oped": "Article"}.get(kind, "ScholarlyArticle")
    authors = []
    for a in e.get("authors", []):
        if a.startswith("Pölzler"):
            authors.append(person_ref)
        else:
            fam, giv = (a.split(", ", 1) + [""])[:2]
            authors.append({"@type": "Person", "name": (giv + " " + fam).strip()})
    w = {"@type": typ, "@id": url + "#work", "name": plain(e["title"]), "headline": plain(e["title"])[:110],
         "author": authors, "datePublished": str(e["year"]), "inLanguage": e.get("lang", "en"), "url": url,
         "mainEntityOfPage": url, "description": desc}
    if kind == "review":
        w["genre"] = "Book review"
    ab = e.get("abstract")
    if ab:
        w["abstract"] = plain(" ".join(ab) if isinstance(ab, list) else ab)
    if e.get("doi"):
        w["sameAs"] = "https://doi.org/" + e["doi"]
    elif e.get("url"):
        w["sameAs"] = e["url"]
    if e.get("pages"):
        w["pagination"] = e["pages"]
    if e.get("journal"):
        per = {"@type": "Periodical", "name": e["journal"]}
        if e.get("volume"):
            per = {"@type": "PublicationVolume", "volumeNumber": e["volume"], "isPartOf": per}
            if e.get("issue"):
                per = {"@type": "PublicationIssue", "issueNumber": e["issue"], "isPartOf": per}
        w["isPartOf"] = per
    elif e.get("book"):
        w["isPartOf"] = {"@type": "Book", "name": e["book"]}
    if e.get("publisher"):
        w["publisher"] = {"@type": "Organization", "name": e["publisher"]}
    if e.get("pdf"):
        w["encoding"] = {"@type": "MediaObject", "encodingFormat": "application/pdf", "contentUrl": site + pdf_url(e["pdf"])}
    page = {"@type": "WebPage", "@id": url, "url": url, "name": plain(e["title"]), "description": desc,
            "mainEntity": {"@id": url + "#work"}, "isPartOf": {"@id": site + "/#website"}, "about": person_ref}
    crumbs = [("Thomas Pölzler", site + "/"), ("Research", site + "/research"), ("Papers", site + "/research/papers"),
              (plain(e["title"]), url)]
    bc = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}
    return '<script type="application/ld+json">%s</script>\n' % json.dumps(
        {"@context": "https://schema.org", "@graph": [page, w, bc]}, ensure_ascii=False)


THUMBS = os.path.join(ROOT, "papers_thumbs.json")


def page_html(e, by_title):
    lang = ' lang="de"' if e.get("lang") == "de" else ""
    out = ['    <h2 class="sec paper"%s>%s</h2>' % (lang, esc(e["title"]))]
    out.append('    <p class="paper-cite"><i>%s</i></p>' % cv_html(e["cv"]))
    if e.get("cv_extra"):
        out.append('    <p class="paper-cite"><i>%s</i></p>' % cv_html(e["cv_extra"]))
    if e.get("note"):
        out.append('    <p class="paper-note">%s</p>' % resolve(e["note"], by_title))
    L = links(e, by_title)
    size = json.load(open(THUMBS)).get(e["slug"]) if os.path.exists(THUMBS) else None
    if size and e.get("pdf"):
        # Vorschaubild der ersten Seite, daneben die Links (wie die Cover auf der Seite Books)
        out.append('    <div class="book paper-box">')
        out.append('      <a class="nu" href="%s"><img class="cover" src="/img/papers/%s.jpg" width="%d" height="%d" alt="First page of the PDF" loading="lazy"></a>'
                   % (pdf_url(e["pdf"]), e["slug"], size[0], size[1]))
        out.append('      <div class="book-info"><p>%s</p></div>' % "<br>".join(L))
        out.append('    </div>')
    elif L:
        out.append('    <p class="paper-links">%s</p>' % "<br>".join(L))
    ab = e.get("abstract")
    if ab:
        al = e.get("abstract_lang", e.get("lang", "en"))
        alang = ' lang="de"' if al == "de" else ""
        for k, para in enumerate(ab if isinstance(ab, list) else [ab]):
            out.append("    <p class=\"paper-abs\"%s>%s%s</p>" % (alang, "Abstract: " if k == 0 else "", esc(para)))
    return "\n".join(out) + "\n"


def thumb(e):
    size = json.load(open(THUMBS)).get(e["slug"]) if os.path.exists(THUMBS) else None
    return ("/img/papers/%s.jpg" % e["slug"], size) if size and e.get("pdf") else (None, None)
