import requests
import time

# List of match results (date, home_team, home_goals, away_goals, away_team)
results = [
    ("18 oktober 2025", "NAC Breda", 2, 2, "PEC Zwolle"),
    ("18 oktober 2025", "Ajax", 0, 2, "AZ"),
    ("18 oktober 2025", "FC Utrecht", 3, 1, "FC Volendam"),
    ("18 oktober 2025", "PSV", 2, 1, "Go Ahead Eagles"),
    ("18 oktober 2025", "N.E.C.", 3, 3, "FC Twente"),
    ("5 oktober 2025", "Go Ahead Eagles", 1, 1, "N.E.C."),
    ("5 oktober 2025", "AZ", 2, 1, "Telstar"),
    ("5 oktober 2025", "Feyenoord", 3, 2, "FC Utrecht"),
    ("5 oktober 2025", "FC Twente", 2, 1, "Heracles Almelo"),
    ("4 oktober 2025", "sc Heerenveen", 2, 1, "Excelsior"),
    ("4 oktober 2025", "PEC Zwolle", 0, 4, "PSV"),
    ("4 oktober 2025", "Fortuna Sittard", 1, 0, "FC Volendam"),
    ("4 oktober 2025", "Sparta Rotterdam", 3, 3, "Ajax"),
    ("3 oktober 2025", "NAC Breda", 1, 2, "FC Groningen"),
    ("28 september 2025", "Telstar", 4, 2, "Go Ahead Eagles"),
    ("28 september 2025", "FC Utrecht", 2, 2, "sc Heerenveen"),
    ("28 september 2025", "FC Groningen", 0, 1, "Feyenoord"),
    ("28 september 2025", "N.E.C.", 2, 1, "AZ"),
    ("27 september 2025", "Heracles Almelo", 3, 0, "Sparta Rotterdam"),
    ("27 september 2025", "Excelsior", 1, 2, "PSV"),
    ("27 september 2025", "FC Volendam", 2, 1, "PEC Zwolle"),
    ("27 september 2025", "Ajax", 2, 1, "NAC Breda"),
    ("26 september 2025", "FC Twente", 3, 2, "Fortuna Sittard"),
    ("24 september 2025", "AZ", 2, 2, "PEC Zwolle"),
]

API_URL = "http://127.0.0.1:5000"

for date, home, home_goals, away_goals, away in results:
    # Step 1: Send prediction request
    predict_payload = {
        "home_team": home,
        "away_team": away,
        "user_id": "import_script"
    }
    try:
        r = requests.post(f"{API_URL}/api/predict", json=predict_payload)
        print(f"Predict {home} vs {away}: {r.status_code}")
        time.sleep(0.2)  # Short delay to ensure prediction is stored
    except Exception as e:
        print(f"Prediction error for {home} vs {away}: {e}")
        continue
    # Step 2: Send learn request
    learn_payload = {
        "home_team": home,
        "away_team": away,
        "actual_home_goals": home_goals,
        "actual_away_goals": away_goals
    }
    try:
        r = requests.post(f"{API_URL}/api/learn", json=learn_payload)
        print(f"Learn {home} vs {away}: {r.status_code} - {r.json().get('message', r.text)}")
        time.sleep(0.2)
    except Exception as e:
        print(f"Learn error for {home} vs {away}: {e}")
