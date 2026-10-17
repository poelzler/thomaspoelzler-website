"""Baut die Website aus Vorlage + Inhaltsdateien.

Ausgabe:
  dist/                  fertige Website (für GitHub + Cloudflare Pages)
  preview/vorschau.html  eine einzige Datei mit allen Seiten zum Durchklicken
"""
import base64
import html
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "..", "dist")
PREVIEW = os.path.join(ROOT, "..", "preview")
SITE_URL = "https://www.thomaspoelzler.com"

# Navigation wie auf der bisherigen Seite
NAV = [
    ("Start", "/", []),
    ("About", "/about", [
        ("Education", "/about/education"),
        ("Positions", "/about/positions"),
        ("Grants & Awards", "/about/grants-awards"),
        ("Contact", "/about/contact"),
    ]),
    ("Research", "/research", [
        ("Interests", "/research/interests"),
        ("Publications", "/research/publications"),
        ("Presentations", "/research/presentations"),
        ("Projects", "/research/projects"),
    ]),
    ("Teaching", "/teaching", [
        ("Courses", "/teaching/courses"),
        ("Materials", "/teaching/materials"),
    ]),
    ("CV", "/cv", []),
]

# Fertig nachgebaute Seiten: Pfad, Inhaltsdatei, Seitentitel im Titelbild, Beschreibung
PAGES = [
    {"path": "/", "src": "start.html", "hero": "Welcome!", "title": "Thomas Pölzler",
     "description": "I am a researcher and lecturer at the Section Moral and Political Philosophy of the University of Graz, Austria. My main areas of research are metaethics and moral psychology."},
    {"path": "/about", "src": "about.html", "hero": "About", "title": "Thomas Pölzler - About",
     "description": "About Thomas Pölzler: education, positions, grants and awards, and contact information."},
    {"path": "/about/education", "src": "education.html", "hero": "Education", "title": "Thomas Pölzler - Education",
     "description": "Education of Thomas Pölzler: Dr. phil in Philosophy, MA in Political, Economic and Legal Philosophy, and Mag. phil. in Philosophy (University of Graz)."},
    {"path": "/about/positions", "src": "positions.html", "hero": "Positions", "title": "Thomas Pölzler - Positions",
     "description": "Research, teaching and visiting positions of Thomas Pölzler at the University of Graz, the University of Tokyo, the College of Charleston and elsewhere."},
    {"path": "/about/grants-awards", "src": "grants-awards.html", "hero": "Grants & Awards", "title": "Thomas Pölzler - Grants & Awards",
     "description": "Grants, fellowships and awards of Thomas Pölzler, including a Marie Skłodowska-Curie Fellowship and the Wolfgang Stegmüller Award."},
    {"path": "/about/contact", "src": "contact.html", "hero": "Contact", "title": "Thomas Pölzler - Contact",
     "description": "Contact Thomas Pölzler: e-mail, phone, postal address at the University of Graz and academic profiles."},
    {"path": "/research", "src": "research.html", "hero": "Research", "title": "Thomas Pölzler - Research",
     "description": "Research of Thomas Pölzler: interests, publications, presentations and projects."},
    {"path": "/research/interests", "src": "interests.html", "hero": "Interests", "title": "Thomas Pölzler - Interests",
     "description": "Research interests of Thomas Pölzler: metaethics, empirical research on morality, political philosophy and Albert Camus."},
    {"path": "/research/publications", "src": "publications.html", "hero": "Publications", "title": "Thomas Pölzler - Publications",
     "description": "Publications by Thomas Pölzler: books, journal articles, chapters, edited volumes, reviews and op-eds on metaethics, moral psychology, basic needs and Albert Camus."},
    {"path": "/research/presentations", "src": "presentations.html", "hero": "Presentations", "title": "Thomas Pölzler - Presentations",
     "description": "Talks and presentations by Thomas Pölzler at universities, conferences and workshops worldwide."},
    {"path": "/research/projects", "src": "projects.html", "hero": "Projects", "title": "Thomas Pölzler - Projects",
     "description": "Research projects of Thomas Pölzler, including the Marie Skłodowska-Curie project Making Morality Impartial."},
    {"path": "/teaching", "src": "teaching.html", "hero": "Teaching", "title": "Thomas Pölzler - Teaching",
     "description": "Teaching of Thomas Pölzler: courses and teaching materials."},
    {"path": "/teaching/courses", "src": "courses.html", "hero": "Courses", "title": "Thomas Pölzler - Courses",
     "description": "Courses taught by Thomas Pölzler at the University of Graz and elsewhere."},
    {"path": "/teaching/materials", "src": "materials.html", "hero": "Materials", "title": "Thomas Pölzler - Materials",
     "description": "Teaching materials by Thomas Pölzler: academic writing, critical thinking, ethics and political philosophy, Theory of Knowledge and quizzes."},
    {"path": "/cv", "src": "cv.html", "hero": "CV", "title": "Thomas Pölzler - CV",
     "description": "Curriculum vitae of Thomas Pölzler."},
    {"path": "/pictures", "src": "pictures.html", "hero": "Pictures", "title": "Thomas Pölzler - Pictures",
     "description": "Pictures from journeys of Thomas Pölzler."},
    {"path": "/imprint", "src": "imprint.html", "hero": "Imprint", "title": "Thomas Pölzler - Imprint",
     "description": "Imprint and data protection declaration of thomaspoelzler.com."},
]


