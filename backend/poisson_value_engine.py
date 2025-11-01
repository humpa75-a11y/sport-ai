"""
🎯 POISSON VALUE ENGINE - EXPECTED VALUE & SIMULATIE MODULE
============================================================
Integreert Poisson-simulaties met PROFESSOR DE MEESTER voor:
- Expected Value (EV) berekeningen
- Monte Carlo simulaties (20+ runs)
- Value bet detectie
- Multi-fold combinaties
- BTTS, Over/Under, Handicap analyses

Gebaseerd op professionele betting analyse met scipy.stats.poisson
"""

import numpy as np
import pandas as pd
from scipy.stats import poisson
import itertools
import warnings
from typing import Dict, List, Tuple, Optional
warnings.filterwarnings("ignore")


class PoissonValueEngine:
    """
    🎯 VALUE BET ENGINE - Detecteert waardevolle weddenschappen
    
    Gebruikt Poisson-verdeling + Expected Value voor objectieve analyses
    """
    
    def __init__(self, simulation_runs: int = 100):
        """
        Initialiseer de Value Engine
        
        Args:
            simulation_runs: Aantal Monte Carlo simulaties per wedstrijd (default: 100)
        """
        self.simulation_runs = simulation_runs
        
        # Default odds (worden overschreven als API odds beschikbaar zijn)
        self.default_odds = {
            'over_2_5': 1.80,
            'btts': 1.75,
            'over_1_5': 1.35,
            'under_2_5': 2.00,
            'over_3_5': 2.50
        }
        
        print(f"🎯 Poisson Value Engine geïnitialiseerd ({simulation_runs} runs per match)")
    
    
    def simulate_match(self, home_goals_exp: float, away_goals_exp: float, 
                       runs: Optional[int] = None) -> Dict:
        """
        🎲 MONTE CARLO SIMULATIE - Simuleer wedstrijd met Poisson-verdeling
        
        Args:
            home_goals_exp: Verwachte thuisdoelpunten (van PROFESSOR)
            away_goals_exp: Verwachte uitdoelpunten (van PROFESSOR)
            runs: Aantal simulaties (default: self.simulation_runs)
        
        Returns:
            Dictionary met alle berekende kansen en statistieken
        """
        if runs is None:
            runs = self.simulation_runs
        
        # Genereer random Poisson samples
        home_goals = poisson.rvs(home_goals_exp, size=runs)
        away_goals = poisson.rvs(away_goals_exp, size=runs)
        
        total_goals = home_goals + away_goals
        btts = (home_goals > 0) & (away_goals > 0)
        goal_diff = home_goals - away_goals
        
        # Bereken alle relevante kansen
        stats = {
            # Basis statistieken
            'home_goals_mean': float(home_goals.mean()),
            'away_goals_mean': float(away_goals.mean()),
            'total_goals_mean': float(total_goals.mean()),
            'goal_diff_mean': float(goal_diff.mean()),
            
            # 1X2 kansen
            'p_home_win': float((home_goals > away_goals).mean()),
            'p_draw': float((home_goals == away_goals).mean()),
            'p_away_win': float((home_goals < away_goals).mean()),
            
            # Over/Under kansen
            'p_over_0_5': float((total_goals >= 1).mean()),
            'p_over_1_5': float((total_goals >= 2).mean()),
            'p_over_2_5': float((total_goals >= 3).mean()),
            'p_over_3_5': float((total_goals >= 4).mean()),
            'p_over_4_5': float((total_goals >= 5).mean()),
            'p_under_2_5': float((total_goals < 3).mean()),
            
            # BTTS (Both Teams To Score)
            'p_btts_yes': float(btts.mean()),
            'p_btts_no': float((~btts).mean()),
            
            # Handicap kansen
            'p_home_minus_1_5': float((goal_diff >= 2).mean()),  # Home -1.5
            'p_home_minus_0_5': float((goal_diff >= 1).mean()),  # Home -0.5
            'p_away_minus_1_5': float((goal_diff <= -2).mean()), # Away -1.5
            'p_away_minus_0_5': float((goal_diff <= -1).mean()), # Away -0.5
            
            # Exact scores (top 5)
            'exact_scores': self._get_top_scores(home_goals, away_goals, top_n=5),
            
            # Metadata
            'simulation_runs': runs,
            'home_goals_expected': home_goals_exp,
            'away_goals_expected': away_goals_exp
        }
        
        return stats
    
    
    def _get_top_scores(self, home_goals: np.ndarray, away_goals: np.ndarray, 
                        top_n: int = 5) -> List[Dict]:
        """
        Haal de meest waarschijnlijke exacte scores op
        
        Returns:
            Lijst met {score: '2-1', probability: 0.15, count: 150}
        """
        from collections import Counter
        
        score_counts = Counter(zip(home_goals, away_goals))
        total = len(home_goals)
        
        top_scores = [
            {
                'score': f"{h}-{a}",
                'probability': float(count / total),
                'count': int(count),
                'home_goals': int(h),
                'away_goals': int(a)
            }
            for (h, a), count in score_counts.most_common(top_n)
        ]
        
        return top_scores
    
    
    def calculate_expected_value(self, probability: float, odds: float) -> float:
        """
        📊 EXPECTED VALUE FORMULE
        
        EV = (Probability × (Odds - 1)) - (1 - Probability)
        
        EV > 0 = VALUE BET! 💰
        EV < 0 = Slechte bet
        
        Args:
            probability: Kans dat bet wint (0.0 - 1.0)
            odds: Bookmaker odds (bijv. 2.50)
        
        Returns:
            Expected Value (positief = value bet)
        """
        ev = (probability * (odds - 1)) - (1 - probability)
        return float(ev)
    
    
    def find_value_bets(self, simulation_stats: Dict, odds_1x2: List[float], 
                        odds_markets: Optional[Dict] = None,
                        min_ev: float = 0.05) -> List[Dict]:
        """
        🔍 DETECTEER VALUE BETS
        
        Vindt alle weddenschappen met positieve Expected Value
        
        Args:
            simulation_stats: Output van simulate_match()
            odds_1x2: [Home Win, Draw, Away Win] odds
            odds_markets: Dict met extra odds (over_2_5, btts, etc.)
            min_ev: Minimale EV om te kwalificeren als value bet (default: 0.05)
        
        Returns:
            Lijst met value bets gesorteerd op EV (hoogste eerst)
        """
        if odds_markets is None:
            odds_markets = self.default_odds.copy()
        
        value_bets = []
        
        # 1X2 MARKET
        markets_1x2 = [
            ('Home Win', simulation_stats['p_home_win'], odds_1x2[0]),
            ('Draw', simulation_stats['p_draw'], odds_1x2[1]),
            ('Away Win', simulation_stats['p_away_win'], odds_1x2[2]),
        ]
        
        for bet_name, prob, odds in markets_1x2:
            ev = self.calculate_expected_value(prob, odds)
            if ev > min_ev:
                value_bets.append({
                    'market': '1X2',
                    'bet': bet_name,
                    'odds': float(odds),
                    'probability': float(prob),
                    'ev': float(ev),
                    'ev_percentage': float(ev * 100),
                    'implied_odds': float(1 / prob) if prob > 0 else 999.0
                })
        
        # OVER/UNDER MARKET
        over_under_markets = [
            ('Over 1.5', simulation_stats['p_over_1_5'], odds_markets.get('over_1_5', 1.35)),
            ('Over 2.5', simulation_stats['p_over_2_5'], odds_markets.get('over_2_5', 1.80)),
            ('Over 3.5', simulation_stats['p_over_3_5'], odds_markets.get('over_3_5', 2.50)),
            ('Under 2.5', simulation_stats['p_under_2_5'], odds_markets.get('under_2_5', 2.00)),
        ]
        
        for bet_name, prob, odds in over_under_markets:
            ev = self.calculate_expected_value(prob, odds)
            if ev > min_ev:
                value_bets.append({
                    'market': 'Over/Under',
                    'bet': bet_name,
                    'odds': float(odds),
                    'probability': float(prob),
                    'ev': float(ev),
                    'ev_percentage': float(ev * 100),
                    'implied_odds': float(1 / prob) if prob > 0 else 999.0
                })
        
        # BTTS MARKET
        btts_markets = [
            ('BTTS Yes', simulation_stats['p_btts_yes'], odds_markets.get('btts', 1.75)),
            ('BTTS No', simulation_stats['p_btts_no'], odds_markets.get('btts_no', 2.00)),
        ]
        
        for bet_name, prob, odds in btts_markets:
            ev = self.calculate_expected_value(prob, odds)
            if ev > min_ev:
                value_bets.append({
                    'market': 'BTTS',
                    'bet': bet_name,
                    'odds': float(odds),
                    'probability': float(prob),
                    'ev': float(ev),
                    'ev_percentage': float(ev * 100),
                    'implied_odds': float(1 / prob) if prob > 0 else 999.0
                })
        
        # Sorteer op EV (hoogste eerst)
        value_bets.sort(key=lambda x: x['ev'], reverse=True)
        
        return value_bets
    
    
    def create_accumulator(self, bets: List[Dict], stake: float = 10.0) -> Dict:
        """
        🎰 MAAK ACCUMULATOR (COMBI-BET)
        
        Combineert meerdere value bets in één parlay
        
        Args:
            bets: Lijst van bet dictionaries (uit find_value_bets)
            stake: Inzet bedrag
        
        Returns:
            Accumulator info met totale odds, kans, potentiële winst
        """
        if not bets:
            return {
                'error': 'Geen bets om te combineren',
                'total_odds': 0,
                'win_probability': 0,
                'potential_win': 0
            }
        
        total_odds = 1.0
        total_probability = 1.0
        
        for bet in bets:
            total_odds *= bet['odds']
            total_probability *= bet['probability']
        
        potential_win = stake * total_odds
        expected_return = stake * total_probability * total_odds
        
        return {
            'num_bets': len(bets),
            'stake': float(stake),
            'total_odds': round(total_odds, 2),
            'win_probability': round(total_probability, 4),
            'win_probability_pct': round(total_probability * 100, 2),
            'potential_win': round(potential_win, 2),
            'potential_profit': round(potential_win - stake, 2),
            'expected_return': round(expected_return, 2),
            'expected_profit': round(expected_return - stake, 2),
            'is_value_bet': expected_return > stake,
            'bets': bets
        }
    
    
    def analyze_match_full(self, home_team: str, away_team: str,
                           home_goals_exp: float, away_goals_exp: float,
                           odds_1x2: List[float],
                           odds_markets: Optional[Dict] = None) -> Dict:
        """
        🎓 VOLLEDIGE WEDSTRIJD ANALYSE
        
        Combineert PROFESSOR voorspellingen met Poisson simulaties + EV analyse
        
        Args:
            home_team: Naam thuisteam
            away_team: Naam uitteam
            home_goals_exp: PROFESSOR verwachte thuisdoelpunten
            away_goals_exp: PROFESSOR verwachte uitdoelpunten
            odds_1x2: [Home, Draw, Away] odds
            odds_markets: Extra markten (optioneel)
        
        Returns:
            Complete analyse met simulaties, value bets, accumulators
        """
        print(f"\n🎯 VALUE ANALYSE: {home_team} vs {away_team}")
        print(f"   Expected Goals: {home_goals_exp:.2f} - {away_goals_exp:.2f}")
        
        # 1. Run simulatie
        sim_stats = self.simulate_match(home_goals_exp, away_goals_exp)
        
        # 2. Vind value bets
        value_bets = self.find_value_bets(sim_stats, odds_1x2, odds_markets)
        
        # 3. Maak beste accumulator (top 3 value bets)
        best_acca = None
        if len(value_bets) >= 2:
            best_acca = self.create_accumulator(value_bets[:3], stake=10.0)
        
        print(f"   ✅ {len(value_bets)} value bets gevonden!")
        if value_bets:
            print(f"   💎 Beste bet: {value_bets[0]['bet']} @ {value_bets[0]['odds']} (EV: +{value_bets[0]['ev_percentage']:.1f}%)")
        
        return {
            'match': f"{home_team} vs {away_team}",
            'home_team': home_team,
            'away_team': away_team,
            'simulation_stats': sim_stats,
            'value_bets': value_bets,
            'best_accumulator': best_acca,
            'odds_1x2': odds_1x2,
            'professor_prediction': {
                'home_goals': home_goals_exp,
                'away_goals': away_goals_exp,
                'total_goals': home_goals_exp + away_goals_exp
            }
        }
    
    
    def generate_betting_report(self, analyses: List[Dict], 
                                max_accumulators: int = 3) -> Dict:
        """
        📊 GENEREER BETTING RAPPORT
        
        Maakt een volledig overzicht van alle value bets en beste combinaties
        
        Args:
            analyses: Lijst van analyze_match_full() outputs
            max_accumulators: Aantal accumulator varianten (4-fold, 5-fold, etc.)
        
        Returns:
            Complete betting strategie met single bets + accumulators
        """
        print("\n" + "="*80)
        print("📊 GENERATING BETTING REPORT - PROFESSOR VALUE STRATEGY")
        print("="*80)
        
        # Verzamel alle value bets
        all_value_bets = []
        for analysis in analyses:
            for bet in analysis['value_bets']:
                bet_copy = bet.copy()
                bet_copy['match'] = analysis['match']
                all_value_bets.append(bet_copy)
        
        # Sorteer op EV
        all_value_bets.sort(key=lambda x: x['ev'], reverse=True)
        
        # Maak verschillende accumulator strategieën
        accumulators = []
        for n in range(2, min(len(all_value_bets) + 1, max_accumulators + 3)):
            if n > len(all_value_bets):
                break
            acca = self.create_accumulator(all_value_bets[:n], stake=10.0)
            acca['type'] = f"{n}-Fold"
            accumulators.append(acca)
        
        # Sorteer accumulators op expected profit
        accumulators.sort(key=lambda x: x['expected_profit'], reverse=True)
        
        report = {
            'total_matches_analyzed': len(analyses),
            'total_value_bets_found': len(all_value_bets),
            'top_single_bets': all_value_bets[:10],
            'recommended_accumulators': accumulators[:max_accumulators],
            'analyses': analyses,
            'summary': {
                'best_ev_bet': all_value_bets[0] if all_value_bets else None,
                'best_accumulator': accumulators[0] if accumulators else None,
                'average_ev': float(np.mean([b['ev'] for b in all_value_bets])) if all_value_bets else 0,
                'total_markets_covered': len(set(b['market'] for b in all_value_bets))
            }
        }
        
        print(f"\n✅ {len(all_value_bets)} VALUE BETS DETECTED")
        if all_value_bets:
            print(f"💎 Best Single Bet: {report['summary']['best_ev_bet']['match']}")
            print(f"   → {report['summary']['best_ev_bet']['bet']} @ {report['summary']['best_ev_bet']['odds']}")
            print(f"   → EV: +{report['summary']['best_ev_bet']['ev_percentage']:.1f}%")
        
        if accumulators:
            best_acca = accumulators[0]
            print(f"\n🎰 Best Accumulator: {best_acca['type']}")
            print(f"   → Total Odds: {best_acca['total_odds']}x")
            print(f"   → Win Probability: {best_acca['win_probability_pct']:.2f}%")
            print(f"   → €10 → €{best_acca['potential_win']:.2f}")
        
        print("="*80 + "\n")
        
        return report


