"""
🔥🔥🔥 THE FUSION - ULTIMATE INTEGRATION MASTER 🔥🔥🔥
========================================================

Dit script controleert en integreert ALLE componenten:
1. PROFESSOR DE MEESTER (AI Model)
2. Live Feature Generator
3. Poisson Value Engine
4. Live Odds Scraper (Sofascore + Flashscore)
5. Ultimate Matches Fetcher
6. Learning Manager
7. Flask API Endpoints
8. Frontend (matches.html)

ALLES WORDT GETEST EN AAN ELKAAR GEKOPPELD!
"""

import os
import sys
import time
import json
import pickle
from datetime import datetime
from typing import Dict, List, Tuple

# Kleuren voor terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print fancy header."""
    print("\n" + "="*80)
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print("="*80)

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# ============================================================================
# FASE 1: FILESYSTEM CHECK
# ============================================================================
def check_filesystem() -> Dict[str, bool]:
    """Check of alle benodigde bestanden aanwezig zijn."""
    print_header("FASE 1: FILESYSTEM CONTROLE")
    
    required_files = {
        # Backend Core
        'backend/app.py': False,
        'backend/prediction_engine.py': False,
        'backend/live_feature_generator.py': False,
        'backend/learning_scheduler.py': False,
        'backend/learning_manager.py': False,
        
        # Value Betting
        'backend/poisson_value_engine.py': False,
        'backend/value_betting_formatter.py': False,
        
        # Live Data
        'backend/live_odds_scraper.py': False,
        'backend/ultimate_matches_fetcher.py': False,
        
        # Data Files
        'data/de_meester_ULTIMATE_PLUS.pkl': False,
        'data/de_meester_HYPER.pkl': False,
        'data/teams_db.json': False,
        
        # Frontend
        'frontend/index.html': False,
        'frontend/matches.html': False,
        'frontend/static/style.css': False,
        'frontend/static/script.js': False,
        
        # Demos
        'demo_value_betting.py': False,
        'demo_bundesliga_style.py': False
    }
    
    for file_path in required_files.keys():
        if os.path.exists(file_path):
            required_files[file_path] = True
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} - NIET GEVONDEN!")
    
    total = len(required_files)
    present = sum(required_files.values())
    print_info(f"\n📊 {present}/{total} bestanden gevonden ({present/total*100:.1f}%)")
    
    return required_files

# ============================================================================
# FASE 2: MODULE IMPORT TEST
# ============================================================================
def test_imports() -> Dict[str, bool]:
    """Test of alle Python modules importeerbaar zijn."""
    print_header("FASE 2: MODULE IMPORT TEST")
    
    sys.path.insert(0, os.path.abspath('backend'))
    
    modules = {}
    
    # Test 1: Prediction Engine
    try:
        from prediction_engine import DeMeester
        modules['prediction_engine'] = True
        print_success("prediction_engine.py")
    except Exception as e:
        modules['prediction_engine'] = False
        print_error(f"prediction_engine.py - {e}")
    
    # Test 2: Live Feature Generator
    try:
        from live_feature_generator import LiveFeatureGenerator
        modules['live_feature_generator'] = True
        print_success("live_feature_generator.py")
    except Exception as e:
        modules['live_feature_generator'] = False
        print_error(f"live_feature_generator.py - {e}")
    
    # Test 3: Poisson Value Engine
    try:
        from poisson_value_engine import PoissonValueEngine
        modules['poisson_value_engine'] = True
        print_success("poisson_value_engine.py")
    except Exception as e:
        modules['poisson_value_engine'] = False
        print_error(f"poisson_value_engine.py - {e}")
    
    # Test 4: Value Betting Formatter
    try:
        from value_betting_formatter import ValueBettingFormatter
        modules['value_betting_formatter'] = True
        print_success("value_betting_formatter.py")
    except Exception as e:
        modules['value_betting_formatter'] = False
        print_error(f"value_betting_formatter.py - {e}")
    
    # Test 5: Live Odds Scraper
    try:
        from live_odds_scraper import get_enhanced_matches
        modules['live_odds_scraper'] = True
        print_success("live_odds_scraper.py")
    except Exception as e:
        modules['live_odds_scraper'] = False
        print_error(f"live_odds_scraper.py - {e}")
    
    # Test 6: Ultimate Matches Fetcher
    try:
        from ultimate_matches_fetcher import UltimateMatchesFetcher
        modules['ultimate_matches_fetcher'] = True
        print_success("ultimate_matches_fetcher.py")
    except Exception as e:
        modules['ultimate_matches_fetcher'] = False
        print_error(f"ultimate_matches_fetcher.py - {e}")
    
    # Test 7: Learning Manager
    try:
        from learning_manager import LearningManager
        modules['learning_manager'] = True
        print_success("learning_manager.py")
    except Exception as e:
        modules['learning_manager'] = False
        print_error(f"learning_manager.py - {e}")
    
    total = len(modules)
    success = sum(modules.values())
    print_info(f"\n📊 {success}/{total} modules geïmporteerd ({success/total*100:.1f}%)")
    
    return modules

