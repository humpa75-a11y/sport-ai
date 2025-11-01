"""
Unibet Scraper
Scrapt alle voetbal odds, wedstrijden en resultaten van Unibet.nl
Stealth, Playwright, output naar JSON/CSV
"""
import json
import os
from playwright.sync_api import sync_playwright

def scrape_unibet(user_agent, output_dir):
	url = "https://www.unibet.nl/betting/sports/filter/football/all/matches"
	print(f"🔎 Scrapen Unibet: {url}")
	data = []
	with sync_playwright() as p:
		browser = p.chromium.launch(headless=True)
		context = browser.new_context(user_agent=user_agent)
		page = context.new_page()
		page.goto(url)
		page.wait_for_timeout(4000)
		# Parse alle voetbalwedstrijden en odds
		wedstrijden = page.query_selector_all('div[data-test="Event"]')
		for w in wedstrijden:
			try:
				thuis = w.query_selector('span[data-test="EventParticipantName--participant1"]')
				uit = w.query_selector('span[data-test="EventParticipantName--participant2"]')
				odds = w.query_selector_all('span[data-test^="OutcomeButton--odds"]')
				competitie = w.query_selector('span[data-test="EventCompetitionName"]')
				tijd = w.query_selector('span[data-test="EventTime"]')
				match = {
					'thuisteam': thuis.inner_text().strip() if thuis else '',
					'uitteam': uit.inner_text().strip() if uit else '',
					'competitie': competitie.inner_text().strip() if competitie else '',
					'speeltijd': tijd.inner_text().strip() if tijd else '',
					'odds': [o.inner_text().strip() for o in odds] if odds else [],
				}
				data.append(match)
			except Exception as e:
				print(f"⚠️ Fout bij parsen van wedstrijd: {e}")
		browser.close()
	# Sla data op
	os.makedirs(output_dir, exist_ok=True)
	with open(os.path.join(output_dir, 'unibet_matches.json'), 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	print(f"✅ Unibet data opgeslagen in {output_dir}/unibet_matches.json")
