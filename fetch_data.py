import requests, json, os
from datetime import datetime

FRED_KEY = "67122fb3c41446ce24860a51a2416d35"
BASE = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    "US":  {"yc": "T10Y2Y",          "hp": "QUSN628BIS"},
    "CA":  {"yc": "IRLTLT01CAM156N", "hp": "QCAN628BIS"},
    "JP":  {"yc": "IRLTLT01JPM156N", "hp": "QJPN628BIS"},
    "DE":  {"yc": "IRLTLT01DEM156N", "hp": "QDER628BIS"},
    "FR":  {"yc": "IRLTLT01FRM156N", "hp": "QFRR628BIS"},
    "IT":  {"yc": "IRLTLT01ITM156N", "hp": "QITR628BIS"},
    "GB":  {"yc": "IRLTLT01GBM156N", "hp": "QGBR628BIS"},
}

def fetch(series_id, limit=60):
    r = requests.get(BASE, params={
        "series_id": series_id,
        "api_key": FRED_KEY,
        "file_type": "json",
        "limit": limit,
        "sort_order": "desc"
    })
    r.raise_for_status()
    obs = r.json().get("observations", [])
    return [
        {"date": o["date"], "value": float(o["value"])}
        for o in obs if o["value"] != "."
    ][::-1]  # reverse to chronological

data = {"updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "countries": {}}

for code, series in SERIES.items():
    print(f"Fetching {code}...")
    try:
        yc = fetch(series["yc"])
    except Exception as e:
        print(f"  YC failed: {e}")
        yc = []
    try:
        hp = fetch(series["hp"])
    except Exception as e:
        print(f"  HP failed: {e}")
        hp = []
    data["countries"][code] = {"yieldCurve": yc, "housing": hp}
    print(f"  YC: {len(yc)} obs, HP: {len(hp)} obs")

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Wrote data.json")