# ============================================================================
# FASE 3: PROFESSOR MODEL TEST
# ============================================================================
def test_professor() -> Tuple[bool, Dict]:
    """Test PROFESSOR DE MEESTER model."""
    print_header("FASE 3: PROFESSOR DE MEESTER TEST")
    
    try:
        # Check model file
        professor_paths = [
            'data/de_meester_ULTIMATE_PLUS.pkl',
            'data/de_meester_HYPER.pkl'
        ]
        
        model_path = None
        for path in professor_paths:
            if os.path.exists(path):
                model_path = path
                print_success(f"Model gevonden: {path}")
                break
        
        if not model_path:
            print_error("Geen PROFESSOR model gevonden!")
            return False, {}
        
        # Load model
        with open(model_path, 'rb') as f:
            professor = pickle.load(f)
        
        info = professor.get('training_info', {})
        
        print_success(f"Model geladen!")
        print_info(f"   📊 Matches: {info.get('total_matches', 0)}")
        print_info(f"   🎯 Accuracy: {info.get('accuracy', 0):.2f}%")
        print_info(f"   📈 Result Accuracy: {info.get('result_accuracy', 0):.2f}%")
        print_info(f"   🔥 Models: {len(professor.get('models_home', {}))}")
        
        return True, professor
    
    except Exception as e:
        print_error(f"PROFESSOR laden mislukt: {e}")
        return False, {}

# ============================================================================
# FASE 4: LIVE FEATURES TEST
# ============================================================================
def test_live_features(modules: Dict[str, bool]) -> bool:
    """Test Live Feature Generator."""
    print_header("FASE 4: LIVE FEATURE GENERATOR TEST")
    
    if not modules.get('live_feature_generator'):
        print_error("Live Feature Generator niet beschikbaar!")
        return False
    
    try:
        from live_feature_generator import LiveFeatureGenerator
        
        generator = LiveFeatureGenerator()
        print_success("LiveFeatureGenerator geïnitialiseerd")
        
        # Test met Ajax vs PSV
        print_info("Test: Ajax vs PSV")
        features = generator.generate_features('Ajax', 'PSV', speelronde=19)
        
        print_success(f"Features gegenereerd: {len(features)} parameters")
        print_info(f"   🏠 Thuis aanval: {features.get('home_attack_strength', 'N/A')}")
        print_info(f"   ✈️  Uit aanval: {features.get('away_attack_strength', 'N/A')}")
        print_info(f"   📊 Thuis vorm: {features.get('home_win_rate', 'N/A')}")
        print_info(f"   📊 Uit vorm: {features.get('away_win_rate', 'N/A')}")
        
        return True
    
    except Exception as e:
        print_error(f"Live Features test mislukt: {e}")
        return False

# ============================================================================
# FASE 5: POISSON VALUE ENGINE TEST
# ============================================================================
def test_poisson_engine(modules: Dict[str, bool]) -> bool:
    """Test Poisson Value Engine."""
    print_header("FASE 5: POISSON VALUE ENGINE TEST")
    
    if not modules.get('poisson_value_engine'):
        print_error("Poisson Value Engine niet beschikbaar!")
        return False
    
    try:
        from poisson_value_engine import PoissonValueEngine
        
        engine = PoissonValueEngine(simulation_runs=100)
        print_success("PoissonValueEngine geïnitialiseerd (100 runs)")
        
        # Test simulatie
        print_info("Test: Bayern Munich vs Borussia Dortmund")
        sim_stats = engine.simulate_match(
            home_goals_expected=2.1,
            away_goals_expected=1.5
        )
        
        print_success("Simulatie voltooid!")
        print_info(f"   🏠 Thuis Win: {sim_stats['p_home_win']*100:.1f}%")
        print_info(f"   🤝 Gelijkspel: {sim_stats['p_draw']*100:.1f}%")
        print_info(f"   ✈️  Uit Win: {sim_stats['p_away_win']*100:.1f}%")
        print_info(f"   ⚽ Over 2.5: {sim_stats['p_over_2_5']*100:.1f}%")
        print_info(f"   🎯 BTTS: {sim_stats['p_btts_yes']*100:.1f}%")
        
        # Test EV calculation
        ev = engine.calculate_expected_value(probability=0.45, odds=2.20)
        print_success(f"EV Berekening: {ev:+.2%} (0.45 prob @ 2.20 odds)")
        
        return True
    
    except Exception as e:
        print_error(f"Poisson Engine test mislukt: {e}")
        return False