def slug(path):
    return "start" if path == "/" else path.strip("/").replace("/", "-")


ICON = {
    "menu": '<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>',
    "close": '<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>',
    "search": '<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>',
    "back": '<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>',
    "chev": '<svg width="12.6" height="8.4" viewBox="6 8 12 8" aria-hidden="true"><path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"/></svg>',
    "expand": '<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M16.59 8.59 12 13.17 7.41 8.59 6 10l6 6 6-6z"/></svg>',
}

e = lambda s: html.escape(s, quote=True)


def desktop_nav(cur):
    out = ['<nav class="main-nav" aria-label="Main"><ul>']
    for label, href, subs in NAV:
        cls = ' class="current"' if href == cur else ""
        aria = ' aria-current="page"' if href == cur else ""
        if not subs:
            out.append('<li%s><a href="%s"%s>%s</a></li>' % (cls, href, aria, e(label)))
            continue
        # Der Oberpunkt öffnet nur das Untermenü; ohne JavaScript führt er zur ersten Unterseite
        out.append('<li class="has-sub"><a class="parent" href="%s" role="button" aria-haspopup="true" aria-expanded="false">%s</a><button class="chev" type="button" aria-label="%s submenu" aria-expanded="false" tabindex="-1">%s</button><ul class="sub">'
                   % (subs[0][1], e(label), e(label), ICON["chev"]))
        for sl, sh in subs:
            c = ' class="current"' if sh == cur else ""
            a = ' aria-current="page"' if sh == cur else ""
            out.append('<li%s><a href="%s"%s>%s</a></li>' % (c, sh, a, e(sl)))
        out.append("</ul></li>")
    out.append("</ul></nav>")
    return "".join(out)


def drawer_nav(cur):
    out = ['<ul class="drawer-nav">']
    for label, href, subs in NAV:
        if not subs:
            c = ' class="current"' if href == cur else ""
            a = ' aria-current="page"' if href == cur else ""
            out.append('<li%s><a href="%s"%s>%s</a></li>' % (c, href, a, e(label)))
            continue
        inside = cur == href or any(sh == cur for _, sh in subs)
        cls = ["group"] + (["open"] if inside else []) + (["current"] if href == cur else [])
        out.append('<li class="%s"><button class="toggle" type="button" aria-expanded="%s" aria-label="%s %s">%s</button>'
                   % (" ".join(cls), "true" if inside else "false", "Collapse" if inside else "Expand", e(label), ICON["expand"]))
        out.append('<a class="parent" href="%s" role="button" aria-expanded="%s">%s</a><ul class="sub">' % (subs[0][1], "true" if inside else "false", e(label)))
        for sl, sh in subs:
            c = ' class="current"' if sh == cur else ""
            a = ' aria-current="page"' if sh == cur else ""
            out.append('<li%s><a href="%s"%s>%s</a></li>' % (c, sh, a, e(sl)))
        out.append("</ul></li>")
    out.append("</ul>")
    return "".join(out)


