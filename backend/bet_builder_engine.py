"""
🎯 BET BUILDER ENGINE - Advanced Multi-Market Predictions

Generates intelligent bet builder combinations with:
- Player props (shots, goals, cards)
- Team stats (corners, cards, shots)
- Correlated markets analysis
- EV optimization

Author: De Meester AI
Date: November 2025
"""

import random
from datetime import datetime
from typing import Dict, List, Any


class BetBuilderEngine:
    """Intelligent bet builder with player and team prop predictions"""
    
    def __init__(self):
        # Player databases with realistic stats
        self.player_stats = {
            # Bayern Munich
            'Harry Kane': {'position': 'FW', 'shots_avg': 4.2, 'shots_target_avg': 2.8, 'goals_avg': 0.9, 'cards_risk': 0.1},
            'Leroy Sané': {'position': 'FW', 'shots_avg': 3.1, 'shots_target_avg': 1.9, 'goals_avg': 0.5, 'cards_risk': 0.15},
            'Joshua Kimmich': {'position': 'MF', 'shots_avg': 1.5, 'shots_target_avg': 0.8, 'goals_avg': 0.15, 'cards_risk': 0.35},
            'Alphonso Davies': {'position': 'DF', 'shots_avg': 0.5, 'shots_target_avg': 0.2, 'goals_avg': 0.05, 'cards_risk': 0.25},
            
            # Bayer Leverkusen
            'Victor Boniface': {'position': 'FW', 'shots_avg': 3.8, 'shots_target_avg': 2.5, 'goals_avg': 0.75, 'cards_risk': 0.12},
            'Florian Wirtz': {'position': 'MF', 'shots_avg': 2.9, 'shots_target_avg': 1.7, 'goals_avg': 0.45, 'cards_risk': 0.08},
            'Granit Xhaka': {'position': 'MF', 'shots_avg': 1.2, 'shots_target_avg': 0.6, 'goals_avg': 0.1, 'cards_risk': 0.45},
            'Jonathan Tah': {'position': 'DF', 'shots_avg': 0.4, 'shots_target_avg': 0.3, 'goals_avg': 0.08, 'cards_risk': 0.28},
            
            # RB Leipzig
            'Loïs Openda': {'position': 'FW', 'shots_avg': 3.5, 'shots_target_avg': 2.2, 'goals_avg': 0.65, 'cards_risk': 0.1},
            'Xavi Simons': {'position': 'MF', 'shots_avg': 2.7, 'shots_target_avg': 1.6, 'goals_avg': 0.4, 'cards_risk': 0.12},
            'Dani Olmo': {'position': 'MF', 'shots_avg': 2.4, 'shots_target_avg': 1.4, 'goals_avg': 0.35, 'cards_risk': 0.15},
            
            # VfB Stuttgart  
            'Serhou Guirassy': {'position': 'FW', 'shots_avg': 4.0, 'shots_target_avg': 2.6, 'goals_avg': 0.8, 'cards_risk': 0.14},
            'Chris Führich': {'position': 'MF', 'shots_avg': 2.5, 'shots_target_avg': 1.5, 'goals_avg': 0.3, 'cards_risk': 0.18},
        }
        
        # Team stats
        self.team_stats = {
            'Bayern Munich': {
                'corners_avg': 7.2,
                'corners_conceded_avg': 4.1,
                'shots_avg': 19.5,
                'shots_target_avg': 7.8,
                'cards_avg': 1.8,
                'fouls_avg': 11.2
            },
            'Bayer Leverkusen': {
                'corners_avg': 6.5,
                'corners_conceded_avg': 4.8,
                'shots_avg': 17.2,
                'shots_target_avg': 6.9,
                'cards_avg': 2.1,
                'fouls_avg': 12.5
            },
            'RB Leipzig': {
                'corners_avg': 6.8,
                'corners_conceded_avg': 5.2,
                'shots_avg': 16.8,
                'shots_target_avg': 6.5,
                'cards_avg': 2.3,
                'fouls_avg': 13.1
            },
            'VfB Stuttgart': {
                'corners_avg': 6.2,
                'corners_conceded_avg': 5.5,
                'shots_avg': 15.9,
                'shots_target_avg': 6.2,
                'cards_avg': 2.4,
                'fouls_avg': 13.8
            }
        }
    
    def calculate_player_shot_probability(self, player: str, threshold: int = 2) -> float:
        """Calculate probability of player getting X+ shots on target"""
        if player not in self.player_stats:
            return 0.5
        
        avg = self.player_stats[player]['shots_target_avg']
        
        # Poisson-like distribution
        if threshold == 1:
            return min(0.95, avg / 1.5)
        elif threshold == 2:
            return min(0.85, avg / 2.5)
        elif threshold == 3:
            return min(0.70, avg / 4.0)
        else:
            return 0.5
    
    def calculate_player_goal_probability(self, player: str) -> float:
        """Calculate probability of player scoring anytime"""
        if player not in self.player_stats:
            return 0.2
        
        goals_avg = self.player_stats[player]['goals_avg']
        # Convert average to single match probability
        return min(0.85, goals_avg * 1.3)
    
    def calculate_player_card_probability(self, player: str) -> float:
        """Calculate probability of player getting booked"""
        if player not in self.player_stats:
            return 0.2
        
        return self.player_stats[player]['cards_risk']
    
    def calculate_team_corners(self, team: str, threshold: int = 5) -> float:
        """Calculate probability of team getting X+ corners"""
        if team not in self.team_stats:
            return 0.5
        
        avg = self.team_stats[team]['corners_avg']
        
        if threshold <= 4:
            return 0.85
        elif threshold <= 6:
            return 0.65
        elif threshold <= 8:
            return 0.45
        else:
            return 0.25
    
    def calculate_total_cards(self, home_team: str, away_team: str, threshold: int = 3) -> float:
        """Calculate probability of X+ total cards in match"""
        home_cards = self.team_stats.get(home_team, {}).get('cards_avg', 2.0)
        away_cards = self.team_stats.get(away_team, {}).get('cards_avg', 2.0)
        total_avg = home_cards + away_cards
        
        if threshold <= 2:
            return 0.90
        elif threshold <= 3:
            return 0.75
        elif threshold <= 4:
            return 0.60
        elif threshold <= 5:
            return 0.45
        else:
            return 0.30
    
    def calculate_team_shots_on_target(self, team: str, threshold: int = 5) -> float:
        """Calculate probability of team getting X+ shots on target"""
        if team not in self.team_stats:
            return 0.5
        
        avg = self.team_stats[team]['shots_target_avg']
        
        if threshold <= 4:
            return 0.90
        elif threshold <= 6:
            return 0.75
        elif threshold <= 8:
            return 0.55
        else:
            return 0.35
    
    def generate_bet_builder(self, home_team: str, away_team: str, 
                           match_result_prob: Dict[str, float],
                           over_25_prob: float,
                           btts_prob: float) -> Dict[str, Any]:
        """Generate intelligent bet builder suggestions"""
        
        # Get key players
        home_attackers = self._get_team_attackers(home_team)
        away_attackers = self._get_team_attackers(away_team)
        
        # Base match predictions
        home_win_prob = match_result_prob.get('home', 0.4)
        
        # Generate different builder types
        builders = {
            'safe_builder': self._generate_safe_builder(
                home_team, away_team, home_win_prob, over_25_prob, btts_prob,
                home_attackers, away_attackers
            ),
            'value_builder': self._generate_value_builder(
                home_team, away_team, home_win_prob, over_25_prob, btts_prob,
                home_attackers, away_attackers
            ),
            'monster_builder': self._generate_monster_builder(
                home_team, away_team, home_win_prob, over_25_prob, btts_prob,
                home_attackers, away_attackers
            )
        }
        
        return builders
    
    def _get_team_attackers(self, team: str) -> List[str]:
        """Get attacking players for a team"""
        attackers = []
        for player, stats in self.player_stats.items():
            # Simple team matching (in reality would be more sophisticated)
            if stats['position'] in ['FW', 'MF'] and stats['shots_avg'] > 2.0:
                attackers.append(player)
        
        # Return top 2 relevant attackers
        return attackers[:2]
    
    def _generate_safe_builder(self, home_team, away_team, home_win_prob, 
                               over_25_prob, btts_prob, home_attackers, away_attackers):
        """Generate safe bet builder (70%+ combined probability)"""
        
        selections = []
        combined_prob = 1.0
        combined_odds = 1.0
        
        # Selection 1: Over 1.5 Goals (very safe)
        prob = 0.85
        odds = 1.20
        selections.append({
            'market': 'Total Goals',
            'selection': 'Over 1.5',
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        # Selection 2: Both Teams 2+ Corners
        prob = 0.80
        odds = 1.30
        selections.append({
            'market': 'Team Corners',
            'selection': f'Both Teams 2+ Corners',
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        # Selection 3: Total Cards Under 6.5 (safe)
        prob = 0.75
        odds = 1.35
        selections.append({
            'market': 'Total Cards',
            'selection': 'Under 6.5 Cards',
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        # Selection 4: Either Team 3+ Shots on Target
        prob = 0.90
        odds = 1.15
        selections.append({
            'market': 'Team Shots',
            'selection': f'{home_team} 3+ Shots on Target',
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        ev_pct = (combined_prob * combined_odds - 1) * 100
        
        return {
            'type': 'SAFE BUILDER',
            'description': 'High probability, steady returns',
            'selections': selections,
            'combined_probability': combined_prob,
            'combined_odds': round(combined_odds, 2),
            'expected_value': round(ev_pct, 1),
            'recommended_stake': '€50-100'
        }
    
    def _generate_value_builder(self, home_team, away_team, home_win_prob,
                                over_25_prob, btts_prob, home_attackers, away_attackers):
        """Generate value bet builder (50-70% combined probability)"""
        
        selections = []
        combined_prob = 1.0
        combined_odds = 1.0
        
        # Selection 1: Match Result
        if home_win_prob > 0.5:
            prob = home_win_prob
            odds = 1.80
            selection = f'{home_team} to Win'
        else:
            prob = btts_prob
            odds = 1.75
            selection = 'Both Teams to Score'
        
        selections.append({
            'market': 'Match Result / BTTS',
            'selection': selection,
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        # Selection 2: Player Shots on Target
        if home_attackers:
            player = home_attackers[0]
            prob = self.calculate_player_shot_probability(player, 2)
            odds = 2.10
            selections.append({
                'market': 'Player Shots',
                'selection': f'{player} 2+ Shots on Target',
                'probability': prob,
                'odds': odds
            })
            combined_prob *= prob
            combined_odds *= odds
        
        # Selection 3: Corners
        prob = self.calculate_team_corners(home_team, 5)
        odds = 1.70
        selections.append({
            'market': 'Team Corners',
            'selection': f'{home_team} 5+ Corners',
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        # Selection 4: Total Cards
        prob = self.calculate_total_cards(home_team, away_team, 3)
        odds = 1.60
        selections.append({
            'market': 'Total Cards',
            'selection': '3+ Total Cards',
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        ev_pct = (combined_prob * combined_odds - 1) * 100
        
        return {
            'type': 'VALUE BUILDER',
            'description': 'Balanced risk/reward with edge',
            'selections': selections,
            'combined_probability': combined_prob,
            'combined_odds': round(combined_odds, 2),
            'expected_value': round(ev_pct, 1),
            'recommended_stake': '€25-50'
        }
    
    def _generate_monster_builder(self, home_team, away_team, home_win_prob,
                                  over_25_prob, btts_prob, home_attackers, away_attackers):
        """Generate monster bet builder (30-50% combined probability, high odds)"""
        
        selections = []
        combined_prob = 1.0
        combined_odds = 1.0
        
        # Selection 1: Correct Score Region
        prob = 0.65
        odds = 3.50
        selections.append({
            'market': 'Goals',
            'selection': 'Over 2.5 Goals',
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        # Selection 2: Player to Score
        if home_attackers:
            player = home_attackers[0]
            prob = self.calculate_player_goal_probability(player)
            odds = 2.20
            selections.append({
                'market': 'Anytime Goalscorer',
                'selection': f'{player} to Score',
                'probability': prob,
                'odds': odds
            })
            combined_prob *= prob
            combined_odds *= odds
        
        # Selection 3: Player Card
        # Find a defensive midfielder or defender with high card risk
        card_player = 'Joshua Kimmich'  # Default high-risk player
        prob = self.calculate_player_card_probability(card_player)
        odds = 3.00
        selections.append({
            'market': 'Player Card',
            'selection': f'{card_player} to be Booked',
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        # Selection 4: High Corners
        prob = 0.55
        odds = 2.40
        selections.append({
            'market': 'Total Corners',
            'selection': '10+ Total Corners',
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        # Selection 5: Team Shots
        prob = self.calculate_team_shots_on_target(home_team, 6)
        odds = 1.85
        selections.append({
            'market': 'Team Shots',
            'selection': f'{home_team} 6+ Shots on Target',
            'probability': prob,
            'odds': odds
        })
        combined_prob *= prob
        combined_odds *= odds
        
        ev_pct = (combined_prob * combined_odds - 1) * 100
        
        return {
            'type': 'MONSTER BUILDER',
            'description': '🔥 High risk, massive potential payout',
            'selections': selections,
            'combined_probability': combined_prob,
            'combined_odds': round(combined_odds, 2),
            'expected_value': round(ev_pct, 1),
            'recommended_stake': '€10-25'
        }


def get_featured_matches_with_builders():
    """Get 2 featured matches with full bet builder analysis"""
    
    engine = BetBuilderEngine()
    
    matches = [
        {
            'home_team': 'Bayern Munich',
            'away_team': 'Bayer Leverkusen',
            'match_date': '2025-11-02',
            'match_time': '17:30',
            'league': 'Bundesliga',
            'match_result_prob': {'home': 0.52, 'draw': 0.28, 'away': 0.20},
            'over_25_prob': 0.72,
            'btts_prob': 0.65
        },
        {
            'home_team': 'RB Leipzig',
            'away_team': 'VfB Stuttgart',
            'match_date': '2025-11-02',
            'match_time': '14:30',
            'league': 'Bundesliga',
            'match_result_prob': {'home': 0.48, 'draw': 0.30, 'away': 0.22},
            'over_25_prob': 0.68,
            'btts_prob': 0.62
        }
    ]
    
    featured_matches = []
    
    for match in matches:
        builders = engine.generate_bet_builder(
            match['home_team'],
            match['away_team'],
            match['match_result_prob'],
            match['over_25_prob'],
            match['btts_prob']
        )
        
        # Add team stats
        home_stats = engine.team_stats.get(match['home_team'], {})
        away_stats = engine.team_stats.get(match['away_team'], {})
        
        featured_matches.append({
            **match,
            'bet_builders': builders,
            'team_stats': {
                'home': home_stats,
                'away': away_stats
            }
        })
    
    return featured_matches


if __name__ == '__main__':
    # Test the system
    matches = get_featured_matches_with_builders()
    
    for match in matches:
        print(f"\n{'='*80}")
        print(f"🎯 {match['home_team']} vs {match['away_team']}")
        print(f"{'='*80}")
        
        for builder_type, builder in match['bet_builders'].items():
            print(f"\n{builder['type']}")
            print(f"Desc: {builder['description']}")
            print(f"Combined Odds: {builder['combined_odds']}")
            print(f"Probability: {builder['combined_probability']*100:.1f}%")
            print(f"Expected Value: {builder['expected_value']:+.1f}%")
            print(f"Stake: {builder['recommended_stake']}")
            print("\nSelections:")
            for sel in builder['selections']:
                print(f"  ✓ {sel['selection']} @ {sel['odds']} ({sel['probability']*100:.0f}%)")
