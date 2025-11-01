"""
🚀 FLASK BACKEND API - Real-Time Betting System

REST API endpoints voor dashboard:
- GET /api/predictions - Get latest predictions
- GET /api/odds - Get current odds
- GET /api/bankroll - Get bankroll status
- GET /api/roi - Get ROI by market
- GET /api/alerts - Get active alerts
- POST /api/bet - Log a new bet
- WebSocket /ws/updates - Real-time updates

Author: Sport AI Sync
Date: November 2025
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
from datetime import datetime
import threading
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import modules (not classes, as aggregator has functions)
import backend.multi_source_aggregator as aggregator_module
from backend.ensemble_predictor import EnsemblePredictor
from backend.bankroll_manager import BankrollManager
from backend.prediction_tracker import PredictionTracker
from backend.odds_movement_monitor import OddsMovementMonitor
from backend.market_roi_analyzer import MarketROIAnalyzer
from backend.calibration_analyzer import CalibrationAnalyzer
from backend.professor_brain import ProfessorBrain
from backend.performance_analytics import get_analytics
from backend.scraper_safety import get_safety

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sport-ai-sync-secret-key-2025'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize all systems
ensemble = EnsemblePredictor()
bankroll = BankrollManager(initial_bankroll=1000.0, risk_profile='moderate')
tracker = PredictionTracker()
odds_monitor = OddsMovementMonitor()
roi_analyzer = MarketROIAnalyzer()
calibration = CalibrationAnalyzer()
professor = ProfessorBrain()  # 🧠 The AI Professor!
analytics = get_analytics()  # 📊 Performance tracking!
safety = get_safety()  # 🛡️ Safety checker!

# Cache for predictions
predictions_cache = {}
last_update = None


# =============================================
# MAIN ENDPOINTS
# =============================================

@app.route('/')
def home():
    """Serve the frontend UI"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS)"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'static')
    return send_from_directory(frontend_path, filename)


