import os
import requests
import pandas as pd
from tabulate import tabulate
from dotenv import load_dotenv

# Laad .env variabelen
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
DATASET_ID = os.getenv("DATASET_ID")

BASE = f"https://api.apify.com/v2/datasets/{DATASET_ID}/items"
params = {"clean": "true", "format": "json"}
headers = {}
if APIFY_TOKEN:
    headers["Authorization"] = f"Bearer {APIFY_TOKEN}"

print("🔄 Data ophalen van Apify...")

resp = requests.get(BASE, params=params, headers=headers, timeout=30)
resp.raise_for_status()
items = resp.json()

if not items:
    print("⚠️ Geen resultaten gevonden.")
    exit(0)

df = pd.DataFrame(items)[["id", "home", "away", "time", "league"]]
print(tabulate(df, headers="keys", tablefmt="github", showindex=False))

df.to_csv("odds_latest.csv", index=False)
print("\n✅ Data opgeslagen in odds_latest.csv")
