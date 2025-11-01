import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def fetch_knvb_eredivisie_results():
    url = "https://www.knvb.nl/competities/eredivisie/uitslagen"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    # Zoek alle wedstrijdblokken (pas deze selector aan als nodig)
    for match in soup.select(".match-block, .match-row, .match-list__item"):  # selector kan variëren
        try:
            home = match.select_one(".team-home, .match-list__team--home").get_text(strip=True)
            away = match.select_one(".team-away, .match-list__team--away").get_text(strip=True)
            score = match.select_one(".score, .match-list__score").get_text(strip=True)
            date = match.select_one(".date, .match-list__date").get_text(strip=True)
            results.append({
                "home_team": home,
                "away_team": away,
                "score": score,
                "date": date
            })
        except Exception:
            continue
    return results

if __name__ == "__main__":
    uitslagen = fetch_knvb_eredivisie_results()
    with open("data/eredivisie_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "fetched_at": datetime.now().isoformat(),
            "results": uitslagen
        }, f, ensure_ascii=False, indent=2)
    print(f"{len(uitslagen)} uitslagen opgeslagen in data/eredivisie_results.json")