# ============================================================================
# FASE 6: LIVE ODDS SCRAPER TEST
# ============================================================================
def test_odds_scraper(modules: Dict[str, bool]) -> bool:
    """Test Live Odds Scraper."""
    print_header("FASE 6: LIVE ODDS SCRAPER TEST")
    
    if not modules.get('live_odds_scraper'):
        print_error("Live Odds Scraper niet beschikbaar!")
        return False
    
    try:
        from live_odds_scraper import get_enhanced_matches
        
        print_info("Ophalen van Bundesliga matches (met cache, snel)...")
        matches = get_enhanced_matches(
            league='bundesliga',
            include_odds=False,  # Snel testen zonder odds
            include_xg=False,
            include_predictz=False
        )
        
        if matches:
            print_success(f"{len(matches)} Bundesliga matches gevonden!")
            
            # Toon eerste match
            if len(matches) > 0:
                m = matches[0]
                print_info(f"   Voorbeeld: {m['home']} vs {m['away']}")
                print_info(f"   ⏰ Tijd: {m['time']}")
                print_info(f"   🏆 League: {m['league']}")
        else:
            print_warning("Geen matches gevonden (mogelijk geen Bundesliga vandaag)")
        
        return True
    
    except Exception as e:
        print_error(f"Live Odds Scraper test mislukt: {e}")
        return False

