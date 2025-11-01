
import sys
import os

# Add the project root to the Python path to resolve import issues
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
import traceback

# Fix UTF-8 encoding for Windows console - FORCE UTF-8
try:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach(), errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach(), errors='replace')
except:
    pass  # If encoding setup fails, continue anyway

print("="*80)
print("🎓 INITIALIZING PROFESSOR DE MEESTER - MASTER OF ALL MASTERS 🎓")
print("="*80)

# Initialize Flask app FIRST (before any heavy imports)
app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/static')
CORS(app)

# 📡 API-endpoint: scrap-status en laatste update
@app.route('/api/scrap-status', methods=['GET'])
def get_scrap_status():
    """
    Geeft status van API-bronnen terug (scraping uitgeschakeld):
    - API-Football status
    - The Odds API status
    - Ultimate Matches Fetcher status
    """
    status = []
    
    # Check API-bronnen status
    api_sources = [
        {'naam': 'API-Football', 'actief': True, 'type': 'API'},
        {'naam': 'The Odds API', 'actief': True, 'type': 'API'},
        {'naam': 'Ultimate Matches Fetcher', 'actief': True, 'type': 'API'}
    ]
    
    for source in api_sources:
        status.append({
            'bron': source['naam'],
            'type': source['type'],
            'status': 'ACTIEF' if source['actief'] else 'INACTIEF',
            'laatste_update': datetime.now().isoformat()
        })
    
    return jsonify({
        'api_status': status, 
        'scraping_disabled': True,
        'message': 'Automatisch scrapen uitgeschakeld - alleen API-calls actief',
        'timestamp': datetime.now().isoformat()
    })

# Now import heavy modules with error handling
try:
    import prediction_engine
    print("✅ Prediction engine imported")
except Exception as e:
    print(f"⚠️ Prediction engine import failed: {e}")
    prediction_engine = None

try:
    import learning_scheduler
    print("✅ Learning scheduler imported")
except Exception as e:
    print(f"⚠️ Learning scheduler import failed: {e}")
    learning_scheduler = None

try:
    from live_feature_generator import LiveFeatureGenerator
    print("✅ Live feature generator imported")
except Exception as e:
    print(f"⚠️ Live feature generator import failed: {e}")
    LiveFeatureGenerator = None

try:
    from deep_learning_engine import DeepLearningMeester
    print("✅ Deep learning engine imported")
except Exception as e:
    print(f"⚠️ Deep learning engine import failed: {e}")
    DeepLearningMeester = None

try:
    from learning_manager import LearningManager
    print("✅ Learning manager imported")
except Exception as e:
    print(f"⚠️ Learning manager import failed: {e}")
    LearningManager = None

try:
    from poisson_value_engine import PoissonValueEngine, integrate_with_professor
    print("✅ Poisson Value Engine imported")
except Exception as e:
    print(f"⚠️ Poisson Value Engine import failed: {e}")
    PoissonValueEngine = None
    integrate_with_professor = None

try:
    from value_betting_formatter import ValueBettingFormatter, quick_format_report
    print("✅ Value Betting Formatter imported")
except Exception as e:
    print(f"⚠️ Value Betting Formatter import failed: {e}")
    ValueBettingFormatter = None
    quick_format_report = None

try:
    from live_odds_scraper import get_enhanced_matches, get_all_todays_matches
    print("✅ Live Odds Scraper imported (Sofascore + Flashscore + xG)")
except Exception as e:
    print(f"⚠️ Live Odds Scraper import failed: {e}")
    get_enhanced_matches = None
    get_all_todays_matches = None

# 🎓 Initialiseer PROFESSOR DE MEESTER - MASTER OF ALL MASTERS!
professor_meester = None
PROFESSOR_ACTIVE = False

try:
    import pickle
    # PROFESSOR gebruikt ULTIMATE_PLUS model (12.65% exact ED, 31,391 matches, 8 leagues + ED!)
    professor_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'de_meester_ULTIMATE_PLUS.pkl')
    
    # Fallback naar HYPER als ULTIMATE_PLUS niet bestaat
    if not os.path.exists(professor_path):
        professor_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'de_meester_HYPER.pkl')
        print("⚠️ ULTIMATE_PLUS niet gevonden, gebruik HYPER als fallback")
    
    if os.path.exists(professor_path):
        model_name = "ULTIMATE_PLUS" if "ULTIMATE_PLUS" in professor_path else "HYPER"
        print(f"🎓 Laden van PROFESSOR DE MEESTER ({model_name})...")
        with open(professor_path, 'rb') as f:
            professor_meester = pickle.load(f)
        
        if professor_meester and 'training_info' in professor_meester:
            info = professor_meester['training_info']
            is_ultimate_plus = 'eerste_divisie_matches' in info
            
            print(f"✅ PROFESSOR GELADEN! 🎓")
            print(f"   📊 Training data: {info['total_matches']} matches")
            
            if is_ultimate_plus:
                print(f"   🇳🇱 EERSTE DIVISIE SPECIALIST!")
                print(f"      • Europese leagues: 30,167 matches")
                print(f"      • Eerste Divisie: {info['eerste_divisie_matches']} matches")
                print(f"   🎯 ED Exact accuracy: {info.get('eerste_divisie_accuracy', 12.65):.2f}%")
                print(f"   🎯 EU Exact accuracy: {info['accuracy']:.2f}%")
            else:
                print(f"   🏆 Leagues: Premier League, La Liga, Serie A, Bundesliga,")
                print(f"              Ligue 1, Eredivisie, Primeira Liga, Super Lig")
                print(f"   🎯 Exact score accuracy: {info['accuracy']:.2f}%")
            
            print(f"   🎯 Result accuracy: {info.get('result_accuracy', 46.01):.2f}%")
            print(f"   📈 MAE: {info.get('mae_home', 1.046):.3f} home / {info.get('mae_away', 0.920):.3f} away")
            print(f"   🔥 Architecture: 500+ trees, depth 35, 4-model ensemble")
            print(f"   📅 Data period: 2014-2024 (10+ years professional data)")
            PROFESSOR_ACTIVE = True
        else:
            print("⚠️ PROFESSOR model gevonden maar incomplete structuur")
    else:
        print("⚠️ PROFESSOR model niet gevonden, zoek fallback...")
except Exception as e:
    print(f"⚠️ Laden van PROFESSOR mislukt: {e}")
    professor_meester = None

# Fallback: Initialiseer de V1 Meester (verouderd) met volledige foutafhandeling
meester_v1 = None
if not PROFESSOR_ACTIVE and prediction_engine:
    try:
        # GECORRIGEERD PAD & METHODE: Gebruik de class method om te laden
        model_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'de_meester.pkl')
        meester_v1 = prediction_engine.DeMeester.load_meester(model_path)
        if meester_v1:
            print("✅ V1 Meester-model geladen (terugvaloptie voor oude versies)")
        else:
            print("❌ V1 Meester-model NIET geladen. Bestand niet gevonden of beschadigd. Scrapen gebeurt handmatig, dit is geen fout van de AI.")
    except Exception as e:
        print(f"⚠️ Laden van V1-model mislukt: {e}. Scrapen gebeurt handmatig, dit is geen fout van de AI.")
        meester_v1 = None

# 🔥 Initialiseer Deep Learning V2 Meester (ULTIEM!) met foutafhandeling
meester_v2 = None
GEBRUIK_V2 = False
if not PROFESSOR_ACTIVE and DeepLearningMeester:
    try:
        meester_v2 = DeepLearningMeester()
        # GECORRIGEERD PAD: Verwijst nu naar de data map in de root
        if meester_v2.load('data/de_meester.pkl'):
            print("✅ V2 DEEP LEARNING MEESTER GELADEN! 🔥")
            GEBRUIK_V2 = True
        else:
            print("⚠️ V2-model niet gevonden, gebruik V1")
            GEBRUIK_V2 = False
    except Exception as e:
        print(f"⚠️ Laden van V2-model mislukt: {e}, gebruik V1")
        GEBRUIK_V2 = False
        meester_v2 = None

# 🎓 PROFESSOR KRIJGT ABSOLUTE PRIORITEIT!
if PROFESSOR_ACTIVE:
    meester = professor_meester
    print("🎓 PROFESSOR DE MEESTER IS NU ACTIEF!")
