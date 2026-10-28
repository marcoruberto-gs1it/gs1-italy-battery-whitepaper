# Linee guida GS1 sulle batterie — edizione italiana

Versione italiana, a cura di GS1 Italy, delle linee guida GS1 in Europe sull'implementazione del Regolamento (UE) 2023/1542 (fonte: [gs1turkiye/batterywhitepaper-web](https://github.com/gs1turkiye/batterywhitepaper-web)).

Sito statico in puro HTML/CSS, senza framework né dipendenze: si apre direttamente `index.html` nel browser o si pubblica la cartella così com'è (es. GitHub Pages).

## Struttura

```
index.html, 01-…24-*.html, 404.html   pagine generate (non modificare a mano)
assets/style.css                       stile (palette GS1, tema chiaro/scuro, responsive)
assets/main.js                         menu mobile, cambio tema, indice "In questa pagina", ricerca (⌘K / Ctrl+K)
assets/search-index.js                 indice di ricerca generato dal build (non modificare a mano)
assets/img/                            logo e favicon ufficiali GS1 Italy (da gs1it.org)
_src/pagine/*.html                     contenuti in italiano: solo il corpo di ogni pagina
_src/build.py                          applica il layout comune e genera le pagine
```

## Modificare i contenuti

1. Modificare il frammento in `_src/pagine/` (i titoli `h2`/`h3` ricevono gli ID automaticamente).
2. Rigenerare le pagine:

```sh
python3 _src/build.py
```

Menu laterale, titoli di navigazione e testo del piè di pagina si trovano in `_src/build.py` (`NAV`, `layout`).