def chrome_top(cur):
    return (
        '<a class="skip" href="#main">Skip to main content</a>\n'
        '<header class="site-header">\n'
        '  <button class="menu-btn" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="drawer">%(menu)s</button>\n'
        '  <a class="brand" href="/"><img class="logo" src="/img/logo-unigraz.png" width="52" height="44" alt="University of Graz"><span class="brand-name">Thomas Pölzler</span></a>\n'
        '  %(nav)s\n'
        '  <button class="search-btn" type="button" aria-label="Search this site" aria-expanded="false" aria-controls="search-panel">%(search)s</button>\n'
        '</header>\n'
        '<div class="search-panel" id="search-panel">\n'
        '  <form class="search-card" role="search" action="https://www.google.com/search" target="_blank">\n'
        '    <button class="search-back" type="button" aria-label="Close search">%(back)s</button>\n'
        '    <span class="search-icon">%(search)s</span>\n'
        '    <input class="search-input" type="search" name="q" placeholder="Search this site" aria-label="Search this site" autocomplete="off">\n'
        '  </form>\n'
        '</div>\n'
        '<div class="scrim" aria-hidden="true"></div>\n'
        '<aside class="drawer" id="drawer" aria-label="Site navigation">\n'
        '  <button class="drawer-close" type="button" aria-label="Close navigation">%(close)s</button>\n'
        '  %(drawer)s\n'
        '</aside>\n'
    ) % dict(ICON, nav=desktop_nav(cur), drawer=drawer_nav(cur))


FOOTER = (
    '<footer class="site-footer">\n'
    '  <div class="page">\n'
    '    <p class="name">Thomas Pölzler</p>\n'
    '    <p class="links"><a href="https://philosophie-gewi.uni-graz.at/en/section-moral-and-political-philosophy/">Section Moral and Political Philosophy</a> | <a href="https://www.uni-graz.at/en/">University of Graz</a> | <a href="/imprint">Imprint</a></p>\n'
    '    <p class="links"><a href="mailto:thomas.poelzler@uni-graz.at">thomas.poelzler(at)uni-graz.at</a></p>\n'
    '  </div>\n'
    '</footer>\n'
)


def main_block(page, body):
    return (
        '<main id="main">\n'
        '  <section class="hero"><h1>%s</h1><span class="bar"></span></section>\n'
        '  <div class="page content p-%s">\n%s  </div>\n'
        '</main>\n'
    ) % (e(page["hero"]), slug(page["path"]), body)


def head(page, css, extra=""):
    url = SITE_URL + (page["path"] if page["path"] != "/" else "/")
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>%s</title>\n<meta name="description" content="%s">\n'
        '<link rel="canonical" href="%s">\n'
        '<meta property="og:title" content="%s">\n<meta property="og:type" content="website">\n'
        '<meta property="og:url" content="%s">\n<meta property="og:description" content="%s">\n'
        '%s%s</head>\n'
    ) % (e(page["title"]), e(page["description"]), url, e(page["title"]), url, e(page["description"]), css, extra)


PERSON_LD = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Thomas Pölzler",
    "url": SITE_URL + "/",
    "jobTitle": "Researcher and lecturer in philosophy",
    "email": "mailto:thomas.poelzler@uni-graz.at",
    "affiliation": {"@type": "CollegeOrUniversity", "name": "University of Graz", "url": "https://www.uni-graz.at/en/"},
    "knowsAbout": ["Metaethics", "Moral psychology", "Basic needs", "Distributive justice", "Environmental ethics", "Albert Camus"],
    "sameAs": [
        "https://scholar.google.at/citations?user=pPmGiWUAAAAJ",
        "https://www.researchgate.net/profile/Thomas_Poelzler/",
        "http://uni-graz.academia.edu/ThomasP%C3%B6lzler",
        "https://philpeople.org/profiles/thomas-polzler",
    ],
}


def out_file(path):
    if path == "/":
        return "index.html"
    return path.strip("/") + ".html"