@app.route('/professor')
def professor_dashboard():
    """Serve the Professor Brain dashboard"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'professor.html')


@app.route('/api')
def api_home():
    """API documentation"""
    return jsonify({
        'message': '🚀 Sport AI Sync - Intelligent Betting System API',
        'version': '3.0',
        'status': 'online',
        'endpoints': {
            'predictions': '/api/predictions',
            'odds': '/api/odds',
            'bankroll': '/api/bankroll',
            'roi': '/api/roi',
            'alerts': '/api/alerts',
            'calibration': '/api/calibration',
            'system_status': '/api/status',
            'safety': '/api/safety',
            'betting_warning': '/api/betting-warning'
        }
    })


@app.route('/api/safety')
def safety_info():
    """Get scraper safety configuration"""
    return jsonify(safety.get_safe_config())


@app.route('/api/betting-warning')
def betting_warning():
    """Get responsible gambling warning"""
    return jsonify({
        'warning': safety.get_betting_warning(),
        'location_check': safety.check_user_location()
    })


@app.route('/api/status')
def system_status():
    """Get system status"""
    bankroll_stats = bankroll.get_statistics()
    roi_summary = roi_analyzer.get_overall_summary()
    
    return jsonify({
        'online': True,
        'timestamp': datetime.now().isoformat(),
        'bankroll': {
            'current': bankroll_stats['current_bankroll'],
            'initial': bankroll_stats['initial_bankroll'],
            'roi': bankroll_stats['roi']
        },
        'bets': {
            'total': bankroll_stats['total_bets'],
            'win_rate': bankroll_stats['win_rate']
        },
        'last_update': last_update
    })


@app.route('/api/predictions')
def get_predictions():
    """Get latest predictions using multi-source data team"""
    league = request.args.get('league', 'bundesliga')
    days_ahead = int(request.args.get('days_ahead', 2))
    
    # Check cache
    cache_key = f"{league}_{days_ahead}"
    
    if cache_key in predictions_cache:
        cached_data = predictions_cache[cache_key]
        # Cache valid for 30 minutes
        if (datetime.now() - cached_data['timestamp']).seconds < 1800:
            return jsonify(cached_data['data'])
    
    try:
        # 🤝 TEAM MODE: Use all 6 data sources working together!
        # Premium APIs (API-Football, Football-Data.org) try first
        # Free APIs (ESPN, TheSportsDB, OpenLigaDB) as supplement
        # Simulation Engine as intelligent fallback
        results_df = aggregator_module.run_full_analysis(
            league=league, 
            days_ahead=days_ahead,
            use_team_mode=True  # 🔥 ALL 6 SOURCES COLLABORATE!
        )
        
        if results_df.empty:
            return jsonify({'error': 'No matches found', 'matches': []})
        
        # Convert DataFrame to dict format expected by dashboard
        matches = []
        for _, row in results_df.iterrows():
            match_data = {
                'home_team': row['match'].split(' vs ')[0] if ' vs ' in row['match'] else 'Home',
                'away_team': row['match'].split(' vs ')[1] if ' vs ' in row['match'] else 'Away',
                'match_date': row['match_date'],
                'match_time': row['match_time'],
                'tournament': row.get('tournament', league),
                'source': row.get('source', 'Unknown'),  # Show which data source provided this match
                'predictions': [
                    {
                        'market': 'Match Result',
                        'prediction': row['prediction'],
                        'probability': float(row['p_home_win'].strip('%')) / 100 if row['prediction'] == 'Home Win' else 
                                     float(row['p_away_win'].strip('%')) / 100 if row['prediction'] == 'Away Win' else
                                     float(row['p_draw'].strip('%')) / 100,
                        'odds': float(row['odds_1x2'].split(' / ')[0]) if row['prediction'] == 'Home Win' else
                               float(row['odds_1x2'].split(' / ')[2]) if row['prediction'] == 'Away Win' else
                               float(row['odds_1x2'].split(' / ')[1]),
                        'confidence': float(row['confidence'].strip('%')) / 100,
                        'ev': row['ev'],
                        'ev_pct': row['ev'] * 100
                    },
                    {
                        'market': 'Over 2.5',
                        'prediction': 'Yes' if float(row['p_over_25'].strip('%')) > 50 else 'No',
                        'probability': float(row['p_over_25'].strip('%')) / 100,
                        'odds': 1.80,
                        'confidence': float(row['p_over_25'].strip('%')) / 100,
                        'ev': 0,
                        'ev_pct': 0
                    },
                    {
                        'market': 'BTTS',
                        'prediction': 'Yes' if float(row['p_btts'].strip('%')) > 50 else 'No',
                        'probability': float(row['p_btts'].strip('%')) / 100,
                        'odds': 1.75,
                        'confidence': float(row['p_btts'].strip('%')) / 100,
                        'ev': 0,
                        'ev_pct': 0
                    }
                ]
            }
            matches.append(match_data)
        
        results = {
            'league': league,
            'days_ahead': days_ahead,
            'matches': matches,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache results
        predictions_cache[cache_key] = {
            'data': results,
            'timestamp': datetime.now()
        }
        
        global last_update
        last_update = datetime.now().isoformat()
        
        # Emit WebSocket update
        socketio.emit('predictions_update', results)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e), 'matches': []}), 500


@app.route('/api/odds')
def get_odds():
    """Get current odds for matches"""
    match_id = request.args.get('match_id')
    
    if match_id:
        # Get odds history for specific match
        history = odds_monitor.get_odds_history(match_id, 'Home Win')
        return jsonify(history.to_dict() if not history.empty else {})
    else:
        # Get all active alerts
        alerts = odds_monitor.get_active_alerts(hours=24)
        return jsonify({
            'alerts': alerts,
            'total': len(alerts)
        })


@app.route('/api/bankroll')
def get_bankroll():
    """Get bankroll status"""
    stats = bankroll.get_statistics()
    
    return jsonify({
        'current_bankroll': stats.get('current_bankroll', 1000.0),
        'initial_bankroll': stats.get('initial_bankroll', 1000.0),
        'total_bets': stats.get('total_bets', 0),
        'wins': stats.get('wins', 0),
        'losses': stats.get('losses', 0),
        'win_rate': stats.get('win_rate', 0.0),
        'roi': stats.get('roi', 0.0),
        'total_staked': stats.get('total_staked', 0.0),
        'total_profit': stats.get('total_profit', 0.0)
    })


@app.route('/api/roi')
def get_roi():
    """Get ROI by market"""
    roi_data = roi_analyzer.get_roi_by_market()
    
    if isinstance(roi_data, dict) and 'message' in roi_data:
        return jsonify({'markets': {}, 'message': roi_data['message']})
    
    return jsonify({
        'markets': roi_data,
        'best_markets': roi_analyzer.get_best_markets(min_bets=5, top_n=5),
        'worst_markets': roi_analyzer.get_worst_markets(min_bets=5, bottom_n=3)
    })


@app.route('/api/alerts')
def get_alerts():
    """Get active alerts"""
    hours = int(request.args.get('hours', 24))
    
    odds_alerts = odds_monitor.get_active_alerts(hours=hours)
    value_opportunities = odds_monitor.get_value_opportunities()
    steam_moves = odds_monitor.get_steam_moves()
    
    return jsonify({
        'all_alerts': odds_alerts,
        'value_opportunities': value_opportunities,
        'steam_moves': steam_moves,
        'total': len(odds_alerts)
    })


@app.route('/api/calibration')
def get_calibration():
    """Get calibration metrics"""
    metrics = calibration.get_reliability_metrics()
    
    return jsonify({
        'metrics': metrics,
        'brier_score': calibration.calculate_brier_score(),
        'by_model': calibration.get_calibration_by_model(),
        'by_market': calibration.get_calibration_by_market()
    })


@app.route('/api/bet', methods=['POST'])
def log_bet():
    """Log a new bet"""
    data = request.json
    
    try:
        # Log to bankroll
        bankroll.log_bet(
            match=data['match'],
            market=data['market'],
            stake=float(data['stake']),
            odds=float(data['odds']),
            probability=float(data.get('probability', 0.5))
        )
        
        # Log to ROI analyzer
        roi_analyzer.log_bet(
            market=data['market'],
            stake=float(data['stake']),
            odds=float(data['odds']),
            match=data['match']
        )
        
        # Emit WebSocket update
        socketio.emit('bet_logged', data)
        
        return jsonify({
            'success': True,
            'message': 'Bet logged successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/bet-builders')
def get_bet_builders():
    """Get featured matches with bet builder suggestions"""
    try:
        from backend.bet_builder_engine import get_featured_matches_with_builders
        
        matches = get_featured_matches_with_builders()
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'featured_matches': matches
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/ensemble', methods=['POST'])
def get_ensemble_prediction():
    """Get ensemble prediction for a match"""
    data = request.json
    
    try:
        result = ensemble.predict_ensemble(
            home_xg=data.get('home_xg'),
            away_xg=data.get('away_xg'),
            home_form=data.get('home_form'),
            away_form=data.get('away_form'),
            odds=data.get('odds'),
            h2h_data=data.get('h2h_data')
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# =============================================
# WEBSOCKET EVENTS
# =============================================

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print('✅ Client connected')
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('❌ Client disconnected')


@socketio.on('subscribe_updates')
def handle_subscribe():
    """Client subscribed to updates"""
    print('📡 Client subscribed to updates')
    emit('subscription_confirmed', {'status': 'subscribed'})


# =============================================
# 🧠 PROFESSOR BRAIN ENDPOINTS
# =============================================

@app.route('/api/professor/analyze')
def professor_analyze():
    """
    Get Professor Brain analysis for matches
    
    Returns comprehensive analysis with:
    - Multi-agent decisions
    - Value opportunities
    - Market inefficiencies
    - Final recommendations
    """
    try:
        # Get matches (use cache or fetch fresh)
        matches = predictions_cache.get('matches', [])
        
        if not matches:
            # Fetch fresh using aggregator
            aggregator = aggregator_module.MultiSourceAggregator()
            df_matches = aggregator.get_matches_team_mode(league='bundesliga', days_ahead=3)
            
            if df_matches is None or df_matches.empty:
                return jsonify({'error': 'No matches available'}), 404
            
            # Convert to list of dicts
            matches = df_matches.to_dict('records')
        
        # Analyze with Professor Brain
        analyses = []
        for match in matches[:10]:  # Top 10 matches
            try:
                analysis = professor.analyze_match(
                    match_data=match,
                    bookmaker_odds=match.get('odds', {})
                )
                
                # Add match info
                analysis['match_info'] = {
                    'home_team': match.get('home_team', 'Unknown'),
                    'away_team': match.get('away_team', 'Unknown'),
                    'league': match.get('league', 'Unknown'),
                    'kickoff': match.get('kickoff_time', 'Unknown')
                }
                
                analyses.append(analysis)
                
            except Exception as e:
                print(f"Error analyzing match: {e}")
                continue
        
        # Sort by recommendation strength
        analyses.sort(
            key=lambda x: x['final_recommendation']['consensus_strength'],
            reverse=True
        )
        
        return jsonify({
            'analyses': analyses,
            'total_analyzed': len(analyses),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/professor/learning-stats')
def professor_learning_stats():
    """Get Professor Brain learning statistics"""
    try:
        stats = professor.get_learning_stats()
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/professor/retrain', methods=['POST'])
def professor_retrain():
    """Trigger manual retrain of Professor Brain models"""
    try:
        result = professor.online_learner.retrain_models()
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================
# 📊 PERFORMANCE ANALYTICS ENDPOINTS
# =============================================

@app.route('/api/analytics/overall')
def analytics_overall():
    """Get overall performance statistics"""
    try:
        stats = analytics.get_overall_stats()
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/markets')
def analytics_markets():
    """Get performance by market"""
    try:
        market_perf = analytics.get_market_performance()
        return jsonify(market_perf)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/timeseries')
def analytics_timeseries():
    """Get time series performance"""
    try:
        days = request.args.get('days', default=30, type=int)
        timeseries = analytics.get_time_series_performance(days=days)
        return jsonify(timeseries)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/calibration')
def analytics_calibration():
    """Get confidence calibration analysis"""
    try:
        calibration = analytics.get_confidence_calibration()
        return jsonify(calibration)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/log-bet', methods=['POST'])
def analytics_log_bet():
    """Log a placed bet"""
    try:
        bet_data = request.get_json()
        
        # Validate required fields
        required = ['match', 'market', 'selection', 'odds', 'stake']
        if not all(field in bet_data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        analytics.log_bet(bet_data)
        
        return jsonify({
            'success': True,
            'message': 'Bet logged successfully',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/settle-bet', methods=['POST'])
def analytics_settle_bet():
    """Settle a bet with result"""
    try:
        data = request.get_json()
        
        # Validate
        if 'bet_id' not in data or 'result' not in data or 'profit' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        bet = analytics.settle_bet(
            bet_id=data['bet_id'],
            result=data['result'],
            profit=data['profit']
        )
        
        if bet:
            # Also update Professor Brain learning
            try:
                professor.online_learner.update_with_result(
                    prediction_id=data['bet_id'],
                    actual_outcome=data['result']
                )
            except:
                pass  # Non-critical
            
            return jsonify({
                'success': True,
                'bet': bet,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Bet not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================
# BACKGROUND TASKS
# =============================================

def background_odds_monitor():
    """Monitor odds in background (every 5 minutes)"""
    while True:
        try:
            # Check for odds movements
            alerts = odds_monitor.get_active_alerts(hours=1)
            
            if alerts:
                # Emit to all connected clients
                socketio.emit('odds_alert', {
                    'alerts': alerts,
                    'timestamp': datetime.now().isoformat()
                })
            
            time.sleep(300)  # 5 minutes
        
        except Exception as e:
            print(f"Error in odds monitor: {e}")
            time.sleep(60)


def start_background_tasks():
    """Start all background tasks"""
    # Start odds monitoring
    odds_thread = threading.Thread(target=background_odds_monitor, daemon=True)
    odds_thread.start()


# =============================================
# RUN SERVER
# =============================================

if __name__ == '__main__':
    print("="*80)
    print("🚀 SPORT AI SYNC - API SERVER")
    print("="*80)
    print("\n📡 Starting server...")
    print("   URL: http://localhost:5000")
    print("\n📊 Endpoints:")
    print("   GET  /api/predictions - Latest predictions")
    print("   GET  /api/odds - Odds & alerts")
    print("   GET  /api/bankroll - Bankroll status")
    print("   GET  /api/roi - ROI by market")
    print("   GET  /api/alerts - Active alerts")
    print("   POST /api/bet - Log new bet")
    print("\n🔌 WebSocket: ws://localhost:5000")
    print("="*80)
    
    # Start background tasks
    start_background_tasks()
    
    # Run server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
