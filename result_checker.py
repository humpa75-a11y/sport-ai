"""
🧠 PROFESSOR RESULT CHECKER - AUTOMATED LEARNING ENGINE 🧠
Versie: V2.0 — 2025-10-16
Gebaseerd op: FD-Daily Result Checker V1.0

Evolutie voor PROFESSOR:
    ✅ Automatisch uitslagen ophalen (Apify Sports API)
    ✅ Vergelijk met prediction_history.json
    ✅ Feed naar learning_manager (automatisch leren)
    ✅ Daily accuracy tracking
    ✅ Performance reports per league
"""

import datetime
import json
import requests
from pathlib import Path
import os

# === CONFIGURATIE ===
PREDICTION_HISTORY_FILE = Path("data/prediction_history.json")
APIFY_API_KEY = os.getenv("APIFY_API_KEY", "")  # Zet in environment variable
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"  # Demo mode voor testing
REGION_KEYWORDS = [
    "Eredivisie", "Netherlands", "Europe", 
    "Premier League", "La Liga", "Serie A", 
    "Bundesliga", "Ligue 1", "Primeira Liga",
    "Super Lig", "Eerste Divisie"
]
DATE_TODAY = datetime.date.today().strftime("%Y-%m-%d")

# === CORE FUNCTIONS ===

def get_today_results():
    """
    🔍 Haal vandaag gespeelde wedstrijden op via Apify Sports Live Scores
    
    Returns:
        list: [{home, away, home_goals, away_goals, league, status, date}]
    """
    print(f"\n{'='*60}")
    print(f"🔍 OPHALEN UITSLAGEN VOOR {DATE_TODAY}")
    print(f"{'='*60}")
    
    # DEMO MODE: Gebruik dummy data voor testing
    if DEMO_MODE:
        print("🎭 DEMO MODE ACTIEF - Gebruik dummy data")
        dummy_results = [
            {
                "home": "FC Eindhoven",
                "away": "Helmond Sport",
                "home_goals": 2,
                "away_goals": 1,
                "league": "Eerste Divisie",
                "status": "FT",
                "date": DATE_TODAY
            },
            {
                "home": "ADO Den Haag",
                "away": "FC Volendam",
                "home_goals": 1,
                "away_goals": 1,
                "league": "Eerste Divisie",
                "status": "FT",
                "date": DATE_TODAY
            },
            {
                "home": "De Graafschap",
                "away": "Roda JC",
                "home_goals": 3,
                "away_goals": 0,
                "league": "Eerste Divisie",
                "status": "FT",
                "date": DATE_TODAY
            }
        ]
        print(f"✅ {len(dummy_results)} dummy wedstrijden gegenereerd")
        for m in dummy_results:
            print(f"   • {m['home']} {m['home_goals']}-{m['away_goals']} {m['away']} ({m['league']})")
        return dummy_results
    
    if not APIFY_API_KEY:
        print("⚠️ APIFY_API_KEY niet gevonden in environment variables")
        print("   Gebruik: $env:APIFY_API_KEY='your_key' (PowerShell)")
        print("   Of: set DEMO_MODE=true voor demo mode")
        return []
    
    api_url = f"https://api.apify.com/v2/acts/apify~sports-live-scores/runs/last/dataset/items?token={APIFY_API_KEY}"
    
    try:
        print("📡 API Request naar Apify Sports Live Scores...")
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        matches = []
        for item in data:
            league = item.get("league_name", "")
            status = item.get("status", "")
            
            # Filter: Alleen afgelopen wedstrijden (FT = Full Time) van vandaag
            if status == "FT" and any(kw.lower() in league.lower() for kw in REGION_KEYWORDS):
                score = item.get("score", "0-0")
                try:
                    home_goals, away_goals = map(int, score.split("-"))
                except:
                    continue  # Skip als score niet parseable is
                
                matches.append({
                    "home": item.get("home_team", "").strip(),
                    "away": item.get("away_team", "").strip(),
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "league": league,
                    "status": status,
                    "date": item.get("date", DATE_TODAY)
                })
        
        print(f"✅ {len(matches)} afgelopen wedstrijden gevonden")
        for m in matches:
            print(f"   • {m['home']} {m['home_goals']}-{m['away_goals']} {m['away']} ({m['league']})")
        
        return matches
    
    except requests.exceptions.RequestException as e:
        print(f"❌ API Request gefaald: {e}")
        return []
    except Exception as e:
        print(f"❌ Fout bij verwerken data: {e}")
        return []


def load_predictions():
    """
    📂 Laad PROFESSOR's voorspellingsgeschiedenis
    
    Returns:
        list: Alle voorspellingen uit prediction_history.json
    """
    if not PREDICTION_HISTORY_FILE.exists():
        print(f"⚠️ Geen voorspellingsgeschiedenis gevonden: {PREDICTION_HISTORY_FILE}")
        return []
    
    try:
        with open(PREDICTION_HISTORY_FILE, "r", encoding="utf-8") as f:
            predictions = json.load(f)
        print(f"📂 {len(predictions)} voorspellingen geladen uit geschiedenis")
        return predictions
    except Exception as e:
        print(f"❌ Fout bij laden voorspellingen: {e}")
        return []