def build_site():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), OUT)
    css = '<link rel="stylesheet" href="/css/fonts.css">\n<link rel="stylesheet" href="/css/style.css">\n'
    for page in PAGES:
        body = open(os.path.join(ROOT, "pages", page["src"]), encoding="utf-8").read()
        extra = ""
        if page["path"] == "/":
            extra = '<script type="application/ld+json">%s</script>\n' % json.dumps(PERSON_LD, ensure_ascii=False)
        doc = (head(page, css, extra) + "<body>\n" + chrome_top(page["path"]) + main_block(page, body)
               + FOOTER + '<script src="/js/site.js" defer></script>\n</body>\n</html>\n')
        dest = os.path.join(OUT, out_file(page["path"]))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8").write(doc)
    # Fehlerseite: ohne sie würde Cloudflare Pages bei unbekannten Adressen die Startseite ausliefern
    nf = {"path": "/404", "hero": "Page not found", "title": "Thomas Pölzler - Page not found",
          "description": "This page could not be found."}
    body = ('    <p>Sorry, the page you requested could not be found.</p>\n'
            '    <p>&gt; <a href="/">Back to the start page</a></p>\n')
    doc = (head(nf, css) + "<body>\n" + chrome_top("") + main_block(nf, body)
           + FOOTER + '<script src="/js/site.js" defer></script>\n</body>\n</html>\n')
    doc = re.sub(r'<link rel="canonical"[^>]*>\n', '<meta name="robots" content="noindex">\n', doc)
    doc = re.sub(r'<meta property="og:url"[^>]*>\n', "", doc)
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(doc)
    # Weiterleitungen und Sitemap für Cloudflare Pages
    open(os.path.join(OUT, "_redirects"), "w").write("/start / 301\n")
    urls = "".join("  <url><loc>%s%s</loc></url>\n" % (SITE_URL, p["path"]) for p in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls)
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE_URL)


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()


def build_preview():
    """Eine Datei mit allen Seiten; interne Links schalten per #/pfad zwischen den Seiten um."""
    os.makedirs(PREVIEW, exist_ok=True)
    A = os.path.join(ROOT, "assets")
    fonts = open(os.path.join(A, "css", "fonts.css"), encoding="utf-8").read()
    fonts = re.sub(r"url\(\.\./fonts/([^)]+)\)", lambda m: "url(data:font/woff2;base64,%s)" % b64(os.path.join(A, "fonts", m.group(1))), fonts)
    style = open(os.path.join(A, "css", "style.css"), encoding="utf-8").read()
    style = style.replace("url(../img/header.svg)", "url(data:image/svg+xml;base64,%s)" % b64(os.path.join(A, "img", "header.svg")))
    img = {"/img/portrait.jpg": "data:image/jpeg;base64," + b64(os.path.join(A, "img", "portrait.jpg")),
           "/img/logo-unigraz.png": "data:image/png;base64," + b64(os.path.join(A, "img", "logo-unigraz.png"))}
    for f in sorted(os.listdir(os.path.join(A, "files", "cv"))):
        img["/files/cv/" + f] = "data:image/webp;base64," + b64(os.path.join(A, "files", "cv", f))
    for f in sorted(os.listdir(os.path.join(A, "img", "books"))):
        img["/img/books/" + f] = "data:image/jpeg;base64," + b64(os.path.join(A, "img", "books", f))
    for f in sorted(os.listdir(os.path.join(A, "img", "pictures"))):
        if f.endswith("-800.webp"):
            img["/img/pictures/" + f] = "data:image/webp;base64," + b64(os.path.join(A, "img", "pictures", f))

    def localize(s):
        # Vorschau: nur die kleinen Fotos einbetten (srcset würde die Daten verdoppeln)
        s = re.sub(r' srcset="[^"]*" sizes="[^"]*"', "", s)
        for k, v in img.items():
            s = s.replace('src="%s"' % k, 'src="%s"' % v)
        return re.sub(r'href="/(?!files/)([^"]*)"', lambda m: 'href="#/%s"' % m.group(1), s)

    built = {}
    for page in PAGES:
        body = open(os.path.join(ROOT, "pages", page["src"]), encoding="utf-8").read()
        built[page["path"]] = {"title": page["title"], "hero": page["hero"], "html": localize(body), "cls": slug(page["path"])}
    first = PAGES[0]
    templates = "".join(
        '<template data-path="%s" data-title="%s" data-hero="%s" data-cls="%s">%s</template>\n' % (p, e(v["title"]), e(v["hero"]), v["cls"], v["html"])
        for p, v in built.items())
    names = {href: label for label, href, subs in NAV for _ in [0]}
    names.update({sh: sl for _, _, subs in NAV for sl, sh in subs})
    names["/imprint"] = "Imprint"
    site_js = open(os.path.join(A, "js", "site.js"), encoding="utf-8").read()
    router = ROUTER % json.dumps(names, ensure_ascii=False)
    pdf64 = b64(os.path.join(A, "files", "CV_Thomas_Poelzler.pdf"))
    router += PDFJS % pdf64
    doc = (head(first, "<style>\n%s\n%s</style>\n" % (fonts, style))
           + "<body>\n" + localize(chrome_top(first["path"])) + localize(main_block(first, built["/"]["html"]))
           + localize(FOOTER) + templates + "<script>\n%s\n%s</script>\n</body>\n</html>\n" % (site_js, router))
    dest = os.path.join(PREVIEW, "website-vorschau.html")
    open(dest, "w", encoding="utf-8").write(doc)
    return dest, len(doc.encode("utf-8"))


