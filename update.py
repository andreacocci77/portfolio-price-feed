import json, re
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PortfolioPriceFeed/1.0)"}

def get_price(isin):
    url = f"https://www.borsaitaliana.it/borsa/obbligazioni/mot/btp/scheda/{isin}-MOTX.html?lang=it"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    m = re.search(r"Prezzo ufficiale\s+([0-9]+[,.][0-9]+)\s+Data Pr Ufficiale\s+([0-9]{2}/[0-9]{2}/[0-9]{2})", text)
    if not m:
        raise RuntimeError(f"Prezzo ufficiale non trovato per {isin}")
    price = float(m.group(1).replace(".", "").replace(",", "."))
    date = datetime.strptime(m.group(2), "%d/%m/%y").date().isoformat()
    return date, price

def main():
    instruments = json.loads((ROOT/"isins.json").read_text(encoding="utf-8"))
    for item in instruments:
        isin = item["isin"]
        date, price = get_price(isin)
        path = ROOT/"prices"/f"{isin}.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"quotes":[]}
        quotes = {q["date"]: q["close"] for q in data.get("quotes", [])}
        quotes[date] = price
        data["quotes"] = [{"date": d, "close": quotes[d]} for d in sorted(quotes)]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print(isin, date, price)

if __name__ == "__main__":
    main()
