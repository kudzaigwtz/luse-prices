"""Fetch LuSE prices from the homepage ticker and save them to prices.json."""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

URL = "https://www.luse.co.zm/"
TICKERS = ["ZNCO", "CECZ", "ATEL", "CHIL", "BATZ", "KLRE", "SCBL"]  # add more here

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def page_text():
    req = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", errors="replace")
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html).replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", html)


def price(text, ticker):
    m = re.search(
        r"\b" + ticker + r"\b[^0-9]{0,20}(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)", text
    )
    return float(m.group(1).replace(",", "")) if m else None


def main():
    try:
        text = page_text()
    except Exception as e:  # HTTP 403 etc. -> fail loudly so the Action turns red
        print("FETCH FAILED:", e)
        sys.exit(1)

    prices = {}
    for t in TICKERS:
        p = price(text, t)
        print(t, "->", p)
        if p and p > 0:
            prices[t] = p

    if not prices:
        print("No prices found - page layout may have changed.")
        sys.exit(1)

    out = {"updated": datetime.now(timezone.utc).isoformat(), "prices": prices}
    with open("prices.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Saved", len(prices), "prices")


if __name__ == "__main__":
    main()
