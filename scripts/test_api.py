import requests
import os

key = os.environ.get('API_FOOTBALL_KEY')
print(f"API Key: {key[:10]}...")

headers = {'x-apisports-key': key}

# Test 1: Check available seasons for Premier League
print("\nTest 1: Available seasons for Premier League...")
response = requests.get('https://v3.football.api-sports.io/leagues/seasons', headers=headers)
print(f"Status: {response.status_code}")
data = response.json()
seasons = data.get('response', [])
print(f"Available seasons: {seasons[-10:]}")  # Last 10 seasons

# Test 2: Get fixtures with current parameter
print("\nTest 2: Current fixtures (live/upcoming)...")
response = requests.get('https://v3.football.api-sports.io/fixtures?league=39&season=2024', headers=headers)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Results: {data.get('results')}")

if data.get('results', 0) > 0:
    fixture = data['response'][0]
    print(f"Sample: {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}")
    print(f"Date: {fixture['fixture']['date']}")
