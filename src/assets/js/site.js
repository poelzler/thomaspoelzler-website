(function () {
  var body = document.body;
  var menuBtn = document.querySelector('.menu-btn');
  var drawer = document.querySelector('.drawer');
  var drawerClose = document.querySelector('.drawer-close');
  var searchBtn = document.querySelector('.search-btn');
  var searchBack = document.querySelector('.search-back');
  var searchForm = document.querySelector('.search-card');
  var searchInput = document.querySelector('.search-input');
  var scrim = document.querySelector('.scrim');
  var SITE = 'thomaspoelzler.com';

  function each(list, fn) { Array.prototype.forEach.call(list, fn); }

  function setMenu(open) {
    body.classList.toggle('menu-open', open);
    body.classList.toggle('lock', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) { drawerClose.focus(); } else if (document.activeElement && drawer.contains(document.activeElement)) { menuBtn.focus(); }
  }

  function setSearch(open) {
    body.classList.toggle('search-open', open);
    searchBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) { searchInput.focus(); } else { searchInput.value = ''; searchBtn.focus(); }
  }

  menuBtn.addEventListener('click', function () {
    // Drehung des Menüsymbols neu starten, dann Menü öffnen
    menuBtn.classList.remove('spin');
    void menuBtn.offsetWidth;
    menuBtn.classList.add('spin');
    setTimeout(function () { menuBtn.classList.remove('spin'); }, 450);
    setMenu(true);
  });
  drawerClose.addEventListener('click', function () { setMenu(false); });
  searchBtn.addEventListener('click', function () { setSearch(true); });
  searchBack.addEventListener('click', function () { setSearch(false); });
  scrim.addEventListener('click', function () {
    if (body.classList.contains('menu-open')) setMenu(false);
    if (body.classList.contains('search-open')) setSearch(false);
  });

  // Suche: bis eine eigene Suche eingebaut ist, laeuft sie ueber Google, beschraenkt auf diese Website
  searchForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var q = searchInput.value.trim();
    if (!q) return;
    window.open('https://www.google.com/search?q=' + encodeURIComponent('site:' + SITE + ' ' + q), '_blank', 'noopener');
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (body.classList.contains('search-open')) setSearch(false);
    if (body.classList.contains('menu-open')) setMenu(false);
    each(document.querySelectorAll('.main-nav .has-sub.open'), function (li) { li.classList.remove('open'); });
  });

  // Untermenues im Seitenmenue auf- und zuklappen
  each(document.querySelectorAll('.drawer .toggle'), function (btn) {
    btn.addEventListener('click', function () {
      var li = btn.parentNode;
      var open = li.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', btn.getAttribute('aria-label').replace(open ? 'Expand' : 'Collapse', open ? 'Collapse' : 'Expand'));
    });
  });

  // Aufklappmenues am Desktop (Tastatur und Touch)
  // Es ist immer nur ein Untermenue offen: Oeffnen eines Menues schliesst die anderen
  function closeSubs(except) {
    each(document.querySelectorAll('.main-nav .has-sub.open'), function (li) {
      if (li === except) return;
      li.classList.remove('open');
      if (li.contains(document.activeElement)) document.activeElement.blur();
      var c = li.querySelector('.chev');
      if (c) c.setAttribute('aria-expanded', 'false');
    });
  }
  each(document.querySelectorAll('.main-nav .chev'), function (chev) {
    chev.addEventListener('click', function () {
      var li = chev.parentNode;
      closeSubs(li);
      var open = li.classList.toggle('open');
      chev.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (!open) chev.blur();
    });
  });
  each(document.querySelectorAll('.main-nav .has-sub'), function (li) {
    li.addEventListener('mouseenter', function (e) {
      if (e.pointerType !== 'touch') closeSubs(li);
    });
  });
  document.addEventListener('click', function (e) {
    if (e.target.closest && !e.target.closest('.main-nav .has-sub')) closeSubs(null);
  });

  // Wechsel auf Desktop-Breite schliesst das Seitenmenue
  window.addEventListener('resize', function () {
    if (window.innerWidth >= 768 && body.classList.contains('menu-open')) setMenu(false);
  });

  // Bilderkarussell: Pfeile, Tastatur, Endlosschleife; Nachbarbilder vorladen
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function slideIndex(track) {
    return Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
  }
  function preload(track) {
    var i = slideIndex(track), slides = track.children;
    for (var k = i - 1; k <= i + 1; k++) {
      each(slides[(k + slides.length) % slides.length].querySelectorAll('img'), function (img) {
        if (img.loading === 'lazy') img.loading = 'eager';
      });
    }
  }
  function go(track, step) {
    var n = track.children.length, i = slideIndex(track), j = (i + step + n) % n;
    var jump = Math.abs(j - i) > 1;
    track.scrollTo({ left: j * track.clientWidth, behavior: jump || reduceMotion ? 'auto' : 'smooth' });
    preload(track);
  }
  var ctrlTimer = null;
  document.addEventListener('click', function (e) {
    var car = e.target.closest && e.target.closest('.carousel');
    if (car) {
      // Beim Antippen (Handy) die Pfeile für einige Sekunden zeigen
      car.classList.add('ctrl');
      clearTimeout(ctrlTimer);
      ctrlTimer = setTimeout(function () { car.classList.remove('ctrl'); }, 3000);
    }
    var btn = e.target.closest && e.target.closest('.car-btn');
    if (!btn) return;
    var track = btn.parentNode.querySelector('.car-track');
    go(track, btn.classList.contains('car-prev') ? -1 : 1);
  });
  document.addEventListener('keydown', function (e) {
    var track = e.target.closest && e.target.closest('.car-track');
    if (!track || (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight')) return;
    e.preventDefault();
    go(track, e.key === 'ArrowLeft' ? -1 : 1);
  });
  document.addEventListener('scroll', function (e) {
    if (e.target.classList && e.target.classList.contains('car-track')) preload(e.target);
  }, true);
})();