# ============================================================================
# INTEGRATIE MET PROFESSOR DE MEESTER
# ============================================================================

def integrate_with_professor(professor_prediction: Dict, 
                             odds_1x2: List[float],
                             home_team: str = None,
                             away_team: str = None) -> Dict:
    """
    🎓 INTEGRATIE FUNCTIE - Koppel PROFESSOR aan Poisson Value Engine
    
    Gebruik deze functie in app.py om value bets toe te voegen aan voorspellingen
    
    Args:
        professor_prediction: Output van /api/predict
        odds_1x2: Live odds [Home, Draw, Away]
        home_team: Team naam (optioneel, uit prediction)
        away_team: Team naam (optioneel, uit prediction)
    
    Returns:
        Aangevulde prediction met value_analysis
    """
    engine = PoissonValueEngine(simulation_runs=100)
    
    # Extract expected goals uit PROFESSOR
    home_goals = professor_prediction.get('expected_home_goals', 1.5)
    away_goals = professor_prediction.get('expected_away_goals', 1.5)
    
    # Run simulatie
    sim_stats = engine.simulate_match(home_goals, away_goals)
    
    # Vind value bets
    value_bets = engine.find_value_bets(sim_stats, odds_1x2)
    
    # Voeg toe aan prediction
    professor_prediction['value_analysis'] = {
        'simulation_stats': sim_stats,
        'value_bets': value_bets,
        'has_value_bets': len(value_bets) > 0,
        'best_value_bet': value_bets[0] if value_bets else None
    }
    
    return professor_prediction


if __name__ == '__main__':
    """
    🧪 TEST MODULE - Reproduceer de Duitse Bundesliga analyse
    """
    print("\n" + "="*80)
    print("🧪 TESTING POISSON VALUE ENGINE - BUNDESLIGA 30 OKT 2025")
    print("="*80)
    
    # Test data (uit jouw code)
    test_matches = [
        ["RB Leipzig", "VfB Stuttgart", [2.00, 3.90, 3.40], [2.1, 1.8]],
        ["Heidenheim", "Eintracht Frankfurt", [3.60, 4.00, 1.90], [1.2, 2.0]],
        ["Union Berlin", "SC Freiburg", [2.50, 3.30, 2.75], [1.8, 1.6]],
    ]
    
    engine = PoissonValueEngine(simulation_runs=100)
    analyses = []
    
    for match in test_matches:
        home, away, odds, goals = match
        analysis = engine.analyze_match_full(
            home, away, goals[0], goals[1], odds
        )
        analyses.append(analysis)
    
    # Genereer rapport
    report = engine.generate_betting_report(analyses)
    
    print("\n✅ MODULE TEST COMPLETED - READY FOR INTEGRATION!")
    print("   Use integrate_with_professor() in app.py /api/predict endpoint")
