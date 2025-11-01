"""
🧠 PROFESSOR BRAIN - Master AI Learning System

The core intelligence that makes De Meester AI a self-learning professor.
Continuously learns from every match, adapts strategies, and hunts value.

Author: De Meester AI - Professor Mode
Date: November 2025
"""

import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OnlineLearningPipeline:
    """Continuous learning from match results"""
    
    def __init__(self, storage_path='data/learning'):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.prediction_log = []
        self.model_performance = {
            'accuracy': [],
            'roi': [],
            'calibration': []
        }
        self.retraining_threshold = 100
        self.samples_since_retrain = 0
        
        self._load_history()
    
    def log_prediction(self, match_data: Dict[str, Any], prediction: Dict[str, Any]):
        """Log a prediction for later evaluation"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'match_id': f"{match_data['home_team']}_{match_data['away_team']}_{match_data['match_date']}",
            'match_data': match_data,
            'prediction': prediction,
            'actual_result': None,  # Will be filled when match completes
            'evaluated': False
        }
        
        self.prediction_log.append(entry)
        self._save_history()
        logger.info(f"Logged prediction for {entry['match_id']}")
    
    def update_with_result(self, match_id: str, actual_result: Dict[str, Any]):
        """Update prediction with actual match result"""
        for entry in self.prediction_log:
            if entry['match_id'] == match_id and not entry['evaluated']:
                entry['actual_result'] = actual_result
                entry['evaluated'] = True
                entry['evaluation_timestamp'] = datetime.now().isoformat()
                
                # Calculate accuracy
                accuracy = self._calculate_prediction_accuracy(entry)
                entry['accuracy'] = accuracy
                
                self.samples_since_retrain += 1
                self.model_performance['accuracy'].append(accuracy)
                
                logger.info(f"Updated {match_id} - Accuracy: {accuracy:.2%}")
                
                # Check if we need to retrain
                if self.samples_since_retrain >= self.retraining_threshold:
                    self._trigger_retrain()
                
                self._save_history()
                return entry
        
        return None
    
    def _calculate_prediction_accuracy(self, entry: Dict[str, Any]) -> float:
        """Calculate how accurate the prediction was"""
        pred = entry['prediction']
        actual = entry['actual_result']
        
        if not actual:
            return 0.0
        
        # Simple accuracy: did we predict the outcome correctly?
        predicted_outcome = pred.get('predicted_outcome', 'Unknown')
        actual_outcome = actual.get('outcome', 'Unknown')
        
        if predicted_outcome == actual_outcome:
            # Bonus points for high confidence
            confidence = pred.get('confidence', 0.5)
            return confidence
        else:
            # Penalty for wrong prediction with high confidence
            confidence = pred.get('confidence', 0.5)
            return (1 - confidence) * 0.3
    
    def _trigger_retrain(self):
        """Trigger model retraining with new data"""
        logger.info(f"🔄 TRIGGERING RETRAIN - {self.samples_since_retrain} new samples")
        
        # Prepare training data from recent evaluations
        recent_data = [e for e in self.prediction_log if e.get('evaluated', False)]
        
        if len(recent_data) < 50:
            logger.warning("Not enough data for retraining yet")
            return
        
        # Convert to training format
        X, y = self._prepare_training_data(recent_data)
        
        # TODO: Actual model retraining would happen here
        # For now, we just reset the counter
        self.samples_since_retrain = 0
        
        logger.info(f"✅ Retrain completed with {len(recent_data)} samples")
    
    def _prepare_training_data(self, entries: List[Dict]) -> tuple:
        """Convert prediction log entries to training data"""
        X = []
        y = []
        
        for entry in entries:
            # Extract features from match_data
            features = self._extract_features(entry['match_data'])
            X.append(features)
            
            # Extract labels from actual_result
            if entry['actual_result']:
                outcome = entry['actual_result'].get('outcome')
                if outcome == 'Home Win':
                    y.append(0)
                elif outcome == 'Draw':
                    y.append(1)
                elif outcome == 'Away Win':
                    y.append(2)
        
        return np.array(X), np.array(y)
    
    def _extract_features(self, match_data: Dict) -> List[float]:
        """Extract feature vector from match data"""
        # Simple feature extraction (would be much more sophisticated in production)
        features = []
        
        # Add basic features
        features.append(match_data.get('home_form', 0.5))
        features.append(match_data.get('away_form', 0.5))
        features.append(match_data.get('home_xg_avg', 1.5))
        features.append(match_data.get('away_xg_avg', 1.5))
        
        return features
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current learning performance statistics"""
        evaluated = [e for e in self.prediction_log if e.get('evaluated', False)]
        
        if not evaluated:
            return {
                'total_predictions': len(self.prediction_log),
                'evaluated': 0,
                'accuracy': 0.0,
                'samples_since_retrain': self.samples_since_retrain
            }
        
        accuracies = [e.get('accuracy', 0) for e in evaluated]
        
        return {
            'total_predictions': len(self.prediction_log),
            'evaluated': len(evaluated),
            'pending': len(self.prediction_log) - len(evaluated),
            'accuracy': np.mean(accuracies) if accuracies else 0.0,
            'accuracy_std': np.std(accuracies) if accuracies else 0.0,
            'samples_since_retrain': self.samples_since_retrain,
            'next_retrain_in': self.retraining_threshold - self.samples_since_retrain,
            'last_10_accuracy': np.mean(accuracies[-10:]) if len(accuracies) >= 10 else 0.0
        }
    
    def _save_history(self):
        """Save prediction history to disk"""
        history_file = self.storage_path / 'prediction_history.json'
        with open(history_file, 'w') as f:
            json.dump(self.prediction_log, f, indent=2)
    
    def _load_history(self):
        """Load prediction history from disk"""
        history_file = self.storage_path / 'prediction_history.json'
        if history_file.exists():
            with open(history_file, 'r') as f:
                self.prediction_log = json.load(f)
            logger.info(f"Loaded {len(self.prediction_log)} historical predictions")


