import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

# === Instellingen ===
# Zet hier je actor-id in de vorm "username/actor-name"
ACTOR_ID = "fashionable_education~oddsapi-fixtures-bridge"



# Laad .env
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

HEADERS = {"Authorization": f"Bearer {APIFY_TOKEN}"} if APIFY_TOKEN else {}

def get_latest_dataset_id():
    """Haalt de default dataset id op van de laatste geslaagde actor-run."""
    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs/last"
    params = {"status": "SUCCEEDED"}
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    # Zowel 'data' als direct veld kunnen voorkomen; we proberen beide
    run = data.get("data", data)
    dsid = run.get("defaultDatasetId")
    if not dsid:
        raise RuntimeError("Geen defaultDatasetId gevonden bij laatste run.")
    return dsid

def pull_once():
    try:
        dataset_id = get_latest_dataset_id()
        base = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        params = {"clean": "true", "format": "json"}
        r = requests.get(base, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        items = r.json() or []
        if not items:
            print("⚠️  Geen items gevonden in dataset.")
            return

        df = pd.DataFrame(items)[["id", "home", "away", "time", "league"]]
        df.to_csv("odds_latest.csv", index=False)
        print(f"✅ {len(df)} regels opgehaald en opgeslagen (dataset {dataset_id}).")
    except Exception as e:
        print(f"❗ Fout tijdens ophalen: {e}")

if __name__ == "__main__":
    print("🔄 Live sync gestart — elke 60 seconden vernieuwen (Ctrl + C om te stoppen)")
    while True:
        pull_once()
        time.sleep(60)

