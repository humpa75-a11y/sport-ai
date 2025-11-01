import requests
import time

def send_to_ai(match_data):
    url_predict = "http://127.0.0.1:5000/api/predict"
    url_learn = "http://127.0.0.1:5000/api/learn"
    for match in match_data:
        print(f"Sending: {match['home_team']} vs {match['away_team']} ({match['home_goals']}-{match['away_goals']})")
        # 1. Predict
        predict_payload = {
            "home_team": match["home_team"],
            "away_team": match["away_team"]
        }
        try:
            r = requests.post(url_predict, json=predict_payload)
            print("Predict response:", r.status_code, r.text)
        except Exception as e:
            print("Predict error:", e)
        time.sleep(0.5)
        # 2. Learn
        learn_payload = {
            "home_team": match["home_team"],
            "away_team": match["away_team"],
            "actual_home_goals": match["home_goals"],
            "actual_away_goals": match["away_goals"]
        }
        try:
            r = requests.post(url_learn, json=learn_payload)
            print("Learn response:", r.status_code, r.text)
        except Exception as e:
            print("Learn error:", e)
        time.sleep(0.5)

# Paste your match data here
match_data = [
    {"home_team": "NAC Breda", "away_team": "PEC Zwolle", "home_goals": 2, "away_goals": 2},
    {"home_team": "Ajax", "away_team": "AZ", "home_goals": 0, "away_goals": 2},
    {"home_team": "FC Utrecht", "away_team": "FC Volendam", "home_goals": 3, "away_goals": 1},
    {"home_team": "PSV", "away_team": "Go Ahead Eagles", "home_goals": 2, "away_goals": 1},
    {"home_team": "N.E.C.", "away_team": "FC Twente", "home_goals": 3, "away_goals": 3},
    {"home_team": "Go Ahead Eagles", "away_team": "N.E.C.", "home_goals": 1, "away_goals": 1},
    {"home_team": "AZ", "away_team": "Telstar", "home_goals": 2, "away_goals": 1},
    {"home_team": "Feyenoord", "away_team": "FC Utrecht", "home_goals": 3, "away_goals": 2},
    {"home_team": "FC Twente", "away_team": "Heracles Almelo", "home_goals": 2, "away_goals": 1},
    {"home_team": "sc Heerenveen", "away_team": "Excelsior", "home_goals": 2, "away_goals": 1},
    {"home_team": "PEC Zwolle", "away_team": "PSV", "home_goals": 0, "away_goals": 4},
    {"home_team": "Fortuna Sittard", "away_team": "FC Volendam", "home_goals": 1, "away_goals": 0},
    {"home_team": "Sparta Rotterdam", "away_team": "Ajax", "home_goals": 3, "away_goals": 3},
    {"home_team": "NAC Breda", "away_team": "FC Groningen", "home_goals": 1, "away_goals": 2},
    {"home_team": "Telstar", "away_team": "Go Ahead Eagles", "home_goals": 4, "away_goals": 2},
    {"home_team": "FC Utrecht", "away_team": "sc Heerenveen", "home_goals": 2, "away_goals": 2},
    {"home_team": "FC Groningen", "away_team": "Feyenoord", "home_goals": 0, "away_goals": 1},
    {"home_team": "N.E.C.", "away_team": "AZ", "home_goals": 2, "away_goals": 1},
    {"home_team": "Heracles Almelo", "away_team": "Sparta Rotterdam", "home_goals": 3, "away_goals": 0},
    {"home_team": "Excelsior", "away_team": "PSV", "home_goals": 1, "away_goals": 2},
    {"home_team": "FC Volendam", "away_team": "PEC Zwolle", "home_goals": 2, "away_goals": 1},
    {"home_team": "Ajax", "away_team": "NAC Breda", "home_goals": 2, "away_goals": 1},
    {"home_team": "FC Twente", "away_team": "Fortuna Sittard", "home_goals": 3, "away_goals": 2},
    {"home_team": "AZ", "away_team": "PEC Zwolle", "home_goals": 2, "away_goals": 2}
]

send_to_ai(match_data)
