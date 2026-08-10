import json
import re
from pathlib import Path
from datetime import datetime

import requests


ROOT = Path(__file__).resolve().parent


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PortfolioPriceFeed/1.0)"
}


def get_price(isin, market):

    if market == "MOT":
        url = (
            f"https://www.borsaitaliana.it/borsa/obbligazioni/mot/btp/"
            f"scheda/{isin}-MOTX.html?lang=it"
        )

        price_label = "Prezzo ufficiale"

    elif market == "SEDX":
        url = (
            f"https://www.borsaitaliana.it/borsa/cw-e-certificates/"
            f"scheda/{isin}-SEDX.html?lang=it"
        )

        price_label = "Prezzo di riferimento"

    else:
        raise RuntimeError(
            f"Mercato non supportato per {isin}: {market}"
        )

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    html = r.text

    # ---------------------------------------------------------
    # MOT - BTP
    # ---------------------------------------------------------

    if market == "MOT":

        pattern = (
            r"Prezzo ufficiale.*?([0-9]+,[0-9]+).*?"
            r"Data Pr Ufficiale.*?([0-9]{2}/[0-9]{2}/[0-9]{2})"
        )

        m = re.search(
            pattern,
            html,
            re.S
        )

        if not m:
            raise RuntimeError(
                f"{price_label} non trovato per {isin}"
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

    # ---------------------------------------------------------
    # SEDX - Certificati
    # ---------------------------------------------------------

    elif market == "SEDX":

        # Prezzo di riferimento
        price_match = re.search(
            r"Prezzo di riferimento.*?([0-9]+,[0-9]+)",
            html,
            re.S
        )

        if not price_match:
            raise RuntimeError(
                f"{price_label} non trovato per {isin}"
            )

        price = float(
            price_match.group(1)
            .replace(".", "")
            .replace(",", ".")
        )

        # Per i certificati utilizziamo sempre la data odierna.
        # Lo script viene eseguito una volta al giorno.
        date = datetime.now().date().isoformat()

    return date, price


def generate_html(isin, quotes):

    rows = []

    for date, price in quotes.items():

        rows.append(
            f"""        <tr>
        <td>{date}</td>
        <td>{price}</td>
    </tr>"""
        )

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>{isin}</title>
</head>
<body>
    <table>
        <thead>
            <tr>
                <th>Data</th>
                <th>Prezzo</th>
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
        (ROOT / "isins.json").read_text(
            encoding="utf-8"
        )
    )

    for item in instruments:

        isin = item["isin"]
        market = item["market"]

        date, price = get_price(
            isin,
            market
        )

        path = ROOT / "prices" / f"{isin}.json"

        if path.exists():

            existing = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            if isinstance(existing, dict):
                old_quotes = existing.get(
                    "quotes",
                    []
                )
            else:
                old_quotes = existing

        else:
            old_quotes = []

        quotes = {
            q["date"]: q["close"]
            for q in old_quotes
        }

        quotes[date] = price

        quotes = dict(
            sorted(quotes.items())
        )

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

        html_path = generate_html(
            isin,
            quotes
        )

        print(
            f"{isin} [{market}] "
            f"{date} {price} "
            f"-> JSON + {html_path.name}"
        )


if __name__ == "__main__":
    main()
