# Linee guida GS1 sulle batterie — edizione italiana

Versione italiana, a cura di GS1 Italy, delle linee guida GS1 in Europe sull'implementazione del Regolamento (UE) 2023/1542 (fonte: [gs1turkiye/batterywhitepaper-web](https://github.com/gs1turkiye/batterywhitepaper-web)).


## Struttura

```
index.html, 01-…27-*.html, 404.html   pagine generate (non modificare a mano)
esempio-passaporto.html                pagina dimostrativa del passaporto (generata da _src/esempio-passaporto.html)
assets/style.css                       stile (palette GS1, tema chiaro/scuro, responsive)
assets/main.js                         menu mobile, cambio tema, indice "In questa pagina", ricerca (⌘K / Ctrl+K)
assets/search-index.js                 indice di ricerca generato dal build (non modificare a mano)
assets/jsonld/                         viste JSON-LD dell'esempio, copiate dal build (non modificare a mano)
assets/img/                            logo e favicon ufficiali GS1 Italy (da gs1it.org)
_src/pagine/*.html                     contenuti in italiano: solo il corpo di ogni pagina
_src/esempio-passaporto.html           pagina dimostrativa (layout autonomo)
_src/jsonld/*.jsonld                   passaporto d'esempio in JSON-LD, una vista per livello di accesso
_src/build.py                          applica il layout comune e genera le pagine
```

## Modificare i contenuti

1. Modificare il frammento in `_src/pagine/` (i titoli `h2`/`h3` ricevono gli ID automaticamente).
2. Rigenerare le pagine:

```sh
python3 _src/build.py
```

Menu laterale, titoli di navigazione e testo del piè di pagina si trovano in `_src/build.py` (`NAV`, `layout`).

## Passaporto d'esempio in JSON-LD

I file in `_src/jsonld/` seguono gli artefatti semantici pubblicati dalla Commissione europea per il DPP Registry (release 1.0.0: core, batterie, sottogruppo LMT). Ci sono quattro viste, `pub`, `res1`, `res2` e `res3`, che corrispondono ai livelli di accesso dell'allegato XIII. Il build le incorpora in `esempio-passaporto.html` e le copia in `assets/jsonld/`. Dopo una modifica, vanno verificate di nuovo con i JSON Schema e le shape SHACL ufficiali.

## Tabelle

Il build avvolge ogni tabella in `div.table-wrap.cols-N` (N = numero di colonne) e copia l'intestazione di colonna in ogni cella (`data-label`). Quando la colonna di testo diventa stretta, il CSS mostra le righe come schede; la soglia dipende dal numero di colonne (2–3 colonne ≤ 560 px, 4 colonne ≤ 620 px, 5 o più ≤ 700 px). Nelle tabelle i codici brevi non vanno a capo, quelli lunghi (URL) vanno a capo solo dopo i separatori.
