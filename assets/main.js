// Menu mobile, tema chiaro/scuro ed evidenziazione della sezione corrente.
(function () {
  var body = document.body;
  var menuBtn = document.querySelector('.menu-btn');
  var backdrop = document.querySelector('.backdrop');

  function setNav(open) {
    body.classList.toggle('nav-open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Chiudi il menu' : 'Apri il menu');
  }
  menuBtn.addEventListener('click', function () { setNav(!body.classList.contains('nav-open')); });
  backdrop.addEventListener('click', function () { setNav(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setNav(false); });

  // Porta in vista la voce corrente scorrendo solo la sidebar, non la pagina.
  var sidebar = document.querySelector('.sidebar');
  var current = sidebar.querySelector('a[aria-current="page"]');
  if (current) sidebar.scrollTop = current.offsetTop - sidebar.clientHeight / 2;

  document.querySelector('.theme-btn').addEventListener('click', function () {
    var root = document.documentElement;
    var dark = root.dataset.theme
      ? root.dataset.theme === 'dark'
      : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    try { localStorage.setItem('tema', root.dataset.theme); } catch (e) {}
  });

  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (!links.length || !('IntersectionObserver' in window)) return;
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
  var visible = {};
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting; });
    var heads = document.querySelectorAll('.doc h2[id]');
    var active = null;
    for (var i = 0; i < heads.length; i++) {
      if (visible[heads[i].id]) { active = heads[i].id; break; }
      if (heads[i].getBoundingClientRect().top < 120) active = heads[i].id;
    }
    links.forEach(function (a) { a.classList.remove('active'); });
    if (active && byId[active]) byId[active].classList.add('active');
  }, { rootMargin: '-64px 0px -60% 0px' });
  document.querySelectorAll('.doc h2[id]').forEach(function (h) { observer.observe(h); });
})();

// Ricerca full-text: l'indice (assets/search-index.js) viene caricato alla prima apertura.
(function () {
  var modal = document.querySelector('.search-modal');
  var input = modal.querySelector('input');
  var list = modal.querySelector('.search-results');
  var entries = null;
  var results = [];
  var selected = 0;

  function norm(s) {
    return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }
  function esc(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function loadIndex(done) {
    if (entries) return done();
    var s = document.createElement('script');
    s.src = 'assets/search-index.js';
    s.onload = function () {
      entries = window.SEARCH_INDEX.map(function (e) {
        return { e: e, p: norm(e.p), h: norm(e.h), t: norm(e.t) };
      });
      done();
    };
    document.head.appendChild(s);
  }

  // Evidenzia i termini in un testo originale usando le posizioni del testo normalizzato.
  function highlight(text, terms) {
    var n = norm(text);
    var marks = [];
    terms.forEach(function (t) {
      var i = n.indexOf(t);
      while (i !== -1) { marks.push([i, i + t.length]); i = n.indexOf(t, i + t.length); }
    });
    marks.sort(function (a, b) { return a[0] - b[0]; });
    var out = '', pos = 0;
    marks.forEach(function (m) {
      if (m[0] < pos) return;
      out += esc(text.slice(pos, m[0])) + '<mark>' + esc(text.slice(m[0], m[1])) + '</mark>';
      pos = m[1];
    });
    return out + esc(text.slice(pos));
  }

  function excerpt(item, terms) {
    var text = item.e.t;
    var first = -1;
    terms.forEach(function (t) {
      var i = item.t.indexOf(t);
      if (i !== -1 && (first === -1 || i < first)) first = i;
    });
    if (first === -1) return esc(text.slice(0, 160)) + (text.length > 160 ? '…' : '');
    var start = Math.max(0, first - 60);
    var end = Math.min(text.length, first + 140);
    return (start > 0 ? '…' : '') + highlight(text.slice(start, end), terms) + (end < text.length ? '…' : '');
  }

  function search() {
    var terms = norm(input.value).split(/\s+/).filter(Boolean);
    if (!terms.length || !entries) {
      results = [];
      list.innerHTML = '<li class="search-empty">Digita una parola o un riferimento, ad esempio «passaporto», «SSCC» o «articolo 46».</li>';
      return;
    }
    results = [];
    entries.forEach(function (item) {
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        var t = terms[i];
        var inH = item.h.indexOf(t) !== -1;
        var inP = item.p.indexOf(t) !== -1;
        var count = item.t.split(t).length - 1;
        if (!inH && !inP && !count) return;
        score += (inH ? 10 : 0) + (inP ? 3 : 0) + Math.min(count, 5);
      }
      results.push({ item: item, score: score });
    });
    results.sort(function (a, b) { return b.score - a.score; });
    results = results.slice(0, 40);
    selected = 0;
    if (!results.length) {
      list.innerHTML = '<li class="search-empty">Nessun risultato per «' + esc(input.value.trim()) + '».</li>';
      return;
    }
    list.innerHTML = results.map(function (r, i) {
      var e = r.item.e;
      var head = e.h !== e.p ? '<span class="sr-head">' + highlight(e.h, terms) + '</span>' : '';
      return '<li role="option"' + (i === 0 ? ' aria-selected="true"' : '') + '><a href="' + esc(e.u) + '">' +
        '<span class="sr-page">' + esc(e.p) + '</span>' + head +
        '<span class="sr-text">' + excerpt(r.item, terms) + '</span></a></li>';
    }).join('');
  }

  function select(i) {
    var items = list.querySelectorAll('[role="option"]');
    if (!items.length) return;
    selected = (i + items.length) % items.length;
    items.forEach(function (el, k) { el.setAttribute('aria-selected', String(k === selected)); });
    items[selected].scrollIntoView({ block: 'nearest' });
  }

  function open() {
    modal.hidden = false;
    document.body.classList.add('search-open');
    input.focus();
    input.select();
    loadIndex(search);
  }
  function close() {
    modal.hidden = true;
    document.body.classList.remove('search-open');
  }

  document.querySelector('.search-btn').addEventListener('click', open);
  modal.querySelector('.search-close').addEventListener('click', close);
  modal.addEventListener('click', function (e) { if (e.target === modal) close(); });
  list.addEventListener('click', function (e) { if (e.target.closest('a')) close(); });
  input.addEventListener('input', search);

  document.addEventListener('keydown', function (e) {
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      modal.hidden ? open() : close();
    } else if (e.key === '/' && !typing && modal.hidden) {
      e.preventDefault();
      open();
    } else if (!modal.hidden) {
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowDown') { e.preventDefault(); select(selected + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); select(selected - 1); }
      else if (e.key === 'Enter') {
        var link = list.querySelector('[aria-selected="true"] a');
        if (link) { e.preventDefault(); close(); location.href = link.href; }
      }
    }
  });

  // Su Windows/Linux la scorciatoia è Ctrl+K.
  if (!/Mac|iPhone|iPad/.test(navigator.platform)) {
    document.querySelector('.search-btn kbd').textContent = 'Ctrl K';
  }
})();