ROUTER = r"""
/* Nur fuer die Vorschau: Seitenwechsel innerhalb einer Datei */
(function () {
  var NAMES = %s;
  var main = document.querySelector('main .content');
  var h1 = document.querySelector('.hero h1');
  function render() {
    var path = (location.hash || '#/').slice(1) || '/';
    if (path.length > 1 && path.charAt(path.length - 1) === '/') path = path.slice(0, -1);
    var t = document.querySelector('template[data-path="' + path + '"]');
    if (t) {
      main.innerHTML = t.innerHTML;
      main.className = 'page content p-' + t.getAttribute('data-cls');
      h1.textContent = t.getAttribute('data-hero');
      document.title = t.getAttribute('data-title');
    } else {
      var name = NAMES[path] || path;
      main.className = 'page content';
      main.innerHTML = '<p style="padding:40px 8px;color:#6a6a6a">Vorschau: Die Seite „' + name + '“ ist noch nicht nachgebaut.</p>';
      h1.textContent = name;
      document.title = 'Thomas Pölzler - ' + name;
    }
    var href = '#' + path;
    document.querySelectorAll('.main-nav li, .drawer-nav li').forEach(function (li) { li.classList.remove('current'); });
    document.querySelectorAll('.main-nav a:not(.parent), .drawer-nav a:not(.parent)').forEach(function (a) {
      a.removeAttribute('aria-current');
      if (a.getAttribute('href') === href) {
        a.setAttribute('aria-current', 'page');
        a.parentNode.classList.add('current');
      }
    });
    document.querySelectorAll('.drawer-nav .group').forEach(function (g) {
      var inside = !!g.querySelector('a[href="' + href + '"]');
      g.classList.toggle('open', inside);
      var b = g.querySelector('.toggle');
      b.setAttribute('aria-expanded', inside ? 'true' : 'false');
    });
    document.body.classList.remove('menu-open', 'lock', 'search-open');
    window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', render);
  if (location.hash && location.hash !== '#/') render();
})();
"""

PDFJS = r"""
/* Nur fuer die Vorschau: Lebenslauf-PDF aus der Datei selbst oeffnen */
(function () {
  var data = "%s";
  var url = null;
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href="/files/CV_Thomas_Poelzler.pdf"]');
    if (!a) return;
    e.preventDefault();
    if (!url) {
      var bin = atob(data), arr = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
      url = URL.createObjectURL(new Blob([arr], {type: 'application/pdf'}));
    }
    window.open(url, '_blank');
  });
})();
"""

if __name__ == "__main__":
    build_site()
    dest, size = build_preview()
    print("dist und Vorschau gebaut:", dest, size, "Bytes")
