"""
💰 BANKROLL MANAGER - Kelly Criterion + Risk Management

Features:
- Kelly Criterion optimal stake calculation
- Risk profiles (Conservative, Moderate, Aggressive)
- Bankroll tracking
- ROI calculations
- Bet history

Author: Sport AI Sync
Date: November 2025
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class BankrollManager:
    """
    Smart Bankroll Management met Kelly Criterion
    
    Kelly Formula: f = (bp - q) / b
    where:
    - f = fraction of bankroll to bet
    - b = odds - 1 (net odds)
    - p = probability of winning
    - q = 1 - p (probability of losing)
    """
    
    def __init__(self, initial_bankroll: float = 1000.0, risk_profile: str = "moderate"):
        """
        Initialize Bankroll Manager
        
        Args:
            initial_bankroll: Starting bankroll in EUR
            risk_profile: 'conservative', 'moderate', or 'aggressive'
        """
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.risk_profile = risk_profile
        self.bet_history = []
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # Risk factors (percentage of Kelly to use)
        self.risk_factors = {
            'conservative': 0.25,  # 25% of Kelly
            'moderate': 0.50,      # 50% of Kelly
            'aggressive': 1.00     # 100% of Kelly (full Kelly)
        }
        
        # Load existing history
        self._load_history()
    
    def calculate_kelly_stake(self, probability: float, odds: float, 
                             custom_risk: Optional[float] = None) -> Dict:
        """
        Calculate optimal stake using Kelly Criterion
        
        Args:
            probability: Win probability (0.0 - 1.0)
            odds: Decimal odds (e.g., 2.10)
            custom_risk: Optional custom risk factor (overrides profile)
        
        Returns:
            Dict with stake info
        """
        # Kelly formula
        b = odds - 1  # Net odds
        p = probability
        q = 1 - p
        
        # Full Kelly fraction
        kelly_fraction = (b * p - q) / b
        
        # Apply risk factor
        risk_factor = custom_risk if custom_risk else self.risk_factors[self.risk_profile]
        adjusted_kelly = kelly_fraction * risk_factor
        
        # Calculate stake (max 10% of bankroll per bet for safety)
        max_stake_percent = 0.10
        kelly_stake = self.current_bankroll * max(0, min(adjusted_kelly, max_stake_percent))
        
        # Expected Value
        ev = (probability * (odds - 1)) - (1 - probability)
        expected_return = kelly_stake * ev
        
        return {
            'stake': round(kelly_stake, 2),
            'stake_percent': round(adjusted_kelly * 100, 2),
            'kelly_full': round(kelly_fraction * 100, 2),
            'kelly_adjusted': round(adjusted_kelly * 100, 2),
            'ev': round(ev, 4),
            'expected_return': round(expected_return, 2),
            'risk_profile': self.risk_profile,
            'risk_factor': risk_factor,
            'current_bankroll': self.current_bankroll,
            'max_loss': round(kelly_stake, 2),
            'max_win': round(kelly_stake * (odds - 1), 2)
        }
    
    def get_stake_recommendation(self, probability: float, odds: float, 
                                market: str, match: str) -> Dict:
        """
        Get complete stake recommendation with safety checks
        
        Args:
            probability: Win probability
            odds: Decimal odds
            market: Market type (e.g., "Over 2.5")
            match: Match name
        
        Returns:
            Complete recommendation with warnings
        """
        stake_info = self.calculate_kelly_stake(probability, odds)
        
        # Safety checks
        warnings = []
        
        # 1. Check EV threshold
        if stake_info['ev'] < 0.03:
            warnings.append("⚠️ Low EV (<3%) - Consider skipping")
        
        # 2. Check stake size
        if stake_info['stake_percent'] > 8:
            warnings.append("⚠️ High stake (>8%) - High risk")
        elif stake_info['stake_percent'] < 1:
            warnings.append("ℹ️ Low stake (<1%) - Small edge")
        
        # 3. Check probability vs odds mismatch
        implied_prob = 1 / odds
        prob_diff = abs(probability - implied_prob)
        if prob_diff < 0.05:
            warnings.append("⚠️ Tight margin - No clear edge")
        
        # 4. Check bankroll impact
        if stake_info['max_loss'] > self.current_bankroll * 0.15:
            warnings.append("🚨 RISK WARNING: Stake >15% of bankroll!")
        
        # Recommendation
        if stake_info['ev'] > 0.08 and len(warnings) <= 1:
            recommendation = "✅ STRONG BET"
        elif stake_info['ev'] > 0.05 and len(warnings) <= 2:
            recommendation = "✓ GOOD BET"
        elif stake_info['ev'] > 0.03:
            recommendation = "⚠️ MARGINAL BET"
        else:
            recommendation = "❌ SKIP"
        
        return {
            'match': match,
            'market': market,
            'probability': probability,
            'odds': odds,
            'stake': stake_info['stake'],
            'stake_percent': stake_info['stake_percent'],
            'ev': stake_info['ev'],
            'expected_return': stake_info['expected_return'],
            'recommendation': recommendation,
            'warnings': warnings,
            'kelly_info': stake_info
        }
    
    def log_bet(self, match: str, market: str, stake: float, odds: float, 
                probability: float, status: str = 'pending') -> None:
        """
        Log a bet to history
        
        Args:
            match: Match name
            market: Market type
            stake: Stake amount
            odds: Decimal odds
            probability: Win probability
            status: 'pending', 'won', 'lost', 'void'
        """
        bet = {
            'timestamp': datetime.now().isoformat(),
            'match': match,
            'market': market,
            'stake': stake,
            'odds': odds,
            'probability': probability,
            'status': status,
            'potential_return': stake * odds if status == 'pending' else 0,
            'profit': 0  # Updated when bet settles
        }
        
        self.bet_history.append(bet)
        self._save_history()
    
    def settle_bet(self, bet_index: int, won: bool) -> Dict:
        """
        Settle a bet (mark as won/lost)
        
        Args:
            bet_index: Index in bet_history
            won: True if bet won, False if lost
        
        Returns:
            Updated bet info
        """
        if bet_index >= len(self.bet_history):
            return {'error': 'Invalid bet index'}
        
        bet = self.bet_history[bet_index]
        
        if won:
            bet['status'] = 'won'
            bet['profit'] = bet['stake'] * (bet['odds'] - 1)
            self.current_bankroll += bet['profit']
        else:
            bet['status'] = 'lost'
            bet['profit'] = -bet['stake']
            self.current_bankroll += bet['profit']
        
        bet['settled_at'] = datetime.now().isoformat()
        
        self._save_history()
        
        return bet
    
    def get_statistics(self) -> Dict:
        """
        Get complete bankroll statistics
        
        Returns:
            Statistics dict with performance metrics
        """
        if not self.bet_history:
            return {
                'total_bets': 0,
                'pending_bets': 0,
                'settled_bets': 0,
                'message': 'No bets recorded yet'
            }
        
        df = pd.DataFrame(self.bet_history)
        
        # Basic counts
        total_bets = len(df)
        pending = len(df[df['status'] == 'pending'])
        settled = len(df[df['status'].isin(['won', 'lost'])])
        
        if settled == 0:
            return {
                'total_bets': total_bets,
                'pending_bets': pending,
                'settled_bets': 0,
                'message': 'No settled bets yet'
            }
        
        # Performance metrics
        settled_df = df[df['status'].isin(['won', 'lost'])].copy()
        won_bets = len(settled_df[settled_df['status'] == 'won'])
        lost_bets = len(settled_df[settled_df['status'] == 'lost'])
        
        total_staked = settled_df['stake'].sum()
        total_profit = settled_df['profit'].sum()
        
        roi = (total_profit / total_staked) * 100 if total_staked > 0 else 0
        win_rate = (won_bets / settled) * 100 if settled > 0 else 0
        
        avg_odds = settled_df['odds'].mean()
        avg_stake = settled_df['stake'].mean()
        
        # Current status
        bankroll_change = self.current_bankroll - self.initial_bankroll
        bankroll_change_pct = (bankroll_change / self.initial_bankroll) * 100
        
        # Best/worst bets
        best_bet = settled_df.loc[settled_df['profit'].idxmax()] if settled > 0 else None
        worst_bet = settled_df.loc[settled_df['profit'].idxmin()] if settled > 0 else None
        
        return {
            'total_bets': total_bets,
            'pending_bets': pending,
            'settled_bets': settled,
            'won_bets': won_bets,
            'lost_bets': lost_bets,
            'win_rate': round(win_rate, 2),
            'total_staked': round(total_staked, 2),
            'total_profit': round(total_profit, 2),
            'roi': round(roi, 2),
            'avg_odds': round(avg_odds, 2),
            'avg_stake': round(avg_stake, 2),
            'initial_bankroll': self.initial_bankroll,
            'current_bankroll': round(self.current_bankroll, 2),
            'bankroll_change': round(bankroll_change, 2),
            'bankroll_change_pct': round(bankroll_change_pct, 2),
            'best_bet': {
                'match': best_bet['match'],
                'profit': round(best_bet['profit'], 2)
            } if best_bet is not None else None,
            'worst_bet': {
                'match': worst_bet['match'],
                'profit': round(worst_bet['profit'], 2)
            } if worst_bet is not None else None,
            'risk_profile': self.risk_profile
        }
    
    def get_pending_bets(self) -> List[Dict]:
        """Get all pending bets"""
        return [bet for bet in self.bet_history if bet['status'] == 'pending']
    
    def _save_history(self) -> None:
        """Save bet history to file"""
        os.makedirs(self.data_dir, exist_ok=True)
        history_file = os.path.join(self.data_dir, 'bankroll_history.json')
        
        data = {
            'initial_bankroll': self.initial_bankroll,
            'current_bankroll': self.current_bankroll,
            'risk_profile': self.risk_profile,
            'bet_history': self.bet_history,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_history(self) -> None:
        """Load bet history from file"""
        history_file = os.path.join(self.data_dir, 'bankroll_history.json')
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                data = json.load(f)
                self.initial_bankroll = data.get('initial_bankroll', self.initial_bankroll)
                self.current_bankroll = data.get('current_bankroll', self.current_bankroll)
                self.risk_profile = data.get('risk_profile', self.risk_profile)
                self.bet_history = data.get('bet_history', [])


# =============================================
# QUICK ACCESS FUNCTIONS
# =============================================

def calculate_stake(probability: float, odds: float, bankroll: float = 1000, 
                   risk_profile: str = "moderate") -> Dict:
    """
    Quick stake calculation (no manager instance needed)
    
    Args:
        probability: Win probability (0-1)
        odds: Decimal odds
        bankroll: Current bankroll
        risk_profile: 'conservative', 'moderate', 'aggressive'
    
    Returns:
        Stake recommendation dict
    """
    manager = BankrollManager(bankroll, risk_profile)
    return manager.calculate_kelly_stake(probability, odds)


def get_stake_recommendation(probability: float, odds: float, market: str, 
                            match: str, bankroll: float = 1000) -> Dict:
    """
    Quick stake recommendation (no manager instance needed)
    """
    manager = BankrollManager(bankroll)
    return manager.get_stake_recommendation(probability, odds, market, match)


# =============================================
# DEMO / TEST
# =============================================
if __name__ == "__main__":
    print("="*80)
    print("💰 BANKROLL MANAGER - Kelly Criterion Demo")
    print("="*80)
    
    # Initialize manager
    manager = BankrollManager(initial_bankroll=1000, risk_profile="moderate")
    
    # Example bets
    bets = [
        {'match': 'Bayern vs Leverkusen', 'market': 'Over 2.5', 'prob': 0.78, 'odds': 1.80},
        {'match': 'Leipzig vs Stuttgart', 'market': 'BTTS', 'prob': 0.72, 'odds': 1.75},
        {'match': 'Heidenheim vs Frankfurt', 'market': 'Away Win', 'prob': 0.55, 'odds': 1.90},
    ]
    
    print(f"\n💼 Starting Bankroll: €{manager.current_bankroll:.2f}")
    print(f"🎯 Risk Profile: {manager.risk_profile.upper()}")
    print("\n" + "="*80)
    
    for bet in bets:
        print(f"\n📊 {bet['match']} - {bet['market']}")
        print(f"   Probability: {bet['prob']:.0%} | Odds: {bet['odds']}")
        
        rec = manager.get_stake_recommendation(
            bet['prob'], bet['odds'], bet['market'], bet['match']
        )
        
        print(f"\n   {rec['recommendation']}")
        print(f"   💰 Recommended Stake: €{rec['stake']:.2f} ({rec['stake_percent']:.1f}% of bankroll)")
        print(f"   📈 Expected Value: {rec['ev']:.2%}")
        print(f"   💵 Expected Return: €{rec['expected_return']:.2f}")
        
        if rec['warnings']:
            print(f"\n   Warnings:")
            for warning in rec['warnings']:
                print(f"   {warning}")
        
        print("\n" + "-"*80)
    
    print("\n" + "="*80)
    print("✅ Kelly Criterion Bankroll Manager Ready!")
    print("="*80)
