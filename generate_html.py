import json
from pathlib import Path

PRICES_DIR = Path("prices")


def generate_html(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    isin = json_file.stem
    html_file = PRICES_DIR / f"{isin}.html"

    rows = []

    for quote in data.get("quotes", []):
        date = quote.get("date")
        close = quote.get("close")

        if date is None or close is None:
            continue

        rows.append(
            f"""        <tr>
            <td>{date}</td>
            <td>{close}</td>
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

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated: {html_file}")


for json_file in PRICES_DIR.glob("*.json"):
    generate_html(json_file)
