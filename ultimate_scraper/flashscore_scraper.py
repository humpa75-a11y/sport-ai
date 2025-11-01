"""
Flashscore Scraper Module
Scrapes football standings, matches, and results from Flashscore.nl
Stealth-enabled using Playwright.
"""
import json
import os
from playwright.sync_api import sync_playwright

def scrape_flashscore(user_agent, output_dir):
	url = "https://www.flashscore.nl/voetbal/"
	print(f"🔎 Scrapen Flashscore: {url}")
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
	with open(os.path.join(output_dir, 'flashscore_matches.json'), 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	print(f"✅ Flashscore data opgeslagen in {output_dir}/flashscore_matches.json")