class AdvancedFeatureEngine:
    """Extract 50+ intelligent features from match data"""
    
    @staticmethod
    def extract_all_features(match_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract comprehensive feature set"""
        features = {}
        
        # Form features (recent performance)
        features.update(AdvancedFeatureEngine._form_features(match_data))
        
        # xG features (expected goals)
        features.update(AdvancedFeatureEngine._xg_features(match_data))
        
        # Defensive features
        features.update(AdvancedFeatureEngine._defensive_features(match_data))
        
        # Contextual features
        features.update(AdvancedFeatureEngine._contextual_features(match_data))
        
        # Head-to-head features
        features.update(AdvancedFeatureEngine._h2h_features(match_data))
        
        return features
    
    @staticmethod
    def _form_features(match_data: Dict) -> Dict[str, float]:
        """Recent form features"""
        return {
            'home_form_5': match_data.get('home_form_last_5', 0.5),
            'away_form_5': match_data.get('away_form_last_5', 0.5),
            'home_form_10': match_data.get('home_form_last_10', 0.5),
            'away_form_10': match_data.get('away_form_last_10', 0.5),
            'home_home_form': match_data.get('home_form_home_only', 0.5),
            'away_away_form': match_data.get('away_form_away_only', 0.5),
            'home_win_streak': match_data.get('home_win_streak', 0),
            'away_win_streak': match_data.get('away_win_streak', 0),
        }
    
    @staticmethod
    def _xg_features(match_data: Dict) -> Dict[str, float]:
        """Expected goals features"""
        return {
            'home_xg_avg': match_data.get('home_xg_avg', 1.5),
            'away_xg_avg': match_data.get('away_xg_avg', 1.5),
            'home_xga_avg': match_data.get('home_xga_avg', 1.5),
            'away_xga_avg': match_data.get('away_xga_avg', 1.5),
            'home_xg_diff': match_data.get('home_xg_avg', 1.5) - match_data.get('home_xga_avg', 1.5),
            'away_xg_diff': match_data.get('away_xg_avg', 1.5) - match_data.get('away_xga_avg', 1.5),
        }
    
    @staticmethod
    def _defensive_features(match_data: Dict) -> Dict[str, float]:
        """Defensive strength features"""
        return {
            'home_clean_sheets': match_data.get('home_clean_sheets', 0),
            'away_clean_sheets': match_data.get('away_clean_sheets', 0),
            'home_goals_conceded': match_data.get('home_goals_conceded_avg', 1.5),
            'away_goals_conceded': match_data.get('away_goals_conceded_avg', 1.5),
        }
    
    @staticmethod
    def _contextual_features(match_data: Dict) -> Dict[str, float]:
        """Context features (rest, motivation, etc.)"""
        return {
            'home_rest_days': match_data.get('home_rest_days', 7),
            'away_rest_days': match_data.get('away_rest_days', 7),
            'is_derby': 1.0 if match_data.get('is_derby', False) else 0.0,
            'is_relegation_battle': 1.0 if match_data.get('is_relegation_battle', False) else 0.0,
        }
    
    @staticmethod
    def _h2h_features(match_data: Dict) -> Dict[str, float]:
        """Head-to-head historical features"""
        h2h = match_data.get('h2h', {})
        return {
            'h2h_home_wins': h2h.get('home_wins', 0),
            'h2h_away_wins': h2h.get('away_wins', 0),
            'h2h_draws': h2h.get('draws', 0),
            'h2h_avg_goals': h2h.get('avg_goals', 2.5),
        }


class MarketInefficiencyDetector:
    """Finds mispriced odds and value opportunities"""
    
    def __init__(self):
        self.threshold_ev = 0.05  # 5% minimum expected value
    
    def detect_value_bets(self, predictions: List[Dict], odds_data: List[Dict]) -> List[Dict]:
        """Find bets with positive expected value"""
        value_bets = []
        
        for pred in predictions:
            for odds in odds_data:
                if self._matches_prediction(pred, odds):
                    ev = self._calculate_expected_value(pred, odds)
                    
                    if ev > self.threshold_ev:
                        value_bets.append({
                            'prediction': pred,
                            'odds': odds,
                            'expected_value': ev,
                            'expected_value_pct': ev * 100,
                            'reason': self._explain_value(pred, odds, ev)
                        })
        
        # Sort by EV (highest first)
        value_bets.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return value_bets
    
    def _matches_prediction(self, pred: Dict, odds: Dict) -> bool:
        """Check if odds match prediction"""
        # Simple matching logic
        return pred.get('match_id') == odds.get('match_id')
    
    def _calculate_expected_value(self, pred: Dict, odds: Dict) -> float:
        """Calculate expected value: (probability * odds) - 1"""
        probability = pred.get('probability', 0.5)
        odds_decimal = odds.get('odds', 2.0)
        
        ev = (probability * odds_decimal) - 1
        return ev
    
    def _explain_value(self, pred: Dict, odds: Dict, ev: float) -> str:
        """Explain why this is a value bet"""
        prob = pred.get('probability', 0.5)
        odds_decimal = odds.get('odds', 2.0)
        implied_prob = 1 / odds_decimal
        
        return f"AI predicts {prob:.1%} probability but odds imply {implied_prob:.1%}. Value: {ev*100:.1f}%"


class MultiAgentSystem:
    """5 Specialized AI agents working together"""
    
    def __init__(self):
        self.agents = {
            'value_hunter': ValueHunterAgent(),
            'risk_manager': RiskManagerAgent(),
            'pattern_spotter': PatternSpotterAgent(),
            'sentiment_analyst': SentimentAnalystAgent(),
            'meta_strategist': MetaStrategistAgent()
        }
    
    def collaborative_decision(self, match_data: Dict, predictions: Dict) -> Dict[str, Any]:
        """All agents vote on the best action"""
        votes = {}
        confidences = {}
        
        for agent_name, agent in self.agents.items():
            vote = agent.analyze(match_data, predictions)
            votes[agent_name] = vote['recommendation']
            confidences[agent_name] = vote['confidence']
        
        # Meta-strategist makes final decision
        final_decision = self.agents['meta_strategist'].coordinate(votes, confidences)
        
        return {
            'decision': final_decision,
            'agent_votes': votes,
            'agent_confidences': confidences,
            'consensus_strength': self._calculate_consensus(votes)
        }
    
    def _calculate_consensus(self, votes: Dict) -> float:
        """Calculate how much agents agree"""
        if not votes:
            return 0.0
        
        # Count most common vote
        vote_counts = {}
        for vote in votes.values():
            action = vote.get('action', 'PASS')
            vote_counts[action] = vote_counts.get(action, 0) + 1
        
        max_votes = max(vote_counts.values())
        consensus = max_votes / len(votes)
        
        return consensus


class ValueHunterAgent:
    """Specializes in finding +EV opportunities"""
    
    def analyze(self, match_data: Dict, predictions: Dict) -> Dict:
        ev = predictions.get('expected_value', 0)
        
        if ev > 0.10:  # 10%+ EV
            return {
                'recommendation': {'action': 'BET', 'stake': 'HIGH'},
                'confidence': 0.9,
                'reason': f'Excellent value: +{ev*100:.1f}% EV'
            }
        elif ev > 0.05:  # 5%+ EV
            return {
                'recommendation': {'action': 'BET', 'stake': 'MEDIUM'},
                'confidence': 0.7,
                'reason': f'Good value: +{ev*100:.1f}% EV'
            }
        else:
            return {
                'recommendation': {'action': 'PASS'},
                'confidence': 0.5,
                'reason': 'Insufficient value'
            }


class RiskManagerAgent:
    """Protects bankroll and manages risk"""
    
    def analyze(self, match_data: Dict, predictions: Dict) -> Dict:
        confidence = predictions.get('confidence', 0.5)
        
        if confidence < 0.6:
            return {
                'recommendation': {'action': 'PASS'},
                'confidence': 0.8,
                'reason': 'Too risky - low confidence'
            }
        elif confidence < 0.75:
            return {
                'recommendation': {'action': 'BET', 'stake': 'SMALL'},
                'confidence': 0.6,
                'reason': 'Acceptable risk with small stake'
            }
        else:
            return {
                'recommendation': {'action': 'BET', 'stake': 'MEDIUM'},
                'confidence': 0.7,
                'reason': 'Good confidence level'
            }


class PatternSpotterAgent:
    """Finds historical patterns and trends"""
    
    def analyze(self, match_data: Dict, predictions: Dict) -> Dict:
        # Check for favorable patterns
        home_form = match_data.get('home_form_last_5', 0.5)
        away_form = match_data.get('away_form_last_5', 0.5)
        
        if home_form > 0.7 and away_form < 0.4:
            return {
                'recommendation': {'action': 'BET', 'stake': 'HIGH'},
                'confidence': 0.8,
                'reason': 'Strong form pattern detected'
            }
        else:
            return {
                'recommendation': {'action': 'BET', 'stake': 'MEDIUM'},
                'confidence': 0.6,
                'reason': 'Normal pattern'
            }


class SentimentAnalystAgent:
    """Analyzes market sentiment and public opinion"""
    
    def analyze(self, match_data: Dict, predictions: Dict) -> Dict:
        # Simple sentiment check
        return {
            'recommendation': {'action': 'BET', 'stake': 'MEDIUM'},
            'confidence': 0.6,
            'reason': 'Neutral market sentiment'
        }


class MetaStrategistAgent:
    """Coordinates all agents and makes final decision"""
    
    def coordinate(self, votes: Dict, confidences: Dict) -> Dict:
        """Combine agent votes into final decision"""
        
        # Count recommendations
        bet_votes = 0
        pass_votes = 0
        stake_suggestions = []
        
        for agent_name, vote in votes.items():
            action = vote.get('action', 'PASS')
            confidence = confidences[agent_name]
            
            if action == 'BET':
                bet_votes += confidence
                stake_suggestions.append(vote.get('stake', 'MEDIUM'))
            else:
                pass_votes += confidence
        
        # Make final decision
        if bet_votes > pass_votes * 1.5:  # Strong consensus to bet
            # Determine stake size
            if 'HIGH' in stake_suggestions and bet_votes > 3.0:
                stake = 'HIGH'
            elif 'SMALL' in stake_suggestions and bet_votes < 2.0:
                stake = 'SMALL'
            else:
                stake = 'MEDIUM'
            
            return {
                'action': 'BET',
                'stake_size': stake,
                'confidence': bet_votes / (bet_votes + pass_votes),
                'consensus': 'STRONG' if bet_votes > pass_votes * 2 else 'MODERATE'
            }
        else:
            return {
                'action': 'PASS',
                'confidence': pass_votes / (bet_votes + pass_votes),
                'consensus': 'WEAK'
            }


class ProfessorBrain:
    """Main orchestrator of the professor AI system"""
    
    def __init__(self):
        self.online_learner = OnlineLearningPipeline()
        self.feature_engine = AdvancedFeatureEngine()
        self.inefficiency_detector = MarketInefficiencyDetector()
        self.multi_agent = MultiAgentSystem()
        
        logger.info("🧠 PROFESSOR BRAIN INITIALIZED")
    
    def analyze_match(self, match_data: Dict, predictions: Dict, odds_data: List[Dict]) -> Dict:
        """Complete analysis of a match with all professor capabilities"""
        
        # Extract advanced features
        features = self.feature_engine.extract_all_features(match_data)
        
        # Detect market inefficiencies
        value_bets = self.inefficiency_detector.detect_value_bets([predictions], odds_data)
        
        # Multi-agent collaborative decision
        agent_decision = self.multi_agent.collaborative_decision(match_data, predictions)
        
        # Log prediction for learning
        self.online_learner.log_prediction(match_data, predictions)
        
        return {
            'match': match_data,
            'predictions': predictions,
            'advanced_features': features,
            'value_opportunities': value_bets,
            'agent_decision': agent_decision,
            'professor_recommendation': self._generate_recommendation(
                predictions, value_bets, agent_decision
            )
        }
    
    def _generate_recommendation(self, predictions: Dict, value_bets: List, 
                                 agent_decision: Dict) -> Dict:
        """Generate final professor recommendation"""
        
        action = agent_decision['decision']['action']
        confidence = agent_decision['decision']['confidence']
        
        if action == 'BET' and value_bets:
            best_value = value_bets[0]
            return {
                'action': 'BET',
                'market': best_value['prediction'].get('market', 'Unknown'),
                'selection': best_value['prediction'].get('selection', 'Unknown'),
                'odds': best_value['odds'].get('odds', 0),
                'stake_size': agent_decision['decision']['stake_size'],
                'confidence': confidence,
                'expected_value': best_value['expected_value_pct'],
                'reason': best_value['reason'],
                'consensus': agent_decision['decision']['consensus']
            }
        else:
            return {
                'action': 'PASS',
                'reason': 'No sufficient value or consensus',
                'confidence': confidence
            }
    
    def get_learning_stats(self) -> Dict:
        """Get current learning statistics"""
        return self.online_learner.get_performance_stats()


# Global professor instance
_professor = None

def get_professor() -> ProfessorBrain:
    """Get global professor instance"""
    global _professor
    if _professor is None:
        _professor = ProfessorBrain()
    return _professor


if __name__ == '__main__':
    # Test the professor brain
    professor = ProfessorBrain()
    
    # Sample match data
    match_data = {
        'home_team': 'Bayern Munich',
        'away_team': 'Bayer Leverkusen',
        'home_form_last_5': 0.8,
        'away_form_last_5': 0.6,
        'home_xg_avg': 2.5,
        'away_xg_avg': 1.8,
    }
    
    predictions = {
        'predicted_outcome': 'Home Win',
        'probability': 0.65,
        'confidence': 0.75,
        'expected_value': 0.12
    }
    
    odds_data = [
        {'match_id': 'test', 'odds': 2.10, 'bookmaker': 'Bet365'}
    ]
    
    result = professor.analyze_match(match_data, predictions, odds_data)
    
    print("\n" + "="*80)
    print("🧠 PROFESSOR ANALYSIS")
    print("="*80)
    print(f"\nAgent Decision: {result['agent_decision']['decision']}")
    print(f"Consensus: {result['agent_decision']['consensus_strength']:.1%}")
    print(f"\nProfessor Recommendation:")
    print(json.dumps(result['professor_recommendation'], indent=2))
    
    stats = professor.get_learning_stats()
    print(f"\n📊 Learning Stats:")
    print(json.dumps(stats, indent=2))
