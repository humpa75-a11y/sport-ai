"""
🧠 PROFESSOR SMART LEARN - TARGETED VERSION 🧠

**SLIM SYSTEEM:**
1. Laad prediction_history.json
2. Check welke matches afgelopen zijn (>2 uur geleden)
3. Haal ALLEEN DIE SPECIFIEKE uitslagen op
4. Feed naar Learning Manager

GEEN VERSPILDE API CALLS!
"""

import datetime
import json
from pathlib import Path
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# === CONFIG ===
PREDICTION_HISTORY_FILE = Path("data/prediction_history.json")

def load_predictions():
    """📂 Laad voorspellingsgeschiedenis"""
    if not PREDICTION_HISTORY_FILE.exists():
        print(f"⚠️ Geen voorspellingen: {PREDICTION_HISTORY_FILE}")
        return []
    
    with open(PREDICTION_HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_learnable_predictions(predictions):
    """
    🔍 Vind voorspellingen waar we VAN KUNNEN LEREN
    
    Criteria:
    - Voorspelling gedaan >2 uur geleden (match waarschijnlijk afgelopen)
    - Nog niet geleerd (geen 'learned' flag)
    """
    print(f"\n{'='*60}")
    print("🔍 ZOEKEN NAAR LEARNABLE PREDICTIONS")
    print(f"{'='*60}\n")
    
    learnable = []
    now = datetime.datetime.now()
    
    for pred in predictions:
        # Check timestamp
        try:
            pred_time = datetime.datetime.fromisoformat(pred['timestamp'])
            hours_ago = (now - pred_time).total_seconds() / 3600
            
            # Match moet >2 uur geleden voorspeld zijn
            if hours_ago > 2:
                # Check of we al geleerd hebben
                if not pred.get('learned', False):
                    learnable.append(pred)
                    print(f"✅ {pred['home_team']} vs {pred['away_team']}")
                    print(f"   Voorspeld: {hours_ago:.1f} uur geleden")
                    print(f"   Engine: {pred.get('engine', 'Unknown')}\n")
        except Exception as e:
            continue
    
    print(f"{'='*60}")
    print(f"📊 GEVONDEN: {len(learnable)} learnable predictions")
    print(f"{'='*60}\n")
    
    return learnable


def get_match_result_for_prediction(pred):
    """
    🎯 Haal resultaat op voor SPECIFIEKE voorspelling
    
    Gebruikt intelligent search via:
    1. API-Football team search
    2. Fuzzy matching
    """
    try:
        from ultimate_matches_fetcher import UltimateMatchesFetcher
        import requests
        
        fetcher = UltimateMatchesFetcher()
        
        if not fetcher.api_football_key:
            return None
        
        home = pred['home_team']
        away = pred['away_team']
        
        # Probeer laatste 7 dagen
        for day_offset in range(7):
            target_date = (datetime.date.today() - datetime.timedelta(days=day_offset)).strftime("%Y-%m-%d")
            
            try:
                url = "https://v3.football.api-sports.io/fixtures"
                headers = {
                    'x-rapidapi-key': fetcher.api_football_key,
                    'x-rapidapi-host': 'v3.football.api-sports.io'
                }
                params = {
                    'date': target_date,
                    'status': 'FT'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for fixture in data.get('response', []):
                        fixture_home = fixture['teams']['home']['name'].lower()
                        fixture_away = fixture['teams']['away']['name'].lower()
                        
                        # Fuzzy match
                        if (home.lower() in fixture_home or fixture_home in home.lower()) and \
                           (away.lower() in fixture_away or fixture_away in away.lower()):
                            
                            return {
                                'home': fixture['teams']['home']['name'],
                                'away': fixture['teams']['away']['name'],
                                'home_goals': fixture['goals']['home'],
                                'away_goals': fixture['goals']['away'],
                                'league': fixture['league']['name'],
                                'date': target_date
                            }
            except:
                continue
        
        return None
    
    except Exception as e:
        print(f"❌ Error getting result: {e}")
        return None


def learn_from_matches(learnable_predictions):
    """
    🧠 LEER VAN MATCHES
    """
    print(f"\n{'='*60}")
    print("🧠 LEARNING FROM MATCHES")
    print(f"{'='*60}\n")
    
    learned_count = 0
    
    try:
        from learning_manager import LearningManager
        learning_mgr = LearningManager()
        
        for pred in learnable_predictions:
            print(f"🔍 Searching result for: {pred['home_team']} vs {pred['away_team']}...", end=' ')
            
            result = get_match_result_for_prediction(pred)
            
            if result:
                print(f"✅ FOUND!")
                print(f"   Actual: {result['home_goals']}-{result['away_goals']}")
                
                # Extract prediction
                pred_data = pred['prediction']
                if 'expected_home_goals' in pred_data:
                    pred_home = int(pred_data['expected_home_goals'])
                    pred_away = int(pred_data['expected_away_goals'])
                else:
                    pred_home = 1
                    pred_away = 1
                
                # Build structure
                pred_dict = {
                    'top_exact_scores': [
                        {'score': f"{pred_home} - {pred_away}", 'probability': 1.0}
                    ],
                    'confidence_factor': pred_data.get('confidence_factor', 0),
                    'expected_home_goals': pred_home,
                    'expected_away_goals': pred_away
                }
                
                # Log it
                learning_mgr.log_prediction(
                    home_team=result['home'],
                    away_team=result['away'],
                    prediction_result=pred_dict,
                    actual_home_goals=result['home_goals'],
                    actual_away_goals=result['away_goals']
                )
                
                # Mark as learned
                pred['learned'] = True
                learned_count += 1
                
                # Check if exact
                exact = (pred_home == result['home_goals'] and pred_away == result['away_goals'])
                print(f"   {'✅ EXACT!' if exact else '❌ Wrong'}\n")
            else:
                print("⚠️ Not found\n")
        
        # Save updated predictions
        with open(PREDICTION_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(learnable_predictions, f, indent=2)
        
        # Get updated stats
        report = learning_mgr.get_performance_report()
        
        print(f"\n{'='*60}")
        print("📈 LEARNING COMPLETE!")
        print(f"{'='*60}")
        print(f"Matches learned: {learned_count}")
        print(f"Total in memory: {report.get('total_predictions', 0)}")
        print(f"Exact accuracy: {report.get('exact_score_accuracy', 0):.2f}%")
        print(f"Result accuracy: {report.get('result_accuracy', 0):.2f}%")
        print(f"{'='*60}\n")
        
        return learned_count
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """🚀 MAIN"""
    print("\n" + "="*60)
    print("🧠 PROFESSOR SMART LEARN")
    print("   TARGETED LEARNING - Geen verspilde API calls!")
    print("="*60 + "\n")
    
    # 1. Load predictions
    predictions = load_predictions()
    if not predictions:
        print("⚠️ Geen voorspellingen om van te leren")
        return
    
    print(f"📂 Loaded {len(predictions)} predictions\n")
    
    # 2. Find learnable ones
    learnable = find_learnable_predictions(predictions)
    if not learnable:
        print("⚠️ Geen learnable predictions (alles te recent of al geleerd)")
        return
    
    # 3. Learn!
    learned = learn_from_matches(learnable)
    
    if learned > 0:
        print("✅ SUCCESS! PROFESSOR is slimmer geworden! 🎓")
    else:
        print("⚠️ Geen matches gevonden om van te leren")


if __name__ == "__main__":
    main()