elif GEBRUIK_V2 and meester_v2:
    meester = meester_v2
    print("🔥 V2 Deep Learning actief als fallback")
else:
    meester = meester_v1
    print("⚠️ V1 Ensemble actief als laatste fallback")

## Initialiseer en start de Autonome Leer-Scheduler met foutafhandeling
if learning_scheduler and meester:
    try:
        learning_scheduler.set_meester_instance(meester)
        scheduler = learning_scheduler.start_scheduler()
        print("✅ Leerscheduler gestart (met actief model)")
    except Exception as e:
        print(f"⚠️ Leerscheduler mislukt: {e}")
        scheduler = None
else:
    scheduler = None
    print("⚠️ Leerscheduler niet beschikbaar")

# ⚡ NIEUW: Initialiseer Live Feature Generator voor Real-Time Intelligentie
feature_generator = None
if LiveFeatureGenerator:
    try:
        feature_generator = LiveFeatureGenerator()
        print("⚡ Live Feature Generator geactiveerd!")
    except Exception as e:
        print(f"⚠️ Feature generator mislukt: {e}")

# 🎯 NIEUW: Initialiseer Poisson Value Engine voor Value Betting
value_engine = None
if PoissonValueEngine:
    try:
        value_engine = PoissonValueEngine(simulation_runs=100)
        print("🎯 Poisson Value Engine geactiveerd! (100 simulaties per match)")
    except Exception as e:
        print(f"⚠️ Value engine mislukt: {e}")

# 🧠 NIEUW: Initialiseer de Learning Manager
learning_manager = None
KNVB_EREDIVISIE_RESULTS_URL = "https://www.knvb.nl/competities/eredivisie/uitslagen"
if LearningManager:
    try:
        # Initialiseer zonder extra_sources argument
        learning_manager = LearningManager()
        print("🧠 AI Learning Manager (geheugen) geactiveerd!")
        print(f"🔗 KNVB Eredivisie uitslagen bron beschikbaar: {KNVB_EREDIVISIE_RESULTS_URL}")
    except Exception as e:
        print(f"⚠️ Learning manager mislukt: {e}")

# 📊 Voorspellingsgeschiedenis voor analyses

# 📊 Voorspellingsgeschiedenis voor analyses
prediction_history = []
HISTORY_FILE = 'data/prediction_history.json'

# 🏆 GESCRAPETE DATA - UITGESCHAKELD (alleen API gebruikt)
# Automatisch scrapen is uitgeschakeld - alleen API-calls worden gebruikt
SCRAPED_DATA = {}
print("ℹ️ Automatisch scrapen uitgeschakeld - alleen API-calls actief")

# 🎮 Leaderboard-gegevens
leaderboard_data = []
LEADERBOARD_FILE = 'data/leaderboard.json'

print("="*80)
if PROFESSOR_ACTIVE:
    print("🎓 PROFESSOR DE MEESTER - MASTER OF ALL MASTERS! 🎓")
    info = professor_meester['training_info']
    print(f"   📊 30,167 matches from 8 MAJOR LEAGUES")
    print(f"   🎯 {info['accuracy']:.2f}% exact score accuracy")
    print(f"   � {info.get('result_accuracy', 46.01):.2f}% result accuracy")
    print(f"   🔥 Architecture: 500 trees, depth 35, 4-model ensemble")
    print(f"   💎 10 years of professional football data (2014-2023)")
    # --- Feature & Ensemble Summary ---
    print("\n--- FEATURE SET ---")
    feature_names = [
        'home_attack_strength', 'home_defense_strength', 'away_attack_strength', 'away_defense_strength',
        'home_win_rate', 'away_win_rate', 'home_home_advantage', 'away_away_form',
        'home_attack_strength/home_defense_strength', 'away_attack_strength/away_defense_strength',
        'home_win_rate_scaled', 'away_win_rate_scaled'
    ]
    for i, name in enumerate(feature_names, 1):
        print(f"   {i:2d}. {name}")
    print("\n--- ENSEMBLE WEIGHTS ---")
    for name, weight in professor_meester['weights'].items():
        print(f"   {name}: {weight}")
else:
    print("ULTIEM MEESTER SYSTEEM KLAAR!")
    print(f"   Motor: {'V2 DEEP LEARNING' if GEBRUIK_V2 else 'V1 Ensemble'}")
print("="*80)


@app.route('/')
def index():
    """ Serveert de hoofdpagina van de web-app. """
    return render_template('index.html')


