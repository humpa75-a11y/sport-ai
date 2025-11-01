import requests
import pandas as pd
import os
from dotenv import load_dotenv

# ✅ Laad .env
load_dotenv()

# ✅ Haal de API key op
API_KEY = os.getenv("ODDS_API_KEY")

# ✅ URL van Odds API
url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"

# ✅ Parameters + KEY in de URL (zoals Odds-API het verwacht)
params = {
    'regions': 'eu',
    'markets': 'h2h',
    'oddsFormat': 'decimal',
    'apiKey': API_KEY  # 👉 deze moet zo in de params
}

# ✅ Stuur verzoek
print("🔄 Data ophalen van The Odds API...")
response = requests.get(url, params=params)

# ✅ Verwerk resultaat
if response.status_code == 200:
    data = response.json()
    df = pd.json_normalize(data)
    df.to_csv("odds_latest.csv", index=False)
    print("✅ Odds opgeslagen in odds_latest.csv")
else:
    print(f"❌ Fout ({response.status_code}): {response.text}")