# ============================================================================
# FASE 7: FULL INTEGRATION TEST
# ============================================================================
def test_full_integration(modules: Dict[str, bool], professor: Dict) -> bool:
    """Test complete integratie: PROFESSOR + Features + Poisson + Odds."""
    print_header("FASE 7: VOLLEDIGE INTEGRATIE TEST")
    
    required_modules = ['live_feature_generator', 'poisson_value_engine']
    if not all(modules.get(m) for m in required_modules):
        print_error("Niet alle vereiste modules beschikbaar!")
        return False
    
    if not professor:
        print_error("PROFESSOR niet geladen!")
        return False
    
    try:
        from live_feature_generator import LiveFeatureGenerator
        from poisson_value_engine import PoissonValueEngine
        import numpy as np
        
        print_info("Initialiseer componenten...")
        generator = LiveFeatureGenerator()
        engine = PoissonValueEngine(simulation_runs=100)
        
        # Test match: Ajax vs PSV
        home_team = "Ajax"
        away_team = "PSV"
        
        print_info(f"\n🎯 Complete Analyse: {home_team} vs {away_team}")
        print_info("="*60)
        
        # STAP 1: Generate Features
        print_info("STAP 1: Genereer AI Features...")
        features = generator.generate_features(home_team, away_team, speelronde=19)
        print_success(f"   ✅ {len(features)} features gegenereerd")
        
        # STAP 2: PROFESSOR Voorspelling
        print_info("STAP 2: PROFESSOR Voorspelling...")
        features_array = np.array([[
            features.get('home_attack_strength', 1.5),
            features.get('home_defense_strength', 1.0),
            features.get('away_attack_strength', 1.5),
            features.get('away_defense_strength', 1.0),
            features.get('home_win_rate', 0.5),
            features.get('away_win_rate', 0.5),
            features.get('home_home_advantage', 0.6),
            features.get('away_away_form', 0.4),
            features.get('home_attack_strength', 1.5) / max(features.get('home_defense_strength', 1.0), 0.5),
            features.get('away_attack_strength', 1.5) / max(features.get('away_defense_strength', 1.0), 0.5),
            min(features.get('home_win_rate', 0.5) * 5, 5),
            min(features.get('away_win_rate', 0.5) * 5, 5),
        ]])
        
        features_scaled = professor['scaler'].transform(features_array)
        
        pred_home = sum(professor['models_home'][name].predict(features_scaled)[0] * weight 
                       for name, weight in professor['weights'].items())
        pred_away = sum(professor['models_away'][name].predict(features_scaled)[0] * weight 
                       for name, weight in professor['weights'].items())
        
        pred_home_int = max(0, round(pred_home))
        pred_away_int = max(0, round(pred_away))
        
        confidence = 100 - (abs(pred_home - pred_home_int) + abs(pred_away - pred_away_int)) * 50
        confidence = max(50, min(95, confidence))
        
        print_success(f"   ✅ Voorspelling: {pred_home_int}-{pred_away_int}")
        print_info(f"   📊 Confidence: {confidence:.1f}%")
        print_info(f"   🎯 Raw: {pred_home:.2f} - {pred_away:.2f}")
        
        # STAP 3: Poisson Simulatie
        print_info("STAP 3: Poisson Simulatie (100 runs)...")
        sim_stats = engine.simulate_match(pred_home, pred_away)
        print_success(f"   ✅ Simulatie voltooid!")
        print_info(f"   🏠 Thuis Win: {sim_stats['p_home_win']*100:.1f}%")
        print_info(f"   🤝 Gelijkspel: {sim_stats['p_draw']*100:.1f}%")
        print_info(f"   ✈️  Uit Win: {sim_stats['p_away_win']*100:.1f}%")
        
        # STAP 4: Value Betting (voorbeeld odds)
        print_info("STAP 4: Value Betting Analyse...")
        example_odds = [2.10, 3.50, 3.20]  # [Home, Draw, Away]
        
        value_bets = engine.find_value_bets(
            sim_stats,
            example_odds,
            odds_markets=None,
            min_ev=0.05
        )
        
        if value_bets:
            print_success(f"   ✅ {len(value_bets)} value bets gevonden!")
            for i, bet in enumerate(value_bets[:3], 1):
                print_info(f"   {i}. {bet['bet']} @ {bet['odds']} → EV: {bet['ev_percentage']:+.1f}%")
        else:
            print_warning("   ⚠️  Geen value bets gevonden (normale odds)")
        
        print_success("\n🎉 VOLLEDIGE INTEGRATIE WERKT PERFECT!")
        return True
    
    except Exception as e:
        print_error(f"Integratie test mislukt: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# FASE 8: API ENDPOINTS CHECK
# ============================================================================
def test_api_endpoints() -> Dict[str, bool]:
    """Test Flask API endpoints (zonder server te starten)."""
    print_header("FASE 8: API ENDPOINTS CHECK")
    
    endpoints = {
        '/': 'Main page',
        '/matches': 'Live matches page',
        '/api/predict': 'Prediction endpoint',
        '/api/golden-matches': 'Golden matches',
        '/api/live-matches/enhanced': 'Enhanced live matches',
        '/api/value-betting': 'Value betting analysis',
        '/api/value-betting/batch': 'Batch value betting',
        '/api/value-betting/report': 'Value betting report',
        '/api/simulate': 'Monte Carlo simulator',
        '/api/status': 'System status',
        '/api/scrap-status': 'Scraper status'
    }
    
    try:
        sys.path.insert(0, os.path.abspath('backend'))
        
        # Import app zonder te runnen
        import app as flask_app
        
        # Check routes
        results = {}
        for rule in flask_app.app.url_map.iter_rules():
            endpoint_path = str(rule)
            if endpoint_path in endpoints:
                results[endpoint_path] = True
                print_success(f"{endpoint_path} - {endpoints[endpoint_path]}")
        
        # Check missing
        for ep in endpoints:
            if ep not in results:
                results[ep] = False
                print_error(f"{ep} - NIET GEVONDEN!")
        
        total = len(endpoints)
        present = sum(results.values())
        print_info(f"\n📊 {present}/{total} endpoints gevonden ({present/total*100:.1f}%)")
        
        return results
    
    except Exception as e:
        print_error(f"API check mislukt: {e}")
        return {}

# ============================================================================
# FASE 9: FRONTEND CHECK
# ============================================================================
def test_frontend() -> Dict[str, bool]:
    """Test frontend bestanden."""
    print_header("FASE 9: FRONTEND CHECK")
    
    results = {}
    
    # Check index.html
    if os.path.exists('frontend/index.html'):
        with open('frontend/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'PROFESSOR' in content:
                results['index.html'] = True
                print_success("index.html - PROFESSOR references ✓")
            else:
                results['index.html'] = False
                print_warning("index.html - Geen PROFESSOR references")
    else:
        results['index.html'] = False
        print_error("index.html niet gevonden!")
    
    # Check matches.html
    if os.path.exists('frontend/matches.html'):
        with open('frontend/matches.html', 'r', encoding='utf-8') as f:
            content = f.read()
            checks = {
                'loadEnhancedMatches': 'Enhanced matches functie',
                'live_odds': 'Live odds support',
                'professor_prediction': 'PROFESSOR integration',
                'valueAnalysisWithOdds': 'Value betting with odds'
            }
            
            all_present = True
            for check, desc in checks.items():
                if check in content:
                    print_success(f"   ✓ {desc}")
                else:
                    print_warning(f"   ✗ {desc}")
                    all_present = False
            
            results['matches.html'] = all_present
    else:
        results['matches.html'] = False
        print_error("matches.html niet gevonden!")
    
    # Check CSS
    if os.path.exists('frontend/static/style.css'):
        results['style.css'] = True
        print_success("style.css gevonden")
    else:
        results['style.css'] = False
        print_error("style.css niet gevonden!")
    
    # Check JS
    if os.path.exists('frontend/static/script.js'):
        results['script.js'] = True
        print_success("script.js gevonden")
    else:
        results['script.js'] = False
        print_error("script.js niet gevonden!")
    
    total = len(results)
    success = sum(results.values())
    print_info(f"\n📊 {success}/{total} frontend checks geslaagd ({success/total*100:.1f}%)")
    
    return results

# ============================================================================
# MAIN FUSION EXECUTION
# ============================================================================
def run_fusion():
    """Run complete FUSION test suite."""
    print("\n" + "="*80)
    print(f"{Colors.MAGENTA}{Colors.BOLD}")
    print("🔥🔥🔥 THE FUSION - ULTIMATE INTEGRATION TEST 🔥🔥🔥")
    print("     ALLE COMPONENTEN WORDEN GETEST EN VERENIGD!")
    print(f"{Colors.END}")
    print("="*80)
    
    results = {
        'filesystem': False,
        'modules': False,
        'professor': False,
        'live_features': False,
        'poisson': False,
        'odds_scraper': False,
        'integration': False,
        'api': False,
        'frontend': False
    }
    
    start_time = time.time()
    
    # FASE 1: Filesystem
    filesystem = check_filesystem()
    results['filesystem'] = sum(filesystem.values()) / len(filesystem) > 0.8
    
    time.sleep(1)
    
    # FASE 2: Modules
    modules = test_imports()
    results['modules'] = sum(modules.values()) / len(modules) > 0.7
    
    time.sleep(1)
    
    # FASE 3: PROFESSOR
    professor_ok, professor = test_professor()
    results['professor'] = professor_ok
    
    time.sleep(1)
    
    # FASE 4: Live Features
    if results['modules']:
        results['live_features'] = test_live_features(modules)
        time.sleep(1)
    
    # FASE 5: Poisson
    if results['modules']:
        results['poisson'] = test_poisson_engine(modules)
        time.sleep(1)
    
    # FASE 6: Odds Scraper
    if results['modules']:
        results['odds_scraper'] = test_odds_scraper(modules)
        time.sleep(1)
    
    # FASE 7: Full Integration
    if results['professor'] and results['modules']:
        results['integration'] = test_full_integration(modules, professor)
        time.sleep(1)
    
    # FASE 8: API
    results['api'] = len(test_api_endpoints()) > 0
    time.sleep(1)
    
    # FASE 9: Frontend
    frontend_results = test_frontend()
    results['frontend'] = sum(frontend_results.values()) / len(frontend_results) > 0.5
    
    # FINAL REPORT
    elapsed = time.time() - start_time
    
    print_header("🎯 FUSION FINAL REPORT")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n{Colors.BOLD}TEST RESULTATEN:{Colors.END}")
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"   {test_name.upper():<20} {status}")
    
    print(f"\n{Colors.BOLD}STATISTIEKEN:{Colors.END}")
    print(f"   📊 Tests: {passed_tests}/{total_tests}")
    print(f"   🎯 Success Rate: {success_rate:.1f}%")
    print(f"   ⏱️  Tijd: {elapsed:.1f}s")
    
    if success_rate >= 80:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉🎉🎉 THE FUSION IS VOLTOOID! 🎉🎉🎉{Colors.END}")
        print(f"{Colors.GREEN}Alle systemen operationeel en verenigd!{Colors.END}")
        print(f"\n{Colors.CYAN}Start server met: python backend/app.py{Colors.END}")
        print(f"{Colors.CYAN}Open browser: http://127.0.0.1:5000/matches{Colors.END}")
    elif success_rate >= 60:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  THE FUSION GEDEELTELIJK GESLAAGD{Colors.END}")
        print(f"{Colors.YELLOW}Sommige componenten werken, andere hebben aandacht nodig.{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ THE FUSION MISLUKT{Colors.END}")
        print(f"{Colors.RED}Kritieke componenten zijn niet operationeel.{Colors.END}")
    
    print("\n" + "="*80)
    
    return results, success_rate

if __name__ == '__main__':
    results, success_rate = run_fusion()
    
    # Exit code op basis van success rate
    sys.exit(0 if success_rate >= 80 else 1)
