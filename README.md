# Portfolio Price Feed

Price feed minimale per Portfolio Performance.

## Configurazione

1. Crea un repository GitHub e carica tutti i file.
2. Attiva GitHub Pages usando il branch `main` e la cartella `/ (root)`.
3. Per aggiungere strumenti modifica `isins.json`.
4. La GitHub Action aggiorna i prezzi nei giorni feriali.
5. In Portfolio Performance usa il file JSON dell'ISIN come feed.

## JSON

Per `IT0005696338`:

`prices/IT0005696338.json`

In Portfolio Performance:
- Feed URL: `https://TUOACCOUNT.github.io/NOME-REPO/prices/IT0005696338.json`
- Path to Date: `$[*].date` oppure, se si usa la struttura `quotes`, `$.quotes[*].date`
- Path to Close: `$[*].close` oppure `$.quotes[*].close`

Nota: prima dell'uso definitivo va verificato il parsing reale della pagina Borsa Italiana e il formato JSON scelto.
