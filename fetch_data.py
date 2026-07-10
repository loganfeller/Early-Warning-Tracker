import requests, json
from datetime import datetime

FRED_KEY = "67122fb3c41446ce24860a51a2416d35"
BASE = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    "US":  {"yc": None,              "hp": "QUSN628BIS"},
    "CA":  {"yc": "IRLTLT01CAM156N", "hp": "QCAN628BIS"},
    "JP":  {"yc": "IRLTLT01JPM156N", "hp": "QJPN628BIS"},
    "DE":  {"yc": "IRLTLT01DEM156N", "hp": "QDER628BIS"},
    "FR":  {"yc": "IRLTLT01FRM156N", "hp": "QFRR628BIS"},
    "IT":  {"yc": "IRLTLT01ITM156N", "hp": "QITR628BIS"},
    "GB":  {"yc": "IRLTLT01GBM156N", "hp": "QGBR628BIS"},
}

def fetch(series_id):
   r = requests.get(BASE, params={
        "series_id": series_id,
        "api_key": FRED_KEY,
        "file_type": "json",
        "limit": 5000,
        "sort_order": "desc",
    })
    r.raise_for_status()
    obs = r.json().get("observations", [])
    return {
        o["date"]: float(o["value"])
        for o in obs if o["value"] != "."
    }

def fetch_us_yield_curve():
    dgs10 = fetch("DGS10")
    dgs2  = fetch("DGS2")
    print(f"  DGS10: {len(dgs10)} obs, DGS2: {len(dgs2)} obs")
    dates = sorted(set(dgs10.keys()) & set(dgs2.keys()))
    result = [{"date": d, "value": round(dgs10[d] - dgs2[d], 2)} for d in dates]
    print(f"  Spread computed: {len(result)} obs, last: {result[-1]}")
    return result

def fetch_series(series_id):
    raw = fetch(series_id)
    return [{"date": d, "value": v} for d, v in sorted(raw.items())]

data = {"updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "countries": {}}

for code, series in SERIES.items():
    print(f"Fetching {code}...")
    try:
        if code == "US":
            yc = fetch_us_yield_curve()
        else:
            yc = fetch_series(series["yc"])
    except Exception as e:
        print(f"  YC failed: {e}")
        yc = []
    try:
        hp = fetch_series(series["hp"])
    except Exception as e:
        print(f"  HP failed: {e}")
        hp = []
    data["countries"][code] = {"yieldCurve": yc, "housing": hp}
    print(f"  YC: {len(yc)} obs, HP: {len(hp)} obs")

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Wrote data.json")
