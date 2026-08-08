import json
import re
from pathlib import Path
from datetime import datetime

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PortfolioPriceFeed/1.0)"
}


def get_price(isin):
    url = (
        "https://www.borsaitaliana.it/borsa/obbligazioni/mot/btp/"
        f"scheda/{isin}-MOTX.html?lang=it"
    )

    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    m = re.search(
        r"Prezzo ufficiale\s+([0-9]+[,.][0-9]+)\s+"
        r"Data Pr Ufficiale\s+([0-9]{2}/[0-9]{2}/[0-9]{2})",
        text
    )

    if not m:
        raise RuntimeError(
            f"Prezzo ufficiale non trovato per {isin}"
        )

    price = float(
        m.group(1)
        .replace(".", "")
        .replace(",", ".")
    )

    date = datetime.strptime(
        m.group(2),
        "%d/%m/%y"
    ).date().isoformat()

    return date, price


def generate_html(isin, quotes):
    """
    Genera una pagina HTML compatibile con
    Portfolio Performance - Table on Website.
    """

    rows = []

    for date, price in quotes.items():
        rows.append(
            f"""        <tr>
            <td>{date}</td>
            <td>{price}</td>
        </tr>"""
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{isin} Historical Prices</title>
</head>
<body>

<table>
    <thead>
        <tr>
            <th>Date</th>
            <th>Close</th>
        </tr>
    </thead>

    <tbody>
{chr(10).join(rows)}
    </tbody>
</table>

</body>
</html>
"""

    path = ROOT / "prices" / f"{isin}.html"

    path.write_text(
        html,
        encoding="utf-8"
    )

    return path


def main():

    instruments = json.loads(
        (ROOT / "isins.json").read_text(encoding="utf-8")
    )

    for item in instruments:

        isin = item["isin"]

        date, price = get_price(isin)

        path = ROOT / "prices" / f"{isin}.json"

        # Legge lo storico esistente
        if path.exists():

            existing = json.loads(
                path.read_text(encoding="utf-8")
            )

            # Compatibilità con il vecchio formato
            if isinstance(existing, dict):
                old_quotes = existing.get("quotes", [])
            else:
                old_quotes = existing

        else:
            old_quotes = []

        # Trasforma lo storico in un dizionario data -> prezzo
        quotes = {
            q["date"]: q["close"]
            for q in old_quotes
        }

        # Aggiunge/aggiorna la quotazione
        quotes[date] = price

        # Ordina cronologicamente
        quotes = dict(sorted(quotes.items()))

        # JSON
        data = [
            {
                "date": d,
                "close": quotes[d]
            }
            for d in quotes
        ]

        path.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            ) + "\n",
            encoding="utf-8"
        )

        # HTML per Portfolio Performance
        html_path = generate_html(isin, quotes)

        print(
            f"{isin} {date} {price} "
            f"-> JSON + {html_path.name}"
        )


if __name__ == "__main__":
    main()
