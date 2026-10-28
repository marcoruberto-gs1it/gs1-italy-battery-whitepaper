#!/usr/bin/env python3
"""Genera il sito statico a partire dai frammenti in _src/pagine/.

Uso: python3 _src/build.py   (dalla root del progetto)
Ogni frammento contiene solo il corpo della pagina, a partire dal <h1>.
"""
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src" / "pagine"

SITE_TITLE = "Linee guida GS1 sulle batterie"
SITE_DESC = ("Linee guida GS1 per l'implementazione del Regolamento (UE) 2023/1542 "
             "sulle batterie — edizione italiana a cura di GS1 Italy")

NAV = [
    ("Parte I — Orientamento e ambito", [
        ("01-executive-summary", "1. Sintesi"),
        ("02-scope-and-purpose", "2. Ambito, finalità e limiti del documento"),
        ("03-how-to-use-this-guideline", "3. Come utilizzare le linee guida"),
        ("04-battery-categories", "4. Determinare la categoria della batteria"),
    ]),
    ("Parte II — Indicazioni per categoria", [
        ("05-portable-batteries", "5. Batterie portatili"),
        ("06-lmt-batteries", "6. Batterie per mezzi di trasporto leggeri"),
        ("07-sli-batteries", "7. Batterie per autoveicoli (SLI)"),
        ("08-industrial-batteries", "8. Batterie industriali"),
        ("09-electric-vehicle-batteries", "9. Batterie per veicoli elettrici"),
    ]),
    ("Parte III — Requisiti comuni e implementazione GS1", [
        ("10-product-sustainability-and-safety", "10. Requisiti di prodotto, sostenibilità e sicurezza"),
        ("11-economic-operators-and-conformity", "11. Operatori economici, conformità e vigilanza del mercato"),
        ("12-battery-and-grouping-identification", "12. Identificazione delle batterie e dei raggruppamenti"),
        ("13-labelling-and-qr-codes", "13. Etichettatura, codici QR e passaporti delle batterie"),
        ("14-due-diligence", "14. Dovere di diligenza per le batterie"),
        ("15-producer-responsibility", "15. Registrazione dei produttori e responsabilità estesa del produttore"),
        ("16-waste-treatment-and-recycling", "16. Raccolta, trattamento e riciclaggio dei rifiuti"),
        ("17-reuse-repurposing-and-remanufacturing", "17. Riutilizzo, cambio di destinazione e rifabbricazione"),
    ]),
    ("Parte IV — Modelli di implementazione ed esempi", [
        ("18-gs1-implementation-models", "18. Modelli di implementazione GS1"),
        ("19-supply-chain-traceability", "19. Tracciabilità della filiera e scambio di informazioni"),
        ("20-worked-examples", "20. Esempi pratici"),
        ("21-gs1-support-summary", "21. Sintesi delle funzioni normative e del supporto GS1"),
    ]),
    ("Parte V — Materiale di riferimento", [
        ("22-glossary", "22. Glossario"),
        ("23-regulatory-reference-tables", "23. Tabelle di riferimento normativo"),
        ("24-sources-and-references", "24. Fonti e riferimenti"),
    ]),
    ("Parte VI — Passaporto della batteria in pratica", [
        ("25-battery-passport-data-points", "25. Data point del passaporto della batteria"),
        ("26-battery-passport-example", "26. Esempio completo: passaporto di una batteria per e-bike"),
    ]),
]

PAGES = [p for _, items in NAV for p in items]


def slugify(text):
    text = unicodedata.normalize("NFKD", html.unescape(re.sub(r"<[^>]+>", "", text)))
    text = text.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "sezione"


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def process(body):
    """Assegna gli id ai titoli, avvolge le tabelle e restituisce l'indice delle h2."""
    toc, used = [], set()

    def heading(m):
        level, inner = m.group(1), m.group(3).strip()
        base = slugify(inner)
        hid, n = base, 2
        while hid in used:
            hid, n = f"{base}-{n}", n + 1
        used.add(hid)
        if level == "2":
            toc.append((hid, strip_tags(inner)))
        anchor = f'<a class="anchor" href="#{hid}" aria-label="Link a questa sezione">#</a>'
        return f'<h{level} id="{hid}">{inner} {anchor}</h{level}>' if level != "1" else f"<h1>{inner}</h1>"

    body = re.sub(r"<h([1-3])([^>]*)>(.*?)</h\1>", heading, body, flags=re.S)
    body = re.sub(r"<table[^>]*>.*?</table>", responsive_table, body, flags=re.S)
    return body, toc


