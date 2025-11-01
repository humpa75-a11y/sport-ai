import asyncio
from playwright.async_api import async_playwright
import json
import csv
from datetime import datetime

FLASH_URL = "https://www.flashscore.nl/eredivisie/#/dWKtjvdd/standen/totaal/"

async def scrape_flashscore_eredivisie():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.goto(FLASH_URL)
        await page.wait_for_timeout(3000)

        # Accept cookies if popup appears
        try:
            await page.click('button:has-text("Akkoord")')
        except:
            pass

        # Scrape standings table
        standings = []
        try:
            rows = await page.query_selector_all('div.league-table__body > div.league-table__row')
            for row in rows:
                cells = await row.query_selector_all('div.league-table__cell')
                if len(cells) >= 10:
                    team = await cells[1].inner_text()
                    played = await cells[2].inner_text()
                    wins = await cells[3].inner_text()
                    draws = await cells[4].inner_text()
                    losses = await cells[5].inner_text()
                    goals = await cells[6].inner_text()
                    points = await cells[9].inner_text()
                    standings.append({
                        "team": team,
                        "played": played,
                        "wins": wins,
                        "draws": draws,
                        "losses": losses,
                        "goals": goals,
                        "points": points
                    })
        except Exception as e:
            print(f"Standings scrape error: {e}")

            # Scrape all matches (fixtures/results)
            matches = []
            try:
                match_rows = await page.query_selector_all('div.event__match')
                for mrow in match_rows:
                    home = await mrow.query_selector('div.event__participant--home')
                    away = await mrow.query_selector('div.event__participant--away')
                    date = await mrow.query_selector('div.event__time')
                    score = await mrow.query_selector('div.event__scores')
                    match = {
                        "home_team": await home.inner_text() if home else None,
                        "away_team": await away.inner_text() if away else None,
                        "date": await date.inner_text() if date else None,
                        "score": await score.inner_text() if score else None
                    }
                    matches.append(match)
            except Exception as e:
                print(f"Matches scrape error: {e}")

            # Save matches to JSON/CSV
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            matches_json_path = f"flashscore_eredivisie_matches_{ts}.json"
            matches_csv_path = f"flashscore_eredivisie_matches_{ts}.csv"
            with open(matches_json_path, "w", encoding="utf-8") as f:
                json.dump(matches, f, ensure_ascii=False, indent=2)
            if matches:
                with open(matches_csv_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=matches[0].keys())
                    writer.writeheader()
                    writer.writerows(matches)
            print(f"✅ Matches saved: {matches_json_path}, {matches_csv_path}")
        # Save to JSON/CSV
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = f"flashscore_eredivisie_standings_{ts}.json"
        csv_path = f"flashscore_eredivisie_standings_{ts}.csv"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(standings, f, ensure_ascii=False, indent=2)
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=standings[0].keys())
            writer.writeheader()
            writer.writerows(standings)
        print(f"✅ Standings saved: {json_path}, {csv_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_flashscore_eredivisie())
