import asyncio
from playwright.async_api import async_playwright
import json
import datetime

async def scrape_unibet():
    url = "https://www.unibet.nl/betting/sports/filter/football/all/matches"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="nl-NL"
        )
        page = await context.new_page()
        network_data = []
        async def handle_response(response):
            if "matches" in response.url and response.status == 200:
                try:
                    json_data = await response.json()
                    network_data.append(json_data)
                    with open("unibet_xhr.json", "w", encoding="utf-8") as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"[Unibet] XHR parse error: {e}")
        page.on("response", handle_response)
        await page.goto(url)
        await page.wait_for_timeout(8000)
        # Parse odds/matches uit XHR-data
        results = []
        for entry in network_data:
            # Zoek naar odds/matches in JSON
            if isinstance(entry, dict) and "events" in entry:
                for event in entry["events"]:
                    try:
                        home = event.get("homeTeam", {}).get("name", "")
                        away = event.get("awayTeam", {}).get("name", "")
                        odds_values = []
                        for market in event.get("markets", []):
                            for outcome in market.get("outcomes", []):
                                odds_values.append(outcome.get("odds", ""))
                        results.append({
                            'home_team': home,
                            'away_team': away,
                            'odds': odds_values
                        })
                    except Exception as e:
                        print(f"[Unibet] XHR event parse error: {e}")
                        continue
        print(f"[Unibet] Gevonden matches via XHR: {len(results)}")
        await browser.close()
        return results

async def scrape_toto():
    import random
    url = "https://sport.toto.nl/"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
    ]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=random.choice(user_agents),
            viewport={"width": random.choice([1280, 1366, 1440]), "height": random.choice([800, 900, 1080])},
            locale="nl-NL"
        )
        page = await context.new_page()
        network_data = []
        async def handle_response(response):
            ct = response.headers.get("content-type", "")
            url = response.url
            print(f"[Toto] XHR: {url} | Content-Type: {ct}")
            # Relevante endpoints voor odds/matches
            relevant = any([
                "/event/live/count" in url,
                "/live/information" in url,
                "/api/events" in url,
                "/api/odds" in url,
                "/api/live" in url
            ])
            if relevant and response.status == 200 and "json" in ct:
                try:
                    json_data = await response.json()
                    network_data.append(json_data)
                    fname = f"toto_xhr_{random.randint(1000,9999)}.json"
                    with open(fname, "w", encoding="utf-8") as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"[Toto] XHR parse error: {e}")
            else:
                # Sla raw body op voor analyse
                try:
                    body = await response.body()
                    fname = f"toto_raw_{random.randint(1000,9999)}.bin"
                    with open(fname, "wb") as f:
                        f.write(body)
                except Exception as e:
                    print(f"[Toto] Raw body save error: {e}")
        page.on("response", handle_response)
        await page.goto(url)
        # Stealth: random delay en mouse move
        await page.wait_for_timeout(random.randint(4000, 9000))
        await page.mouse.move(random.randint(100, 800), random.randint(100, 600))
        await page.wait_for_timeout(random.randint(1000, 3000))
        # Parse odds/matches uit XHR-data
        results = []
        for entry in network_data:
            # Zoek naar odds/matches in JSON
            if isinstance(entry, dict):
                # /api/events structuur
                if "events" in entry:
                    for event in entry["events"]:
                        try:
                            home = event.get("homeTeam", {}).get("name", "")
                            away = event.get("awayTeam", {}).get("name", "")
                            odds_values = []
                            for market in event.get("markets", []):
                                for outcome in market.get("outcomes", []):
                                    odds_values.append(outcome.get("odds", ""))
                            results.append({
                                'home_team': home,
                                'away_team': away,
                                'odds': odds_values
                            })
                        except Exception as e:
                            print(f"[Toto] XHR event parse error: {e}")
                            continue
                # /live/information structuur
                elif "liveEvents" in entry:
                    for event in entry["liveEvents"]:
                        try:
                            home = event.get("homeTeam", {}).get("name", "")
                            away = event.get("awayTeam", {}).get("name", "")
                            odds_values = []
                            for market in event.get("markets", []):
                                for outcome in market.get("outcomes", []):
                                    odds_values.append(outcome.get("odds", ""))
                            results.append({
                                'home_team': home,
                                'away_team': away,
                                'odds': odds_values
                            })
                        except Exception as e:
                            print(f"[Toto] XHR live event parse error: {e}")
                            continue
                # /event/live/count structuur (alleen count, geen odds)
                elif "count" in entry:
                    print(f"[Toto] Live event count: {entry['count']}")
        print(f"[Toto] Gevonden matches via XHR: {len(results)}")
        await browser.close()
        return results

async def main():
    print("Scraping Unibet...")
    unibet_data = await scrape_unibet()
    print(f"Unibet: {len(unibet_data)} matches scraped.")
    print("Scraping Toto...")
    toto_data = await scrape_toto()
    print(f"Toto: {len(toto_data)} matches scraped.")
    # Save results
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f'unibet_odds_{now}.json', 'w', encoding='utf-8') as f:
        json.dump(unibet_data, f, ensure_ascii=False, indent=2)
    with open(f'toto_odds_{now}.json', 'w', encoding='utf-8') as f:
        json.dump(toto_data, f, ensure_ascii=False, indent=2)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