def responsive_table(m):
    """Avvolge la tabella e aggiunge a ogni cella l'intestazione di colonna (data-label),
    usata dal CSS per mostrare la tabella come schede sugli schermi stretti."""
    table = m.group(0)
    head = re.search(r"<thead>(.*?)</thead>", table, re.S)
    labels = [strip_tags(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", head.group(1), re.S)] if head else []

    def row(r):
        cells = iter(labels)
        return re.sub(r"<td([^>]*)>",
                      lambda c: f'<td{c.group(1)} data-label="{html.escape(next(cells, ""))}">', r.group(0))

    table = re.sub(r"<table[^>]*>", "<table>", table, count=1)
    if head:
        table = re.sub(r"<tbody>.*?</tbody>", lambda b: re.sub(r"<tr>.*?</tr>", row, b.group(0), flags=re.S),
                       table, flags=re.S)
    wide = " wide" if len(labels) >= 5 else ""
    return f'<div class="table-wrap{wide}">{table}</div>'


def search_entries(body, slug, page_title):
    """Divide la pagina in sezioni (h1/h2/h3) per l'indice di ricerca."""
    parts = re.split(r'(<h[1-3](?: id="[^"]*")?>.*?</h[1-3]>)', body, flags=re.S)
    entries, heading, anchor = [], page_title, ""
    for part in parts:
        m = re.match(r'<h[1-3](?: id="([^"]*)")?>(.*?)</h[1-3]>', part, re.S)
        if m:
            anchor = m.group(1) or ""
            heading = strip_tags(re.sub(r'<a class="anchor".*?</a>', "", m.group(2)))
            continue
        text = re.sub(r"\s+", " ", strip_tags(re.sub(r"<(td|th|li|p)[^>]*>", " ", part))).strip()
        if text or anchor:
            entries.append({"p": page_title, "h": heading,
                            "u": f"{slug}.html" + (f"#{anchor}" if anchor else ""), "t": text})
    return entries


def sidebar(active):
    out, cur = [], ' aria-current="page"'
    for part, items in NAV:
        links = "".join(
            f'<li><a href="{slug}.html"{cur if slug == active else ""}>{html.escape(t)}</a></li>'
            for slug, t in items)
        out.append(f'<div class="nav-group"><p class="nav-part">{html.escape(part)}</p><ul>{links}</ul></div>')
    return "\n".join(out)


def layout(title, body, active=None, toc=None, pager=""):
    toc_html = ""
    if toc:
        items = "".join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in toc)
        toc_html = f'<aside class="toc" aria-label="In questa pagina"><p class="toc-title">In questa pagina</p><ul>{items}</ul></aside>'
    full_title = f"{title} · {SITE_TITLE}" if active else SITE_TITLE
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(SITE_DESC)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" type="image/png" href="assets/img/favicon-gs1-italy.png">
<script>try{{var t=localStorage.getItem('tema');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body{' class="home"' if not active else ''}>
<a class="skip" href="#contenuto">Vai al contenuto</a>
<header class="topbar">
  <button class="menu-btn" aria-label="Apri il menu" aria-expanded="false" aria-controls="sidebar"><span></span></button>
  <a class="brand" href="index.html"><img class="brand-logo" src="assets/img/logo-gs1-italy.png" alt="GS1 Italy" width="178" height="122"><span class="brand-text">Linee guida sulle batterie<small>Regolamento (UE) 2023/1542</small></span></a>
  <button class="search-btn" type="button" aria-label="Cerca nelle linee guida"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zm9 2-4-4"/></svg><span class="search-label">Cerca</span><kbd>⌘K</kbd></button>
  <span class="badge">Bozza di lavoro</span>
  <button class="theme-btn" aria-label="Cambia tema chiaro/scuro"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.39 5.39 0 0 1-4.4 2.26 5.4 5.4 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/></svg></button>
</header>
<div class="shell">
<nav id="sidebar" class="sidebar" aria-label="Indice">
<a class="nav-home" href="index.html"{' aria-current="page"' if not active else ''}>Panoramica</a>
{sidebar(active)}
</nav>
<div class="backdrop"></div>
<main id="contenuto" class="main">
<article class="doc">
{body}
</article>
{pager}
<footer class="foot">
<p>Edizione italiana a cura di <strong>GS1 Italy</strong> delle linee guida GS1 in Europe sull'implementazione del Regolamento (UE) 2023/1542. Documento di lavoro: i contenuti non costituiscono consulenza legale; fa fede il testo ufficiale del Regolamento.</p>
</footer>
</main>
{toc_html}
</div>
<div class="search-modal" role="dialog" aria-modal="true" aria-label="Ricerca" hidden>
  <div class="search-panel">
    <div class="search-field">
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zm9 2-4-4"/></svg>
      <input type="search" placeholder="Cerca nelle linee guida (es. passaporto, GTIN, articolo 77)" autocomplete="off" spellcheck="false" aria-label="Testo da cercare">
      <button class="search-close" type="button" aria-label="Chiudi la ricerca">Esc</button>
    </div>
    <ul class="search-results" role="listbox"></ul>
    <p class="search-hint"><kbd>↑</kbd><kbd>↓</kbd> per spostarti · <kbd>Invio</kbd> per aprire · <kbd>Esc</kbd> per chiudere</p>
  </div>
</div>
<script src="assets/main.js"></script>
</body>
</html>
"""


def pager(i):
    parts = []
    if i > 0:
        s, t = PAGES[i - 1]
        parts.append(f'<a class="prev" href="{s}.html"><span>Precedente</span>{html.escape(t)}</a>')
    else:
        parts.append('<a class="prev" href="index.html"><span>Precedente</span>Panoramica</a>')
    if i < len(PAGES) - 1:
        s, t = PAGES[i + 1]
        parts.append(f'<a class="next" href="{s}.html"><span>Successiva</span>{html.escape(t)}</a>')
    return f'<nav class="pager" aria-label="Navigazione tra le pagine">{"".join(parts)}</nav>'


def main():
    index = []
    for i, (slug, label) in enumerate(PAGES):
        src = SRC / f"{slug}.html"
        if not src.exists():
            print(f"manca: {src.name}")
            continue
        body, toc = process(src.read_text(encoding="utf-8"))
        m = re.search(r"<h1>(.*?)</h1>", body, re.S)
        title = strip_tags(m.group(1)) if m else label
        index += search_entries(body, slug, title)
        (ROOT / f"{slug}.html").write_text(layout(title, body, slug, toc, pager(i)), encoding="utf-8")

    # File JS (non JSON) così la ricerca funziona anche aprendo le pagine da file://
    data = json.dumps(index, ensure_ascii=False, separators=(",", ":"))
    (ROOT / "assets" / "search-index.js").write_text(f"window.SEARCH_INDEX={data};\n", encoding="utf-8")

    home, _ = process((SRC / "index.html").read_text(encoding="utf-8"))
    (ROOT / "index.html").write_text(layout(SITE_TITLE, home), encoding="utf-8")

    # Pagina dimostrativa del passaporto (layout autonomo, copiata così com'è)
    (ROOT / "esempio-passaporto.html").write_text(
        (ROOT / "_src" / "esempio-passaporto.html").read_text(encoding="utf-8"), encoding="utf-8")

    not_found = ('<h1>Pagina non trovata</h1><p>La pagina richiesta non esiste o è stata spostata.</p>'
                 '<p><a href="index.html">Torna alla panoramica</a></p>')
    (ROOT / "404.html").write_text(layout("Pagina non trovata", not_found, "404"), encoding="utf-8")
    print(f"generate {len(PAGES) + 2} pagine")


if __name__ == "__main__":
    main()
