"""
Toto Scraper Module
Scrapes football odds, matches, and results from Toto.nl
Stealth-enabled using Playwright.
"""
import json
import os
from playwright.sync_api import sync_playwright

def scrape_toto(user_agent, output_dir):
	url = "https://sport.toto.nl/voetbal"
	print(f"🔎 Scrapen Toto: {url}")
	data = []
	with sync_playwright() as p:
		browser = p.chromium.launch(headless=True)
		context = browser.new_context(user_agent=user_agent)
		page = context.new_page()
		page.goto(url)
		page.wait_for_timeout(4000)
		# TODO: Voeg parsing van odds/wedstrijden toe
		browser.close()
	os.makedirs(output_dir, exist_ok=True)
	with open(os.path.join(output_dir, 'toto_matches.json'), 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	print(f"✅ Toto data opgeslagen in {output_dir}/toto_matches.json")
