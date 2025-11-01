"""
🧠 PROFESSOR RESULT CHECKER - ULTIMATE VERSION 🧠
Versie: V3.0 ULTIMATE — 2025-10-16

**GEBRUIKT JE BESTAANDE API KEYS VIA ULTIMATE_MATCHES_FETCHER!**

Evolutie voor PROFESSOR:
    ✅ Live uitslagen via ULTIMATE_MATCHES_FETCHER (API-Football + The Odds API)
    ✅ Automatische matching met prediction_history
    ✅ Learning Manager integration
    ✅ Daily accuracy tracking
    ✅ ALLEEN ECHTE DATA - gebruikt je bestaande API infrastructure!
"""

import datetime
import json
import requests
from pathlib import Path
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# === CONFIGURATIE ===
PREDICTION_HISTORY_FILE = Path("data/prediction_history.json")
DATE_TODAY = datetime.date.today().strftime("%Y-%m-%d")

# === CORE FUNCTIONS ===

def get_today_results():
    """
    🔍 Haal vandaag gespeelde wedstrijden op via ULTIMATE_MATCHES_FETCHER
    GEBRUIKT JE BESTAANDE API KEYS!
    
    Returns:
        list: [{home, away, home_goals, away_goals, league, status, date}]
    """
    print(f"\n{'='*60}")
    print(f"🔍 OPHALEN LIVE UITSLAGEN VOOR {DATE_TODAY}")
    print(f"   Via ULTIMATE_MATCHES_FETCHER (je eigen API keys!)")
    print(f"{'='*60}")
    
    try:
        from ultimate_matches_fetcher import UltimateMatchesFetcher
        
        # Gebruik de ULTIMATE fetcher die JE AL HEBT!
        fetcher = UltimateMatchesFetcher()
        
        # Check API keys status
        has_api_football = bool(fetcher.api_football_key)
        has_odds_api = bool(fetcher.odds_api_key)
        
        print(f"� API Keys Status:")
        print(f"   API-Football: {'✅ ACTIEF' if has_api_football else '❌ NIET GEVONDEN'}")
        print(f"   The Odds API: {'✅ ACTIEF' if has_odds_api else '❌ NIET GEVONDEN'}")
        
        if not has_api_football and not has_odds_api:
            print("\n⚠️ GEEN API KEYS GEVONDEN!")
            print("🔧 SETUP in PowerShell:")
            print("   $env:API_FOOTBALL_KEY = 'your_key'")
            print("   $env:ODDS_API_KEY = 'your_key'")
            return []
        
        # Haal LIVE matches op
        print(f"\n📡 Fetching via ULTIMATE infrastructure...")
        all_matches_raw = fetcher.get_todays_matches()
        
        if not all_matches_raw:
            print("⚠️ Geen matches gevonden voor vandaag")
            return []
        
        # Filter ALLEEN AFGELOPEN wedstrijden (FT status)
        finished_matches = []
        now = datetime.datetime.utcnow()
        
        for match in all_matches_raw:
            try:
                # Parse kickoff time
                kickoff_str = match.get('commence_time', '')
                if isinstance(kickoff_str, str):
                    try:
                        kickoff = datetime.datetime.fromisoformat(kickoff_str.replace('Z', '+00:00'))
                        kickoff = kickoff.replace(tzinfo=None)
                    except:
                        continue
                    
                    # Match is FINISHED if kickoff was >2 hours ago
                    time_diff = (now - kickoff).total_seconds() / 3600  # hours
                    
                    if time_diff > 2:  # Match finished
                        # Try to get ACTUAL result via API-Football
                        if has_api_football:
                            result = _get_match_result_api_football(
                                match['home_team'], 
                                match['away_team'],
                                fetcher.api_football_key
                            )
                            if result:
                                finished_matches.append(result)
            except Exception as e:
                continue
        
        if finished_matches:
            print(f"\n{'='*60}")
            print(f"📊 TOTAAL: {len(finished_matches)} afgelopen wedstrijden")
            print(f"{'='*60}")
            for m in finished_matches:
                print(f"   • {m['home']} {m['home_goals']}-{m['away_goals']} {m['away']} ({m['league']})")
        else:
            print("\n⚠️ Geen afgelopen wedstrijden vandaag")
            print("   (Wedstrijden moeten >2 uur geleden zijn)")
        
        return finished_matches
    
    except ImportError:
        print("❌ ultimate_matches_fetcher.py niet gevonden!")
        print("   Zorg dat het bestand in backend/ staat")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def _get_match_result_api_football(home_team, away_team, api_key):
    """
    Haal exact resultaat op voor een specifieke wedstrijd via API-Football
    """
    try:
        # Search by team names
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        params = {
            'date': DATE_TODAY,
            'status': 'FT'  # Full Time
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            for fixture in data.get('response', []):
                fixture_home = fixture['teams']['home']['name']
                fixture_away = fixture['teams']['away']['name']
                
                # Fuzzy match team names
                if (home_team.lower() in fixture_home.lower() or fixture_home.lower() in home_team.lower()) and \
                   (away_team.lower() in fixture_away.lower() or fixture_away.lower() in away_team.lower()):
                    
                    return {
                        'home': fixture_home,
                        'away': fixture_away,
                        'home_goals': fixture['goals']['home'],
                        'away_goals': fixture['goals']['away'],
                        'league': fixture['league']['name'],
                        'status': 'FT',
                        'date': DATE_TODAY
                    }
    except Exception as e:
        pass
    
    return None


def load_predictions():
    """
    📂 Laad PROFESSOR's voorspellingsgeschiedenis
    
    Returns:
        list: Alle voorspellingen uit prediction_history.json
    """
    if not PREDICTION_HISTORY_FILE.exists():
        print(f"⚠️ Geen voorspellingsgeschiedenis: {PREDICTION_HISTORY_FILE}")
        return []
    
    try:
        with open(PREDICTION_HISTORY_FILE, "r", encoding="utf-8") as f:
            predictions = json.load(f)
        print(f"📂 {len(predictions)} voorspellingen geladen")
        return predictions
    except Exception as e:
        print(f"❌ Fout bij laden: {e}")
        return []


def compare_predictions(results, predictions):
    """
    🔍 Vergelijk uitslagen met PROFESSOR's voorspellingen
    
    Returns:
        dict: Performance metrics
    """
    print(f"\n{'='*60}")
    print("🔍 VERGELIJKEN VOORSPELLINGEN MET UITSLAGEN")
    print(f"{'='*60}\n")
    
    matched = []
    
    for result in results:
        for pred in predictions:
            pred_home = pred.get('home_team', '').strip().lower()
            pred_away = pred.get('away_team', '').strip().lower()
            result_home = result['home'].strip().lower()
            result_away = result['away'].strip().lower()
            
            # Match teams
            if pred_home == result_home and pred_away == result_away:
                pred_data = pred.get('prediction', {})
                
                # Handle both old (V1) and new (PROFESSOR) prediction formats
                if 'top_exact_scores' in pred_data:
                    # V1 format
                    top_pred = pred_data['top_exact_scores'][0]['score']
                    pred_home_goals, pred_away_goals = map(int, top_pred.split(' - '))
                else:
                    # PROFESSOR format
                    pred_home_goals = pred_data.get('expected_home_goals', 0)
                    pred_away_goals = pred_data.get('expected_away_goals', 0)
                
                # Check exact score
                exact_match = (pred_home_goals == result['home_goals'] and 
                              pred_away_goals == result['away_goals'])
                
                # Check result (W/D/L)
                pred_result = 'D'
                if pred_home_goals > pred_away_goals:
                    pred_result = 'H'
                elif pred_home_goals < pred_away_goals:
                    pred_result = 'A'
                
                actual_result = 'D'
                if result['home_goals'] > result['away_goals']:
                    actual_result = 'H'
                elif result['home_goals'] < result['away_goals']:
                    actual_result = 'A'
                
                result_match = (pred_result == actual_result)
                
                matched.append({
                    'home': result['home'],
                    'away': result['away'],
                    'predicted': f"{pred_home_goals}-{pred_away_goals}",
                    'actual': f"{result['home_goals']}-{result['away_goals']}",
                    'exact_correct': exact_match,
                    'result_correct': result_match,
                    'confidence': pred_data.get('confidence_factor', 0),
                    'league': result['league'],
                    'timestamp': pred.get('timestamp', 'Unknown')
                })
                
                # Print result
                status = "✅ EXACT!" if exact_match else ("✓ Result" if result_match else "❌ Wrong")
                print(f"{status} | {result['home']} vs {result['away']}")
                print(f"         Voorspeld: {pred_home_goals}-{pred_away_goals} | Werkelijk: {result['home_goals']}-{result['away_goals']}")
                print(f"         Confidence: {pred_data.get('confidence_factor', 0):.1f}% | {result['league']}\n")
                
                break
    
    # Statistics
    total = len(matched)
    if total == 0:
        print("⚠️ Geen matching voorspellingen gevonden")
        return {
            'total_checked': 0,
            'exact_correct': 0,
            'result_correct': 0,
            'exact_accuracy': 0.0,
            'result_accuracy': 0.0,
            'matches': []
        }
    
    exact_correct = sum(1 for m in matched if m['exact_correct'])
    result_correct = sum(1 for m in matched if m['result_correct'])
    
    exact_acc = (exact_correct / total) * 100
    result_acc = (result_correct / total) * 100
    
    print(f"\n{'='*60}")
    print("📊 DAGELIJKSE PERFORMANCE")
    print(f"{'='*60}")
    print(f"Wedstrijden gecheckt: {total}")
    print(f"Exact score correct:  {exact_correct}/{total} ({exact_acc:.1f}%)")
    print(f"Result correct (W/D/L): {result_correct}/{total} ({result_acc:.1f}%)")
    print(f"{'='*60}\n")
    
    return {
        'total_checked': total,
        'exact_correct': exact_correct,
        'result_correct': result_correct,
        'exact_accuracy': exact_acc,
        'result_accuracy': result_acc,
        'matches': matched,
        'date': DATE_TODAY
    }


def feed_to_learning_manager(comparison_results):
    """
    🧠 FEED RESULTS TO PROFESSOR's LEARNING MANAGER
    """
    print(f"\n{'='*60}")
    print("🧠 FEEDING TO LEARNING MANAGER")
    print(f"{'='*60}\n")
    
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from learning_manager import LearningManager
        
        learning_mgr = LearningManager()
        
        for match in comparison_results['matches']:
            pred_score = match['predicted'].split('-')
            actual_score = match['actual'].split('-')
            
            pred_home = int(pred_score[0])
            pred_away = int(pred_score[1])
            
            # Build prediction structure
            pred_dict = {
                'top_exact_scores': [
                    {'score': f"{pred_home} - {pred_away}", 'probability': 1.0}
                ],
                'confidence_factor': match.get('confidence', 0),
                'expected_home_goals': pred_home,
                'expected_away_goals': pred_away
            }
            
            # Log to learning manager
            learning_mgr.log_prediction(
                home_team=match['home'],
                away_team=match['away'],
                prediction_result=pred_dict,
                actual_home_goals=int(actual_score[0]),
                actual_away_goals=int(actual_score[1])
            )
            
            print(f"✅ Logged: {match['home']} vs {match['away']}")
        
        # Performance report
        report = learning_mgr.get_performance_report()
        print(f"\n📈 UPDATED LEARNING STATS:")
        print(f"   Total learned: {report.get('total_predictions', 0)}")
        print(f"   Current exact accuracy: {report.get('exact_score_accuracy', 0):.2f}%")
        print(f"   Current result accuracy: {report.get('result_accuracy', 0):.2f}%")
        
        return True
    
    except ImportError:
        print("⚠️ LearningManager niet gevonden (standalone mode)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def save_daily_report(comparison_results):
    """💾 Save daily report"""
    report_dir = Path("data/daily_reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"report_{DATE_TODAY}.json"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_results, f, indent=2, ensure_ascii=False)
        print(f"💾 Report saved: {report_file}")
    except Exception as e:
        print(f"⚠️ Could not save: {e}")


# === MAIN ===

def main():
    """🚀 HOOFDFUNCTIE - Automated Daily Result Checking"""
    print("\n" + "="*60)
    print("🧠 PROFESSOR RESULT CHECKER - ULTIMATE VERSION")
    print("   GEBRUIKT JE BESTAANDE API INFRASTRUCTURE!")
    print("="*60 + "\n")
    
    # 1. Haal LIVE uitslagen op via ULTIMATE FETCHER
    results = get_today_results()
    
    if not results:
        print("⚠️ Geen uitslagen vandaag. Check:")
        print("   - Is je API key correct?")
        print("   - Zijn er wedstrijden afgelopen vandaag?")
        return
    
    # 2. Laad voorspellingen
    predictions = load_predictions()
    
    if not predictions:
        print("⚠️ Geen voorspellingen gevonden")
        return
    
    # 3. Vergelijk
    comparison = compare_predictions(results, predictions)
    
    if comparison['total_checked'] == 0:
        print("⚠️ Geen matches om te vergelijken")
        return
    
    # 4. Feed to Learning Manager
    feed_to_learning_manager(comparison)
    
    # 5. Save report
    save_daily_report(comparison)
    
    print("\n" + "="*60)
    print("✅ RESULT CHECKER COMPLETED")
    print("🎓 PROFESSOR HEEFT GELEERD VAN ECHTE DATA!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