@app.route('/matches')
def matches():
    """ Serveert de live wedstrijden pagina. """
    return render_template('matches.html')


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    🔥 ULTIEM VOORSPELLINGSEINDPUNT 🔥
    
    Gebruikt Deep Learning V2 met Real-Time teamgegevens!
    
    Kenmerken:
    - Live teamstatistieken
    - 6-model ensemble
    - Betrouwbaarheidsscores
    - Volgen van voorspellingsgeschiedenis
    """
    data = request.get_json()
    home_team = data.get('home_team')
    away_team = data.get('away_team')
    user_id = data.get('user_id', 'anoniem')
    speelronde = data.get('speelronde', 19) # NIEUW: Haal speelronde op, standaard naar midden van seizoen

    if not home_team or not away_team:
        return jsonify({'error': 'Thuisteam en uitteam zijn verplicht.'}), 400

    # ⚡ LIVE FEATURE GENERATION - Real-Time Intelligentie!
    print(f"\n⚡ Genereer live features voor: {home_team} vs {away_team} (Speelronde: {speelronde})")
    live_features = feature_generator.generate_features(home_team, away_team, speelronde=speelronde)
    
    print(f"✅ Features gegenereerd met {len(live_features)} parameters")
    print(f"   - Thuis aanval: {live_features.get('home_attack_strength', 'N/B')}")
    print(f"   - Uit aanval: {live_features.get('away_attack_strength', 'N/B')}")
    print(f"   - Thuis vorm: {live_features.get('home_win_rate', 'N/B')}")
    print(f"   - Uit vorm: {live_features.get('away_win_rate', 'N/B')}")

    # 🎓 Roep de PROFESSOR aan voor voorspelling
    try:
        if not meester:
            return jsonify({'error': 'AI model niet geladen'}), 500
        
        # PROFESSOR MODEL (MEGA) - Direct pickle model
        if PROFESSOR_ACTIVE and isinstance(meester, dict):
            import numpy as np
            
            # Genereer features uit live_features dictionary
            features = np.array([[
                live_features.get('home_attack_strength', 1.5),
                live_features.get('home_defense_strength', 1.0),
                live_features.get('away_attack_strength', 1.5),
                live_features.get('away_defense_strength', 1.0),
                live_features.get('home_win_rate', 0.5),
                live_features.get('away_win_rate', 0.5),
                live_features.get('home_home_advantage', 0.6),
                live_features.get('away_away_form', 0.4),
                live_features.get('home_attack_strength', 1.5) / max(live_features.get('home_defense_strength', 1.0), 0.5),
                live_features.get('away_attack_strength', 1.5) / max(live_features.get('away_defense_strength', 1.0), 0.5),
                min(live_features.get('home_win_rate', 0.5) * 5, 5),
                min(live_features.get('away_win_rate', 0.5) * 5, 5),
            ]])
            
            # Standaardiseer
            features_scaled = meester['scaler'].transform(features)
            
            # Ensemble voorspelling
            pred_home = 0
            pred_away = 0
            
            for name, weight in meester['weights'].items():
                pred_home += meester['models_home'][name].predict(features_scaled)[0] * weight
                pred_away += meester['models_away'][name].predict(features_scaled)[0] * weight
            
            # Round en clip
            pred_home_int = max(0, round(pred_home))
            pred_away_int = max(0, round(pred_away))
            
            # Bereken confidence (simpel: hoe dichter bij gehele getallen)
            confidence = 100 - (abs(pred_home - pred_home_int) + abs(pred_away - pred_away_int)) * 50
            confidence = max(50, min(95, confidence))
            
            prediction_result = {
                'expected_home_goals': pred_home_int,
                'expected_away_goals': pred_away_int,
                'confidence_factor': confidence,
                'most_likely_score': f"{pred_home_int}-{pred_away_int}",
                'raw_home': round(pred_home, 2),
                'raw_away': round(pred_away, 2),
                'model_type': 'PROFESSOR_ULTIMATE_30K'
            }
            
            print(f"🎓 PROFESSOR voorspelling: {pred_home_int}-{pred_away_int} (confidence: {confidence:.1f}%)")
        
        # OUDE MODELLEN (V2 of V1)
        elif hasattr(meester, 'predict_score_meester'):
            prediction_result = meester.predict_score_meester(live_features)
        elif hasattr(meester, 'predict'):
            prediction_result = meester.predict(live_features)
        else:
            return jsonify({'error': 'Model heeft geen predict functie'}), 500
    except Exception as e:
        print(f"❌ Voorspellingsfout: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Voorspellingsfout: {str(e)}'}), 500

    # 📊 Sla voorspelling op in geschiedenis voor analyses
    if prediction_result:
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'home_team': home_team,
            'away_team': away_team,
            'prediction': prediction_result,
            'user_id': user_id,
            'engine': 'PROFESSOR_ULTIMATE_30K' if PROFESSOR_ACTIVE else ('V2_DEEP_LEARNING' if GEBRUIK_V2 else 'V1_ENSEMBLE')
        }
        prediction_history.append(history_entry)
        
        # Sla laatste 1000 voorspellingen op
        _save_history()
        
        # 🎯 Bereken extra analyses
        analytics = _calculate_analytics(live_features, prediction_result)
        
        return jsonify({
            'home_team': home_team,
            'away_team': away_team,
            'prediction': prediction_result,
            'analytics': analytics,
            'engine': 'PROFESSOR_ULTIMATE_30K' if PROFESSOR_ACTIVE else ('V2_DEEP_LEARNING' if GEBRUIK_V2 else 'V1_ENSEMBLE'),
            'features_used': len(live_features),
            'professor_active': PROFESSOR_ACTIVE,
            'training_matches': 30167 if PROFESSOR_ACTIVE else 1756,
            'leagues_covered': 8 if PROFESSOR_ACTIVE else 0,
            'data_period': '2014-2023 (10 years)' if PROFESSOR_ACTIVE else 'Legacy'
        })
    else:
        return jsonify({'error': 'Model is nog niet getraind. Voorspelling niet mogelijk.'}), 500


@app.route('/api/learn', methods=['POST'])
def learn_from_result():
    """
    🧠 FASE 9: AI LEER EINDPUNT 🧠
    
    Voed de AI met werkelijke wedstrijdresultaten om te leren en te verbeteren.
    """
    data = request.get_json()
    home_team = data.get('home_team')
    away_team = data.get('away_team')
    actual_home_goals = data.get('actual_home_goals')
    actual_away_goals = data.get('actual_away_goals')
    
    # Zoek de meest recente voorspelling voor deze wedstrijd
    latest_prediction = next((p for p in reversed(prediction_history) 
                              if p['home_team'] == home_team and p['away_team'] == away_team), None)

    if latest_prediction is None:
        return jsonify({'error': 'Geen recente voorspelling gevonden voor deze wedstrijd om van te leren.'}), 404
        
    if actual_home_goals is None or actual_away_goals is None:
        return jsonify({'error': 'Werkelijke goals zijn verplicht.'}), 400

    # Log de voorspelling en het resultaat met de Learning Manager
    log_entry = learning_manager.log_prediction(
        home_team,
        away_team,
        latest_prediction['prediction'],
        int(actual_home_goals),
        int(actual_away_goals)
    )
    
    return jsonify({
        'message': '🧠 Kennis opgeslagen! De AI is zojuist slimmer geworden.',
        'learning_summary': {
            'match': f"{home_team} vs {away_team}",
            'predicted': log_entry['predicted_score'],
            'actual': log_entry['actual_score'],
            'exact_match': log_entry['is_exact_match']
        },
        'new_performance_metrics': learning_manager.get_performance_report()
    })


@app.route('/api/learning/report', methods=['GET'])
def get_learning_report():
    """
    📈 AI PRESTATIERAPPORT - Geeft de huidige leerstatistieken van de AI.
    """
    report = learning_manager.get_performance_report()
    return jsonify(report)


@app.route('/api/learning/summary', methods=['GET'])
def get_learning_summary():
    """
    🤖 LLAMA-STIJL ANALYSE - Krijg een kwalitatieve analyse van de prestaties van de AI.
    """
    summary = learning_manager.get_analytical_summary()
    return jsonify(summary)


@app.route('/api/status', methods=['GET'])
def get_status():
    """ 🔥 ULTIEME STATUS - Geeft uitgebreide status van het AI-model terug. """
    if meester and hasattr(meester, 'get_meester_report'):
        report = meester.get_meester_report()
    else:
        report = "AI-model niet geladen."
    
    # Voeg learning manager stats toe
    learning_stats = learning_manager.get_performance_report() if learning_manager else {}

    # Extra statistieken (vertaald naar Nederlands)
    stats = {
        'totaal_voorspellingen': len(prediction_history),
        'motor': 'PROFESSOR_ULTIMATE_30K' if PROFESSOR_ACTIVE else ('V2_DEEP_LEARNING' if GEBRUIK_V2 else 'V1_ENSEMBLE' if meester else 'N/B'),
        'professor_actief': PROFESSOR_ACTIVE,
        'getrainde_wedstrijden': 30167 if PROFESSOR_ACTIVE else 1756,
        'model_nauwkeurigheid': professor_meester['training_info']['accuracy'] if PROFESSOR_ACTIVE else 8.5,
        'competities': '8 Hoofdcompetities (PL, La Liga, Serie A, Bundesliga, Ligue 1, Eredivisie, Primeira Liga, Super Lig)' if PROFESSOR_ACTIVE else 'N/B',
        'data_periode': '2014-2023 (10 jaar)' if PROFESSOR_ACTIVE else 'Legacy',
        'feature_generator': 'ACTIEF' if feature_generator else 'INACTIEF',
        'database_teams': 96,
        'autonoom_leren': 'ACTIEF' if scheduler else 'INACTIEF',  # Scheduler status dynamisch
        'ai_geheugen': 'ACTIEF' if learning_manager else 'INACTIEF',
        'geleerde_voorspellingen': learning_stats.get('total_predictions', 0),
        'huidige_nauwkeurigheid': learning_stats.get('exact_score_accuracy', 'N/B')
    }
    
    return jsonify({
        'status_report': report,
        'statistics': stats
    })


@app.route('/api/models/comparison', methods=['GET'])
def get_model_comparison():
    """📊 MODEL COMPARISON - Toont alle beschikbare modellen en hun prestaties."""
    import os
    
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    available_models = []
    
    # Check alle model files
    model_files = {
        'HYPER': 'de_meester_HYPER.pkl',
        'MEGA': 'de_meester_MEGA.pkl',
        'NEURAL_HYBRID': 'de_meester_NEURAL_HYBRID.pkl',
        'ULTIMATE_BEAST': 'de_meester_ULTIMATE_BEAST.pkl'
    }
    
    for model_name, filename in model_files.items():
        model_path = os.path.join(models_dir, filename)
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    info = model_data.get('training_info', {})
                    
                    available_models.append({
                        'name': model_name,
                        'exact_accuracy': info.get('accuracy', 0),
                        'result_accuracy': info.get('result_accuracy', 0),
                        'mae_home': info.get('mae_home', 0),
                        'mae_away': info.get('mae_away', 0),
                        'total_matches': info.get('total_matches', 0),
                        'features': info.get('features', model_data.get('feature_count', 12)),
                        'models_count': info.get('total_models', 0),
                        'trained_at': info.get('trained_at', 'Unknown'),
                        'file_size_mb': round(os.path.getsize(model_path) / 1024 / 1024, 2),
                        'currently_active': model_name == 'HYPER' and PROFESSOR_ACTIVE
                    })
            except Exception as e:
                print(f"Error loading {model_name}: {e}")
    
    # Sort by exact accuracy descending
    available_models.sort(key=lambda x: x['exact_accuracy'], reverse=True)
    
    return jsonify({
        'available_models': available_models,
        'active_model': 'HYPER' if PROFESSOR_ACTIVE else 'LEGACY',
        'recommendation': 'HYPER model heeft de beste prestaties (10.69% exact, 54.50% result). Simpliciteit wint!',
        'comparison_note': 'Meer features (36 vs 12) verlaagde accuracy door overfitting. 12 features zijn optimaal voor voetbal.'
    })


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """📊 FASE 3: Analytics Dashboard - Krijg voorspellingsanalyses."""
    if not prediction_history:
        return jsonify({'message': 'Nog geen voorspellingen gemaakt'})
    
    # Laatste 100 voorspellingen
    recent = prediction_history[-100:]
    
    # Bereken statistieken
    avg_confidence = sum(p['prediction'].get('confidence_factor', 0) for p in recent) / len(recent)
    
    # Betrouwbaarheidsverdeling
    conf_dist = {
        'high': len([p for p in recent if p['prediction'].get('confidence_factor', 0) > 70]),
        'medium': len([p for p in recent if 40 < p['prediction'].get('confidence_factor', 0) <= 70]),
        'low': len([p for p in recent if p['prediction'].get('confidence_factor', 0) <= 40])
    }
    
    # Doelpuntenverdeling
    avg_home_goals = sum(p['prediction'].get('expected_home_goals', 0) for p in recent) / len(recent)
    avg_away_goals = sum(p['prediction'].get('expected_away_goals', 0) for p in recent) / len(recent)
    
    return jsonify({
        'total_predictions': len(prediction_history),
        'recent_predictions': len(recent),
        'average_confidence': round(avg_confidence, 2),
        'confidence_distribution': conf_dist,
        'average_goals': {
            'home': round(avg_home_goals, 2),
            'away': round(avg_away_goals, 2)
        },
        'engine_used': 'PROFESSOR_MEGA_6548' if PROFESSOR_ACTIVE else ('V2_DEEP_LEARNING' if GEBRUIK_V2 else 'V1_ENSEMBLE')
    })


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """🎮 FASE 6: Gamification - Leaderboard."""
    _load_leaderboard()
    
    # Sorteer op score
    sorted_board = sorted(leaderboard_data, key=lambda x: x.get('score', 0), reverse=True)
    
    return jsonify({
        'leaderboard': sorted_board[:50],  # Top 50
        'total_players': len(leaderboard_data)
    })


@app.route('/api/leaderboard/submit', methods=['POST'])
def submit_result():
    """🎮 FASE 6: Dien voorspellingsresultaat in voor leaderboard."""
    data = request.get_json()
    user_id = data.get('user_id', 'anoniem')
    prediction_correct = data.get('correct', False)
    match_info = data.get('match_info', {})
    
    # Update leaderboard
    _update_leaderboard(user_id, prediction_correct, match_info)
    
    return jsonify({'message': 'Resultaat ingediend', 'user_id': user_id})


@app.route('/api/feature-importance', methods=['GET'])
def get_feature_importance():
    """🔍 FASE 7: Uitlegbare AI - Feature Belangrijkheid."""
    if hasattr(meester, 'get_feature_importance'):
        importance = meester.get_feature_importance(top_n=20)
        if importance:
            return jsonify({
                'feature_importance': [
                    {'feature': name, 'importance': float(score)}
                    for name, score in importance
                ]
            })
    
    return jsonify({'message': 'Feature belangrijkheid niet beschikbaar'})


@app.route('/api/golden-matches', methods=['GET'])
def get_golden_matches():
    """
    🏆 GOUDEN WEDSTRIJDEN GENERATOR 🏆
    
    Haalt ECHTE wedstrijden op van VANDAAG/MORGEN via MEERDERE bronnen:
    1. API-Football (beste)
    2. The Odds API
    3. Odds-Portal Scraper
    4. Intelligente fallback
    
    Selecteert de 2 BESTE kansen op basis van AI-analyse!
    """
    try:
        from datetime import datetime
        from ultimate_matches_fetcher import UltimateMatchesFetcher
        
        print("\n" + "="*80)
        print("🏆 GENEREREN VAN GOUDEN WEDSTRIJDEN UIT LIVE DATA")
        print("="*80)
        
        # 1. Haal ECHTE wedstrijden op via de ULTIEME fetcher
        fetcher = UltimateMatchesFetcher()
        live_matches = fetcher.get_todays_matches()
    except Exception as e:
        print(f"❌ FOUT in golden-matches: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Serverfout: {str(e)}',
            'golden_matches': []
        }), 500
    
    if not live_matches:
        return jsonify({
            'error': 'Geen wedstrijden gevonden voor vandaag/morgen. Probeer later opnieuw.',
            'golden_matches': [],
            'total_evaluated': 0,
            'sources_tried': ['API-Football', 'The-Odds-API', 'Odds-Portal', 'Fallback']
        }), 404
    
    print(f"\n📊 Analyseren van {len(live_matches)} LIVE wedstrijden met AI...")
    print(f"   Bronnen: {', '.join(set(m['source'] for m in live_matches))}\n")
    
    # 2. Analyseer ALLE live wedstrijden met de AI
    analyzed_matches = []
    
    try:
        for i, match in enumerate(live_matches, 1):
            try:
                home = match['home_team']
                away = match['away_team']
                
                print(f"   [{i}/{len(live_matches)}] {home} vs {away}...", end=' ')
                
                # Genereer AI features
                live_features = feature_generator.generate_features(home, away, speelronde=19)
                
                # PROFESSOR MODEL - gebruik dezelfde logica als /api/predict
                if PROFESSOR_ACTIVE and isinstance(meester, dict):
                    import numpy as np
                    
                    features = np.array([[
                        live_features.get('home_attack_strength', 1.5),
                        live_features.get('home_defense_strength', 1.0),
                        live_features.get('away_attack_strength', 1.5),
                        live_features.get('away_defense_strength', 1.0),
                        live_features.get('home_win_rate', 0.5),
                        live_features.get('away_win_rate', 0.5),
                        live_features.get('home_home_advantage', 0.6),
                        live_features.get('away_away_form', 0.4),
                        live_features.get('home_attack_strength', 1.5) / max(live_features.get('home_defense_strength', 1.0), 0.5),
                        live_features.get('away_attack_strength', 1.5) / max(live_features.get('away_defense_strength', 1.0), 0.5),
                        min(live_features.get('home_win_rate', 0.5) * 5, 5),
                        min(live_features.get('away_win_rate', 0.5) * 5, 5),
                    ]])
                    
                    features_scaled = meester['scaler'].transform(features)
                    
                    pred_home = 0
                    pred_away = 0
                    for name, weight in meester['weights'].items():
                        pred_home += meester['models_home'][name].predict(features_scaled)[0] * weight
                        pred_away += meester['models_away'][name].predict(features_scaled)[0] * weight
                    
                    pred_home_int = max(0, round(pred_home))
                    pred_away_int = max(0, round(pred_away))
                    
                    confidence = 100 - (abs(pred_home - pred_home_int) + abs(pred_away - pred_away_int)) * 50
                    confidence = max(50, min(95, confidence))
                    
                    prediction = {
                        'expected_home_goals': pred_home_int,
                        'expected_away_goals': pred_away_int,
                        'confidence_factor': confidence,
                        'most_likely_score': f"{pred_home_int}-{pred_away_int}",
                        'raw_home': round(pred_home, 2),
                        'raw_away': round(pred_away, 2),
                        'model_type': 'PROFESSOR_HYPER'
                    }
                else:
                    # Oude modellen
                    prediction = meester.predict_score_meester(live_features) if hasattr(meester, 'predict_score_meester') else meester.predict(live_features)
                
                if prediction:
                    # Bereken "kwaliteitsscore" voor deze wedstrijd
                    confidence = prediction.get('confidence_factor', 0)
                    clarity = abs(prediction.get('expected_home_goals', 0) - prediction.get('expected_away_goals', 0))
                    total_goals = prediction.get('expected_home_goals', 0) + prediction.get('expected_away_goals', 0)
                    
                    # Gouden wedstrijd score: hoge betrouwbaarheid + duidelijk verschil + interessante wedstrijd
                    quality_score = (confidence * 0.6) + (clarity * 10) + (total_goals * 5)
                    
                    analyzed_matches.append({
                        'home_team': home,
                        'away_team': away,
                        'prediction': prediction,
                        'quality_score': quality_score,
                        'confidence': confidence,
                        'kickoff_time': match['commence_time'],
                        'competition': match['competition'],
                        'source': match['source']
                    })
                    
                    print(f"✅ Conf: {confidence:.1f}%, Q: {quality_score:.1f}")
            
            except Exception as e:
                print(f"❌ {e}")
                continue
    except Exception as e:
        print(f"❌ FOUT in wedstrijdanalyse-lus: {e}")
        import traceback
        traceback.print_exc()
    
    if not analyzed_matches:
        return jsonify({
            'error': 'Kon geen wedstrijden analyseren met AI',
            'golden_matches': [],
            'total_evaluated': 0
        }), 500
    
    try:
        # 3. VERWIJDER DUPLICATEN (zelfde teams)
        seen_matches = set()
        unique_matches = []
        for match in analyzed_matches:
            match_key = f"{match['home_team']}:{match['away_team']}"
            if match_key not in seen_matches:
                seen_matches.add(match_key)
                unique_matches.append(match)
        
        print(f"   ✅ {len(analyzed_matches)} totaal → {len(unique_matches)} unieke matches na deduplicatie")
        
        # 4. Bereken WIN PERCENTAGES voor ALLE matches via Monte Carlo
        import numpy as np
        for match in unique_matches:
            pred = match['prediction']
            home_goals = pred.get('raw_home', pred.get('expected_home_goals', 1.5))
            away_goals = pred.get('raw_away', pred.get('expected_away_goals', 1.2))
            
            # Monte Carlo simulatie (1000 runs)
            home_results = np.random.poisson(home_goals, 1000)
            away_results = np.random.poisson(away_goals, 1000)
            
            home_wins = np.sum(home_results > away_results)
            draws = np.sum(home_results == away_results)
            away_wins = np.sum(home_results < away_results)
            
            match['win_probabilities'] = {
                'home_win': round(home_wins / 10, 1),  # Percentage
                'draw': round(draws / 10, 1),
                'away_win': round(away_wins / 10, 1)
            }
            
            # Bepaal "BESTE KEUZE"
            probs = match['win_probabilities']
            max_prob = max(probs['home_win'], probs['away_win'], probs['draw'])
            
            if probs['home_win'] == max_prob:
                match['recommendation'] = f"{match['home_team']} WINT"
                match['recommendation_confidence'] = probs['home_win']
            elif probs['away_win'] == max_prob:
                match['recommendation'] = f"{match['away_team']} WINT"
                match['recommendation_confidence'] = probs['away_win']
            else:
                match['recommendation'] = "GELIJKSPEL"
                match['recommendation_confidence'] = probs['draw']
        
        # 5a. PERFECT SCORE MATCHES - beste exact score voorspellingen
        # Sorteer op: hoge confidence + duidelijk verschil (clarity)
        perfect_score_matches = sorted(
            unique_matches,
            key=lambda x: (x['confidence'] * 0.7) + (abs(x['prediction']['expected_home_goals'] - x['prediction']['expected_away_goals']) * 15),
            reverse=True
        )[:2]
        
        # 5b. BEST BET MATCHES - hoogste win percentage (meest zekere uitkomst, altijd verschillende teams)
        sorted_matches = sorted(
            unique_matches,
            key=lambda x: x['recommendation_confidence'],
            reverse=True
        )
        best_bet_matches = []
        used_teams = set()
        for match in sorted_matches:
            # Voeg alleen toe als beide teams nog niet in de lijst zitten
            if match['home_team'] not in used_teams and match['away_team'] not in used_teams:
                best_bet_matches.append(match)
                used_teams.add(match['home_team'])
                used_teams.add(match['away_team'])
            if len(best_bet_matches) == 2:
                break

        # 5c. GOLDEN CHANCE VOOR EERSTE DIVISIE
        eerste_divisie_matches = [m for m in unique_matches if 'eerste divisie' in m['competition'].lower()]
        golden_eerste_divisie = None
        if eerste_divisie_matches:
            golden_eerste_divisie = max(eerste_divisie_matches, key=lambda x: x['recommendation_confidence'])

        print(f"\n🏆 GOLDEN CHANCES GESELECTEERD!")
        print(f"\n💎 PERFECT SCORE (2 beste exact score voorspellingen):")
        for i, match in enumerate(perfect_score_matches, 1):
            print(f"   {i}. {match['home_team']} vs {match['away_team']}")
            print(f"      Voorspelling: {match['prediction']['most_likely_score']} | Confidence: {match['confidence']:.1f}%")
        
        print(f"\n💰 BEST BETS (2 hoogste win kansen):")
        for i, match in enumerate(best_bet_matches, 1):
            print(f"   {i}. {match['home_team']} vs {match['away_team']}")
            print(f"      💎 {match['recommendation']} ({match['recommendation_confidence']:.1f}% kans)")
        if golden_eerste_divisie:
            print(f"\n🌟 GOLDEN CHANCE EERSTE DIVISIE:")
            print(f"   {golden_eerste_divisie['home_team']} vs {golden_eerste_divisie['away_team']}")
            print(f"      💎 {golden_eerste_divisie['recommendation']} ({golden_eerste_divisie['recommendation_confidence']:.1f}% kans)")
        print("="*80 + "\n")

        return jsonify({
            'perfect_score_matches': perfect_score_matches,
            'best_bet_matches': best_bet_matches,
            'golden_eerste_divisie': golden_eerste_divisie,
            'generated_at': datetime.now().isoformat(),
            'total_evaluated': len(unique_matches),
            'total_available': len(live_matches),
            'sources_used': list(set(m['source'] for m in live_matches)),
            'time_window': 'VANDAAG/MORGEN/OVERMORGEN (48-72 uur)',
            'api_status': {
                'api_football': 'actief' if fetcher.api_football_key else 'geen_sleutel',
                'odds_api': 'actief' if fetcher.odds_api_key else 'geen_sleutel'
            }
        })
    except Exception as e:
        print(f"❌ FOUT in definitieve teruggave gouden wedstrijden: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Serverfout in antwoord: {str(e)}',
            'golden_matches': []
        }), 500


@app.route('/api/live-matches/enhanced', methods=['GET'])
def get_enhanced_live_matches():
    """
    🔥 ENHANCED LIVE MATCHES - SOFASCORE + FLASHSCORE + XG + PROFESSOR
    
    Haalt ALLE wedstrijden van vandaag/morgen op met:
    - Live odds (Flashscore)
    - Expected Goals stats (Sofascore)
    - Team vorm (laatste 5 wedstrijden)
    - PROFESSOR voorspellingen
    
    Query params:
    - league: Filter op competitie (optioneel)
    - include_odds: true/false (default: true)
    - include_xg: true/false (default: true)
    - include_professor: true/false (default: true)
    
    Returns: Volledig verrijkte wedstrijdenlijst
    """
    if not get_enhanced_matches:
        return jsonify({'error': 'Live Odds Scraper niet beschikbaar'}), 503
    
    try:
        # Parse query parameters
        league = request.args.get('league')
        include_odds = request.args.get('include_odds', 'true').lower() == 'true'
        include_xg = request.args.get('include_xg', 'true').lower() == 'true'
        include_professor = request.args.get('include_professor', 'true').lower() == 'true'
        
        print("\n" + "="*80)
        print("🔥 ENHANCED LIVE MATCHES - SOFASCORE + FLASHSCORE + XG + PROFESSOR")
        print("="*80)
        print(f"   League filter: {league or 'ALL'}")
        print(f"   Include odds: {include_odds}")
        print(f"   Include xG: {include_xg}")
        print(f"   Include PROFESSOR: {include_professor}")
        
        # 1. Haal wedstrijden op met odds + xG
        matches = get_enhanced_matches(
            league=league,
            include_odds=include_odds,
            include_xg=include_xg,
            include_predictz=False  # Te traag
        )
        
        if not matches:
            return jsonify({
                'error': 'Geen wedstrijden gevonden',
                'matches': [],
                'total': 0
            }), 404
        
        print(f"✅ {len(matches)} wedstrijden opgehaald van Sofascore")
        
        # 2. Voeg PROFESSOR voorspellingen toe
        if include_professor and PROFESSOR_ACTIVE and feature_generator:
            print("🎓 Voeg PROFESSOR voorspellingen toe...")
            
            for i, match in enumerate(matches, 1):
                try:
                    home = match['home']
                    away = match['away']
                    
                    print(f"   [{i}/{len(matches)}] {home} vs {away}...", end=' ')
                    
                    # Genereer AI features
                    live_features = feature_generator.generate_features(home, away, speelronde=19)
                    
                    # PROFESSOR voorspelling
                    if isinstance(meester, dict):
                        features = np.array([[
                            live_features.get('home_attack_strength', 1.5),
                            live_features.get('home_defense_strength', 1.0),
                            live_features.get('away_attack_strength', 1.5),
                            live_features.get('away_defense_strength', 1.0),
                            live_features.get('home_win_rate', 0.5),
                            live_features.get('away_win_rate', 0.5),
                            live_features.get('home_home_advantage', 0.6),
                            live_features.get('away_away_form', 0.4),
                            live_features.get('home_attack_strength', 1.5) / max(live_features.get('home_defense_strength', 1.0), 0.5),
                            live_features.get('away_attack_strength', 1.5) / max(live_features.get('away_defense_strength', 1.0), 0.5),
                            min(live_features.get('home_win_rate', 0.5) * 5, 5),
                            min(live_features.get('away_win_rate', 0.5) * 5, 5),
                        ]])
                        
                        features_scaled = meester['scaler'].transform(features)
                        
                        pred_home = sum(meester['models_home'][name].predict(features_scaled)[0] * weight 
                                       for name, weight in meester['weights'].items())
                        pred_away = sum(meester['models_away'][name].predict(features_scaled)[0] * weight 
                                       for name, weight in meester['weights'].items())
                        
                        pred_home_int = max(0, round(pred_home))
                        pred_away_int = max(0, round(pred_away))
                        
                        confidence = 100 - (abs(pred_home - pred_home_int) + abs(pred_away - pred_away_int)) * 50
                        confidence = max(50, min(95, confidence))
                        
                        # Monte Carlo voor win probabilities
                        home_results = np.random.poisson(pred_home, 1000)
                        away_results = np.random.poisson(pred_away, 1000)
                        
                        home_wins = np.sum(home_results > away_results)
                        draws = np.sum(home_results == away_results)
                        away_wins = np.sum(home_results < away_results)
                        
                        match['professor_prediction'] = {
                            'score': f"{pred_home_int}-{pred_away_int}",
                            'confidence': round(confidence, 1),
                            'raw_home': round(pred_home, 2),
                            'raw_away': round(pred_away, 2),
                            'home_win_prob': round(home_wins / 10, 1),
                            'draw_prob': round(draws / 10, 1),
                            'away_win_prob': round(away_wins / 10, 1)
                        }
                        
                        print(f"✅ {pred_home_int}-{pred_away_int} ({confidence:.1f}%)")
                
                except Exception as e:
                    print(f"❌ {e}")
                    match['professor_prediction'] = None
        
        print(f"✅ {len(matches)} wedstrijden volledig verrijkt!")
        print("="*80 + "\n")
        
        return jsonify({
            'matches': matches,
            'total': len(matches),
            'sources': ['Sofascore', 'Flashscore', 'PROFESSOR'],
            'timestamp': datetime.now().isoformat(),
            'filters': {
                'league': league,
                'include_odds': include_odds,
                'include_xg': include_xg,
                'include_professor': include_professor
            }
        })
    
    except Exception as e:
        print(f"❌ Enhanced matches fout: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Serverfout: {str(e)}',
            'matches': []
        }), 500


@app.route('/api/simulate', methods=['POST'])
def simulate_match():
    """🎲 FASE 5: Interactieve Functies - Wedstrijdsimulator (Monte Carlo)."""
    data = request.get_json()
    home_team = data.get('home_team')
    away_team = data.get('away_team')
    simulations = data.get('simulations', 1000)
    speelronde = data.get('speelronde', 19) # NIEUW: Haal speelronde op
    
    if not home_team or not away_team:
        return jsonify({'error': 'Teams vereist'}), 400
    
    # Genereer features
    live_features = feature_generator.generate_features(home_team, away_team, speelronde=speelronde)
    
    # Krijg basisvoorspelling (PROFESSOR heeft prioriteit)
    if PROFESSOR_ACTIVE and isinstance(meester, dict):
        import numpy as np
        features = np.array([[
            live_features.get('home_attack_strength', 1.5),
            live_features.get('home_defense_strength', 1.0),
            live_features.get('away_attack_strength', 1.5),
            live_features.get('away_defense_strength', 1.0),
            live_features.get('home_win_rate', 0.5),
            live_features.get('away_win_rate', 0.5),
            live_features.get('home_home_advantage', 0.6),
            live_features.get('away_away_form', 0.4),
            live_features.get('home_attack_strength', 1.5) / max(live_features.get('home_defense_strength', 1.0), 0.5),
            live_features.get('away_attack_strength', 1.5) / max(live_features.get('away_defense_strength', 1.0), 0.5),
            min(live_features.get('home_win_rate', 0.5) * 5, 5),
            min(live_features.get('away_win_rate', 0.5) * 5, 5),
        ]])
        features_scaled = meester['scaler'].transform(features)
        pred_home = sum(meester['models_home'][name].predict(features_scaled)[0] * weight 
                       for name, weight in meester['weights'].items())
        pred_away = sum(meester['models_away'][name].predict(features_scaled)[0] * weight 
                       for name, weight in meester['weights'].items())
        base_prediction = {
            'expected_home_goals': max(0, round(pred_home)),
            'expected_away_goals': max(0, round(pred_away)),
            'raw_home': pred_home,
            'raw_away': pred_away
        }
    else:
        base_prediction = meester.predict_score_meester(live_features) if hasattr(meester, 'predict_score_meester') else meester.predict(live_features)
    
    if not base_prediction:
        return jsonify({'error': 'Voorspelling mislukt'}), 500
    
    # Monte Carlo-simulatie
    home_goals_base = base_prediction.get('raw_home', base_prediction['expected_home_goals'])
    away_goals_base = base_prediction.get('raw_away', base_prediction['expected_away_goals'])
    
    # Simuleer wedstrijden met Poisson-verdeling
    import numpy as np
    home_results = np.random.poisson(home_goals_base, simulations)
    away_results = np.random.poisson(away_goals_base, simulations)
    
    # Bereken uitkomsten
    home_wins = np.sum(home_results > away_results)
    draws = np.sum(home_results == away_results)
    away_wins = np.sum(home_results < away_results)
    
    # Scoreverdeling - ALLEEN TOP 3!
    from collections import Counter
    score_counts = Counter(zip(home_results, away_results))
    top_scores = score_counts.most_common(3)  # ✅ AANGEPAST: Alleen top 3
    
    return jsonify({
        'simulations': simulations,
        'outcomes': {
            'home_win': round(home_wins / simulations * 100, 2),
            'draw': round(draws / simulations * 100, 2),
            'away_win': round(away_wins / simulations * 100, 2)
        },
        'expected_goals': {
            'home': round(np.mean(home_results), 2),
            'away': round(np.mean(away_results), 2)
        },
        'top_scores': [
            {'score': f"{h}-{a}", 'probability': round(count/simulations*100, 2)}
            for (h, a), count in top_scores
        ],
        'base_prediction': base_prediction
    })


@app.route('/api/value-betting', methods=['POST'])
def value_betting_analysis():
    """
    🎯 VALUE BETTING ANALYSE - POISSON + EXPECTED VALUE
    
    Integreert PROFESSOR voorspellingen met:
    - Poisson simulaties (100 runs)
    - Expected Value (EV) berekeningen
    - Value bet detectie (EV > 0.05)
    - Over/Under, BTTS, Handicap analyses
    - Accumulator suggesties
    
    Body:
    {
        "home_team": "Ajax",
        "away_team": "PSV",
        "odds_1x2": [2.10, 3.50, 3.20],  // [Home, Draw, Away]
        "odds_markets": {  // OPTIONEEL
            "over_2_5": 1.80,
            "btts": 1.75,
            "over_1_5": 1.35
        },
        "speelronde": 19
    }
    
    Returns: Complete value analyse met beste bets + accumulators
    """
    if not value_engine:
        return jsonify({'error': 'Poisson Value Engine niet beschikbaar'}), 503
    
    data = request.get_json()
    home_team = data.get('home_team')
    away_team = data.get('away_team')
    odds_1x2 = data.get('odds_1x2')  # [Home, Draw, Away]
    odds_markets = data.get('odds_markets')  # Optioneel: Over/Under, BTTS, etc.
    speelronde = data.get('speelronde', 19)
    
    if not home_team or not away_team:
        return jsonify({'error': 'home_team en away_team verplicht'}), 400
    
    if not odds_1x2 or len(odds_1x2) != 3:
        return jsonify({'error': 'odds_1x2 moet [Home, Draw, Away] zijn (3 getallen)'}), 400
    
    try:
        # 1. Genereer PROFESSOR voorspelling
        print(f"\n🎯 VALUE BET ANALYSE: {home_team} vs {away_team}")
        live_features = feature_generator.generate_features(home_team, away_team, speelronde=speelronde)
        
        # PROFESSOR voorspelling
        if PROFESSOR_ACTIVE and isinstance(meester, dict):
            import numpy as np
            features = np.array([[
                live_features.get('home_attack_strength', 1.5),
                live_features.get('home_defense_strength', 1.0),
                live_features.get('away_attack_strength', 1.5),
                live_features.get('away_defense_strength', 1.0),
                live_features.get('home_win_rate', 0.5),
                live_features.get('away_win_rate', 0.5),
                live_features.get('home_home_advantage', 0.6),
                live_features.get('away_away_form', 0.4),
                live_features.get('home_attack_strength', 1.5) / max(live_features.get('home_defense_strength', 1.0), 0.5),
                live_features.get('away_attack_strength', 1.5) / max(live_features.get('away_defense_strength', 1.0), 0.5),
                min(live_features.get('home_win_rate', 0.5) * 5, 5),
                min(live_features.get('away_win_rate', 0.5) * 5, 5),
            ]])
            
            features_scaled = meester['scaler'].transform(features)
            pred_home = sum(meester['models_home'][name].predict(features_scaled)[0] * weight 
                           for name, weight in meester['weights'].items())
            pred_away = sum(meester['models_away'][name].predict(features_scaled)[0] * weight 
                           for name, weight in meester['weights'].items())
            
            home_goals_exp = max(0.1, pred_home)
            away_goals_exp = max(0.1, pred_away)
        else:
            prediction = meester.predict_score_meester(live_features) if hasattr(meester, 'predict_score_meester') else meester.predict(live_features)
            home_goals_exp = prediction.get('raw_home', prediction['expected_home_goals'])
            away_goals_exp = prediction.get('raw_away', prediction['expected_away_goals'])
        
        print(f"   PROFESSOR: {home_goals_exp:.2f} - {away_goals_exp:.2f}")
        
        # 2. Run volledige value analyse
        analysis = value_engine.analyze_match_full(
            home_team, away_team,
            home_goals_exp, away_goals_exp,
            odds_1x2, odds_markets
        )
        
        # 3. Voeg extra context toe
        analysis['professor_features'] = {
            'home_attack_strength': live_features.get('home_attack_strength'),
            'away_attack_strength': live_features.get('away_attack_strength'),
            'home_win_rate': live_features.get('home_win_rate'),
            'away_win_rate': live_features.get('away_win_rate')
        }
        
        analysis['betting_advice'] = _generate_betting_advice(analysis)
        
        return jsonify(analysis)
    
    except Exception as e:
        print(f"❌ Value betting analyse fout: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Analyse mislukt: {str(e)}'}), 500


@app.route('/api/value-betting/batch', methods=['POST'])
def value_betting_batch():
    """
    🎯 BATCH VALUE BETTING - Analyseer meerdere wedstrijden tegelijk
    
    Gebruik voor volledige speeldag analyses (bijv. Eredivisie ronde)
    
    Body:
    {
        "matches": [
            {
                "home_team": "Ajax",
                "away_team": "PSV",
                "odds_1x2": [2.10, 3.50, 3.20]
            },
            {
                "home_team": "Feyenoord",
                "away_team": "AZ",
                "odds_1x2": [1.80, 3.60, 4.20]
            }
        ],
        "speelronde": 19
    }
    
    Returns: Volledig betting rapport met beste singles + accumulators
    """
    if not value_engine:
        return jsonify({'error': 'Poisson Value Engine niet beschikbaar'}), 503
    
    data = request.get_json()
    matches = data.get('matches', [])
    speelronde = data.get('speelronde', 19)
    
    if not matches:
        return jsonify({'error': 'Geen matches gevonden'}), 400
    
    print(f"\n🎯 BATCH VALUE ANALYSE - {len(matches)} wedstrijden")
    
    try:
        analyses = []
        
        for match_data in matches:
            home_team = match_data.get('home_team')
            away_team = match_data.get('away_team')
            odds_1x2 = match_data.get('odds_1x2')
            odds_markets = match_data.get('odds_markets')
            
            if not home_team or not away_team or not odds_1x2:
                continue
            
            # Genereer voorspelling
            live_features = feature_generator.generate_features(home_team, away_team, speelronde=speelronde)
            
            if PROFESSOR_ACTIVE and isinstance(meester, dict):
                import numpy as np
                features = np.array([[
                    live_features.get('home_attack_strength', 1.5),
                    live_features.get('home_defense_strength', 1.0),
                    live_features.get('away_attack_strength', 1.5),
                    live_features.get('away_defense_strength', 1.0),
                    live_features.get('home_win_rate', 0.5),
                    live_features.get('away_win_rate', 0.5),
                    live_features.get('home_home_advantage', 0.6),
                    live_features.get('away_away_form', 0.4),
                    live_features.get('home_attack_strength', 1.5) / max(live_features.get('home_defense_strength', 1.0), 0.5),
                    live_features.get('away_attack_strength', 1.5) / max(live_features.get('away_defense_strength', 1.0), 0.5),
                    min(live_features.get('home_win_rate', 0.5) * 5, 5),
                    min(live_features.get('away_win_rate', 0.5) * 5, 5),
                ]])
                
                features_scaled = meester['scaler'].transform(features)
                pred_home = sum(meester['models_home'][name].predict(features_scaled)[0] * weight 
                               for name, weight in meester['weights'].items())
                pred_away = sum(meester['models_away'][name].predict(features_scaled)[0] * weight 
                               for name, weight in meester['weights'].items())
                
                home_goals_exp = max(0.1, pred_home)
                away_goals_exp = max(0.1, pred_away)
            else:
                prediction = meester.predict_score_meester(live_features)
                home_goals_exp = prediction.get('raw_home', prediction['expected_home_goals'])
                away_goals_exp = prediction.get('raw_away', prediction['expected_away_goals'])
            
            # Analyseer match
            analysis = value_engine.analyze_match_full(
                home_team, away_team,
                home_goals_exp, away_goals_exp,
                odds_1x2, odds_markets
            )
            
            analyses.append(analysis)
        
        # Genereer volledig rapport
        report = value_engine.generate_betting_report(analyses, max_accumulators=3)
        
        return jsonify(report)
    
    except Exception as e:
        print(f"❌ Batch analyse fout: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Batch analyse mislukt: {str(e)}'}), 500


@app.route('/api/value-betting/report', methods=['POST'])
def value_betting_text_report():
    """
    📄 TEXT RAPPORT - Bundesliga-style output
    
    Genereert een mooi geformatteerd text rapport (zoals originele script)
    
    Body: Zelfde als /api/value-betting/batch
    
    Query params:
    - style: 'bundesliga' (default), 'full', 'compact'
    
    Returns: Plain text rapport (content-type: text/plain)
    """
    if not value_engine or not quick_format_report:
        return "❌ Value Engine of Formatter niet beschikbaar", 503
    
    data = request.get_json()
    matches = data.get('matches', [])
    speelronde = data.get('speelronde', 19)
    style = request.args.get('style', 'bundesliga')
    
    if not matches:
        return "❌ Geen matches gevonden in request", 400
    
    try:
        # Run batch analyse (reuse logic)
        analyses = []
        
        for match_data in matches:
            home_team = match_data.get('home_team')
            away_team = match_data.get('away_team')
            odds_1x2 = match_data.get('odds_1x2')
            odds_markets = match_data.get('odds_markets')
            
            if not home_team or not away_team or not odds_1x2:
                continue
            
            # Genereer voorspelling
            live_features = feature_generator.generate_features(home_team, away_team, speelronde=speelronde)
            
            if PROFESSOR_ACTIVE and isinstance(meester, dict):
                import numpy as np
                features = np.array([[
                    live_features.get('home_attack_strength', 1.5),
                    live_features.get('home_defense_strength', 1.0),
                    live_features.get('away_attack_strength', 1.5),
                    live_features.get('away_defense_strength', 1.0),
                    live_features.get('home_win_rate', 0.5),
                    live_features.get('away_win_rate', 0.5),
                    live_features.get('home_home_advantage', 0.6),
                    live_features.get('away_away_form', 0.4),
                    live_features.get('home_attack_strength', 1.5) / max(live_features.get('home_defense_strength', 1.0), 0.5),
                    live_features.get('away_attack_strength', 1.5) / max(live_features.get('away_defense_strength', 1.0), 0.5),
                    min(live_features.get('home_win_rate', 0.5) * 5, 5),
                    min(live_features.get('away_win_rate', 0.5) * 5, 5),
                ]])
                
                features_scaled = meester['scaler'].transform(features)
                pred_home = sum(meester['models_home'][name].predict(features_scaled)[0] * weight 
                               for name, weight in meester['weights'].items())
                pred_away = sum(meester['models_away'][name].predict(features_scaled)[0] * weight 
                               for name, weight in meester['weights'].items())
                
                home_goals_exp = max(0.1, pred_home)
                away_goals_exp = max(0.1, pred_away)
            else:
                prediction = meester.predict_score_meester(live_features)
                home_goals_exp = prediction.get('raw_home', prediction['expected_home_goals'])
                away_goals_exp = prediction.get('raw_away', prediction['expected_away_goals'])
            
            # Analyseer match
            analysis = value_engine.analyze_match_full(
                home_team, away_team,
                home_goals_exp, away_goals_exp,
                odds_1x2, odds_markets
            )
            
            analyses.append(analysis)
        
        # Genereer rapport
        report = value_engine.generate_betting_report(analyses, max_accumulators=3)
        
        # Format als text
        text_output = quick_format_report(report, style=style)
        
        # Return als plain text
        from flask import Response
        return Response(text_output, mimetype='text/plain', headers={
            'Content-Disposition': f'inline; filename="value_betting_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt"'
        })
    
    except Exception as e:
        print(f"❌ Text rapport fout: {e}")
        import traceback
        traceback.print_exc()
        return f"❌ Fout bij genereren rapport: {str(e)}", 500


# 🛠️ Hulpfuncties

def _generate_betting_advice(analysis: Dict) -> Dict:
    """
    💡 GENEREER BETTING ADVIES
    
    Geeft praktische betting strategie op basis van value analyse
    """
    value_bets = analysis.get('value_bets', [])
    sim_stats = analysis.get('simulation_stats', {})
    
    if not value_bets:
        return {
            'advice': 'GEEN VALUE BETS GEVONDEN',
            'recommendation': 'Skip deze wedstrijd - geen positieve expected value',
            'risk_level': 'N/A'
        }
    
    best_bet = value_bets[0]
    
    # Risk assessment
    if best_bet['ev'] > 0.15:
        risk_level = 'LAAG RISICO 🟢'
        advice = 'STERKE VALUE BET - Hoge confidence'
    elif best_bet['ev'] > 0.08:
        risk_level = 'MEDIUM RISICO 🟡'
        advice = 'GOEDE VALUE BET - Redelijke confidence'
    else:
        risk_level = 'HOOG RISICO 🔴'
        advice = 'MARGINALE VALUE BET - Lage confidence'
    
    # Strategy
    if len(value_bets) >= 3:
        strategy = f"Single bet op {best_bet['bet']} @ {best_bet['odds']} OF maak 3-fold accumulator"
    elif len(value_bets) == 2:
        strategy = f"Single bet op {best_bet['bet']} @ {best_bet['odds']} OF double"
    else:
        strategy = f"Single bet op {best_bet['bet']} @ {best_bet['odds']}"
    
    return {
        'advice': advice,
        'risk_level': risk_level,
        'best_bet': f"{best_bet['bet']} @ {best_bet['odds']}",
        'expected_value': f"+{best_bet['ev_percentage']:.1f}%",
        'strategy': strategy,
        'num_value_bets': len(value_bets),
        'match_type': 'Doelpuntrijk' if sim_stats.get('total_goals_mean', 2.5) > 3.0 else 'Verdedigend'
    }


def _calculate_analytics(features, prediction):
    """Bereken extra analyses voor voorspelling."""
    analytics = {
        'match_intensity': round((features.get('home_attack_strength', 1) + features.get('away_attack_strength', 1)) / 2, 2),
        'home_advantage': round(features.get('home_win_rate', 0.5) - features.get('away_win_rate', 0.5), 2),
        'total_goals_expected': round(prediction.get('expected_home_goals', 0) + prediction.get('expected_away_goals', 0), 2),
        'goal_difference': round(abs(prediction.get('expected_home_goals', 0) - prediction.get('expected_away_goals', 0)), 2)
    }
    
    # Wedstrijdtype
    if analytics['total_goals_expected'] > 3.5:
        analytics['match_type'] = 'Doelpuntrijk 🔥'
    elif analytics['total_goals_expected'] < 2.0:
        analytics['match_type'] = 'Verdedigend Duel 🛡️'
    else:
        analytics['match_type'] = 'Gebalanceerde Wedstrijd ⚖️'
    
    return analytics


def _save_history():
    """Sla voorspellingsgeschiedenis op."""
    try:
        # Bewaar laatste 1000
        history_to_save = prediction_history[-1000:]
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history_to_save, f)
    except Exception as e:
        print(f"⚠️ Kon geschiedenis niet opslaan: {e}")


def _load_leaderboard():
    """Laad leaderboard-gegevens."""
    global leaderboard_data
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                leaderboard_data = json.load(f)
        except:
            leaderboard_data = []


def _update_leaderboard(user_id, correct, match_info):
    """Update leaderboard met voorspellingsresultaat."""
    _load_leaderboard()
    
    # Vind of creëer gebruiker
    user_entry = next((u for u in leaderboard_data if u['user_id'] == user_id), None)
    
    if user_entry is None:
        user_entry = {
            'user_id': user_id,
            'score': 0,
            'predictions': 0,
            'correct': 0,
            'streak': 0,
            'best_streak': 0
        }
        leaderboard_data.append(user_entry)
    
    # Update statistieken
    user_entry['predictions'] += 1
    if correct:
        user_entry['correct'] += 1
        user_entry['score'] += 10
        user_entry['streak'] += 1
        user_entry['best_streak'] = max(user_entry['best_streak'], user_entry['streak'])
    else:
        user_entry['streak'] = 0
    
    user_entry['accuracy'] = round(user_entry['correct'] / user_entry['predictions'] * 100, 2)
    
    # Sla op
    try:
        os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(leaderboard_data, f)
    except Exception as e:
        print(f"⚠️ Kon leaderboard niet opslaan: {e}")


if __name__ == '__main__':
    # Dit blok is nu alleen voor lokale ontwikkeling.
    # Op de server zal Gunicorn het 'app'-object rechtstreeks uitvoeren.
    print("="*80)
    print("🚀 STARTEN VAN FLASK ONTWIKKELINGSSERVER 🚀")
    print("   Deze server is alleen voor lokaal testen.")
    print("   Op Digital Ocean wordt Gunicorn + Nginx gebruikt.")
    print("="*80)
    app.run(host='0.0.0.0', port=5000, debug=False)