def compare_predictions(results, predictions):
    """
    🔍 Vergelijk uitslagen met PROFESSOR's voorspellingen
    
    Args:
        results: Lijst met wedstrijduitslagen van vandaag
        predictions: PROFESSOR's prediction_history
    
    Returns:
        dict: {
            'total_checked': int,
            'exact_correct': int,
            'result_correct': int,
            'exact_accuracy': float,
            'result_accuracy': float,
            'matches': [...]
        }
    """
    print(f"\n{'='*60}")
    print("🔍 VERGELIJKEN VOORSPELLINGEN MET UITSLAGEN")
    print(f"{'='*60}\n")
    
    matched = []
    
    for result in results:
        # Zoek matching voorspelling
        for pred in predictions:
            pred_home = pred.get('home_team', '').strip().lower()
            pred_away = pred.get('away_team', '').strip().lower()
            result_home = result['home'].strip().lower()
            result_away = result['away'].strip().lower()
            
            # Match teams (case-insensitive, strip whitespace)
            if pred_home == result_home and pred_away == result_away:
                pred_data = pred.get('prediction', {})
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
                
                # Print match result
                status = "✅ EXACT!" if exact_match else ("✓ Result" if result_match else "❌ Wrong")
                print(f"{status} | {result['home']} vs {result['away']}")
                print(f"         Voorspeld: {pred_home_goals}-{pred_away_goals} | Werkelijk: {result['home_goals']}-{result['away_goals']}")
                print(f"         Confidence: {pred_data.get('confidence_factor', 0):.1f}% | League: {result['league']}\n")
                
                break  # Stop na eerste match
    
    # Calculate statistics
    total = len(matched)
    if total == 0:
        print("⚠️ Geen matching voorspellingen gevonden voor vandaag")
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
    print("📊 DAGELIJKSE PERFORMANCE SAMENVATTING")
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
    
    Integreert met backend/learning_manager.py voor automated learning
    """
    print(f"\n{'='*60}")
    print("🧠 FEEDING RESULTS TO LEARNING MANAGER")
    print(f"{'='*60}\n")
    
    # Try to import learning manager
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from learning_manager import LearningManager
        
        learning_mgr = LearningManager()
        
        for match in comparison_results['matches']:
            # Extract data
            pred_score = match['predicted'].split('-')
            actual_score = match['actual'].split('-')
            
            # Convert to int (handle floats from old predictions)
            pred_home = int(float(pred_score[0]))
            pred_away = int(float(pred_score[1]))
            
            # Build prediction structure that Learning Manager expects
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
            
            print(f"✅ Logged: {match['home']} vs {match['away']} → Learning Manager")
        
        # Get updated performance report
        report = learning_mgr.get_performance_report()
        print(f"\n📈 UPDATED LEARNING STATS:")
        print(f"   Total learned predictions: {report.get('total_predictions', 0)}")
        print(f"   Current exact accuracy: {report.get('exact_score_accuracy', 0):.2f}%")
        print(f"   Current result accuracy: {report.get('result_accuracy', 0):.2f}%")
        
        return True
    
    except ImportError:
        print("⚠️ LearningManager niet gevonden - kan niet automatisch leren")
        print("   (Dit is normaal als je dit script standalone draait)")
        return False
    except Exception as e:
        print(f"❌ Fout bij feeding naar Learning Manager: {e}")
        return False


def save_daily_report(comparison_results):
    """
    💾 Sla dagelijks rapport op voor historische tracking
    """
    report_dir = Path("data/daily_reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"report_{DATE_TODAY}.json"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_results, f, indent=2, ensure_ascii=False)
        print(f"💾 Daily report saved: {report_file}")
    except Exception as e:
        print(f"⚠️ Kon rapport niet opslaan: {e}")


# === MAIN EXECUTION ===

def main():
    """
    🚀 HOOFDFUNCTIE - Automated Daily Result Checking & Learning
    """
    print("\n" + "="*60)
    print("🧠 PROFESSOR RESULT CHECKER - AUTOMATED LEARNING")
    print("="*60 + "\n")
    
    # 1. Haal vandaag's uitslagen op
    results = get_today_results()
    
    if not results:
        print("❌ Geen uitslagen gevonden voor vandaag. Stoppen.")
        return
    
    # 2. Laad voorspellingen
    predictions = load_predictions()
    
    if not predictions:
        print("❌ Geen voorspellingen gevonden. Stoppen.")
        return
    
    # 3. Vergelijk
    comparison = compare_predictions(results, predictions)
    
    if comparison['total_checked'] == 0:
        print("⚠️ Geen matches om te vergelijken")
        return
    
    # 4. Feed naar Learning Manager (automated learning!)
    feed_to_learning_manager(comparison)
    
    # 5. Save daily report
    save_daily_report(comparison)
    
    print("\n" + "="*60)
    print("✅ RESULT CHECKER COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
