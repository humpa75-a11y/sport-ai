"""
📊 PERFORMANCE ANALYTICS - Advanced Tracking & Insights

Tracks every prediction, calculates sophisticated metrics,
and provides actionable insights for continuous improvement.

Author: De Meester AI - Professor Mode
Date: November 2025
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict


class PerformanceAnalytics:
    """Advanced performance tracking and analysis"""
    
    def __init__(self, storage_path='data/analytics'):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.bets_log = []
        self.daily_performance = defaultdict(dict)
        self.market_performance = defaultdict(lambda: {'wins': 0, 'total': 0, 'profit': 0})
        
        self._load_data()
    
    def log_bet(self, bet_data: Dict[str, Any]):
        """Log a placed bet"""
        bet_entry = {
            'timestamp': datetime.now().isoformat(),
            'bet_id': f"bet_{len(self.bets_log)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            **bet_data,
            'settled': False
        }
        
        self.bets_log.append(bet_entry)
        self._save_data()
    
    def settle_bet(self, bet_id: str, result: str, profit: float):
        """Settle a bet with result"""
        for bet in self.bets_log:
            if bet['bet_id'] == bet_id and not bet.get('settled', False):
                bet['settled'] = True
                bet['result'] = result  # 'win', 'loss', 'push'
                bet['profit'] = profit
                bet['settlement_timestamp'] = datetime.now().isoformat()
                
                # Update market performance
                market = bet.get('market', 'Unknown')
                self.market_performance[market]['total'] += 1
                if result == 'win':
                    self.market_performance[market]['wins'] += 1
                self.market_performance[market]['profit'] += profit
                
                # Update daily performance
                date = datetime.now().date().isoformat()
                if date not in self.daily_performance:
                    self.daily_performance[date] = {'wins': 0, 'losses': 0, 'profit': 0}
                
                if result == 'win':
                    self.daily_performance[date]['wins'] += 1
                elif result == 'loss':
                    self.daily_performance[date]['losses'] += 1
                self.daily_performance[date]['profit'] += profit
                
                self._save_data()
                return bet
        
        return None
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get comprehensive overall statistics"""
        settled_bets = [b for b in self.bets_log if b.get('settled', False)]
        
        if not settled_bets:
            return {
                'total_bets': 0,
                'settled_bets': 0,
                'win_rate': 0.0,
                'total_profit': 0.0,
                'roi': 0.0,
                'avg_odds': 0.0,
                'best_win': 0.0,
                'worst_loss': 0.0,
                'current_streak': 0,
                'longest_win_streak': 0,
                'longest_loss_streak': 0
            }
        
        wins = [b for b in settled_bets if b['result'] == 'win']
        losses = [b for b in settled_bets if b['result'] == 'loss']
        
        total_staked = sum(b.get('stake', 0) for b in settled_bets)
        total_profit = sum(b.get('profit', 0) for b in settled_bets)
        
        return {
            'total_bets': len(self.bets_log),
            'settled_bets': len(settled_bets),
            'pending_bets': len(self.bets_log) - len(settled_bets),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(settled_bets) if settled_bets else 0.0,
            'total_staked': total_staked,
            'total_profit': total_profit,
            'roi': (total_profit / total_staked * 100) if total_staked > 0 else 0.0,
            'avg_odds': np.mean([b.get('odds', 0) for b in settled_bets]),
            'avg_stake': np.mean([b.get('stake', 0) for b in settled_bets]),
            'best_win': max([b.get('profit', 0) for b in wins]) if wins else 0.0,
            'worst_loss': min([b.get('profit', 0) for b in losses]) if losses else 0.0,
            'current_streak': self._calculate_current_streak(settled_bets),
            'longest_win_streak': self._calculate_longest_streak(settled_bets, 'win'),
            'longest_loss_streak': self._calculate_longest_streak(settled_bets, 'loss'),
            'profit_factor': self._calculate_profit_factor(wins, losses),
            'sharpe_ratio': self._calculate_sharpe_ratio(settled_bets),
            'max_drawdown': self._calculate_max_drawdown(settled_bets)
        }
    
    def get_market_performance(self) -> Dict[str, Any]:
        """Performance breakdown by market"""
        market_stats = {}
        
        for market, data in self.market_performance.items():
            total = data['total']
            wins = data['wins']
            profit = data['profit']
            
            market_stats[market] = {
                'total_bets': total,
                'wins': wins,
                'losses': total - wins,
                'win_rate': wins / total if total > 0 else 0.0,
                'profit': profit,
                'roi': (profit / (total * 50) * 100) if total > 0 else 0.0,  # Assume €50 avg stake
            }
        
        # Sort by ROI
        sorted_markets = sorted(
            market_stats.items(),
            key=lambda x: x[1]['roi'],
            reverse=True
        )
        
        return {
            'markets': dict(sorted_markets),
            'best_market': sorted_markets[0] if sorted_markets else None,
            'worst_market': sorted_markets[-1] if sorted_markets else None
        }
    
    def get_time_series_performance(self, days: int = 30) -> Dict[str, Any]:
        """Performance over time"""
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        
        daily_stats = {}
        cumulative_profit = 0
        
        for date_str, data in sorted(self.daily_performance.items()):
            date = datetime.fromisoformat(date_str).date()
            if date >= cutoff_date:
                cumulative_profit += data['profit']
                daily_stats[date_str] = {
                    'wins': data['wins'],
                    'losses': data['losses'],
                    'profit': data['profit'],
                    'cumulative_profit': cumulative_profit,
                    'win_rate': data['wins'] / (data['wins'] + data['losses']) if (data['wins'] + data['losses']) > 0 else 0
                }
        
        return {
            'daily': daily_stats,
            'total_days': len(daily_stats),
            'profitable_days': sum(1 for d in daily_stats.values() if d['profit'] > 0),
            'average_daily_profit': np.mean([d['profit'] for d in daily_stats.values()]) if daily_stats else 0
        }
    
    def get_confidence_calibration(self) -> Dict[str, Any]:
        """Check if confidence scores are calibrated"""
        settled_bets = [b for b in self.bets_log if b.get('settled', False)]
        
        if not settled_bets:
            return {'calibration_score': 0, 'bins': {}}
        
        # Group by confidence bins
        bins = {
            '50-60%': {'predicted': 0.55, 'actual': [], 'count': 0},
            '60-70%': {'predicted': 0.65, 'actual': [], 'count': 0},
            '70-80%': {'predicted': 0.75, 'actual': [], 'count': 0},
            '80-90%': {'predicted': 0.85, 'actual': [], 'count': 0},
            '90-100%': {'predicted': 0.95, 'actual': [], 'count': 0},
        }
        
        for bet in settled_bets:
            confidence = bet.get('confidence', 0.5)
            won = 1 if bet['result'] == 'win' else 0
            
            if 0.5 <= confidence < 0.6:
                bins['50-60%']['actual'].append(won)
                bins['50-60%']['count'] += 1
            elif 0.6 <= confidence < 0.7:
                bins['60-70%']['actual'].append(won)
                bins['60-70%']['count'] += 1
            elif 0.7 <= confidence < 0.8:
                bins['70-80%']['actual'].append(won)
                bins['70-80%']['count'] += 1
            elif 0.8 <= confidence < 0.9:
                bins['80-90%']['actual'].append(won)
                bins['80-90%']['count'] += 1
            elif 0.9 <= confidence <= 1.0:
                bins['90-100%']['actual'].append(won)
                bins['90-100%']['count'] += 1
        
        # Calculate actual win rates per bin
        calibration_error = 0
        for bin_name, data in bins.items():
            if data['actual']:
                data['actual_win_rate'] = np.mean(data['actual'])
                calibration_error += abs(data['predicted'] - data['actual_win_rate'])
            else:
                data['actual_win_rate'] = None
        
        return {
            'bins': bins,
            'calibration_error': calibration_error / len(bins),
            'calibration_score': 1 - (calibration_error / len(bins))
        }
    
    def _calculate_current_streak(self, bets: List[Dict]) -> int:
        """Calculate current win/loss streak"""
        if not bets:
            return 0
        
        # Sort by timestamp
        sorted_bets = sorted(bets, key=lambda x: x.get('settlement_timestamp', ''), reverse=True)
        
        current_result = sorted_bets[0]['result']
        streak = 0
        
        for bet in sorted_bets:
            if bet['result'] == current_result:
                streak += 1 if current_result == 'win' else -1
            else:
                break
        
        return streak
    
    def _calculate_longest_streak(self, bets: List[Dict], result_type: str) -> int:
        """Calculate longest streak of wins or losses"""
        if not bets:
            return 0
        
        sorted_bets = sorted(bets, key=lambda x: x.get('settlement_timestamp', ''))
        
        current_streak = 0
        longest_streak = 0
        
        for bet in sorted_bets:
            if bet['result'] == result_type:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 0
        
        return longest_streak
    
    def _calculate_profit_factor(self, wins: List[Dict], losses: List[Dict]) -> float:
        """Profit Factor = Total Wins / Total Losses"""
        total_wins = sum(b.get('profit', 0) for b in wins)
        total_losses = abs(sum(b.get('profit', 0) for b in losses))
        
        if total_losses == 0:
            return float('inf') if total_wins > 0 else 0
        
        return total_wins / total_losses
    
    def _calculate_sharpe_ratio(self, bets: List[Dict], risk_free_rate: float = 0.02) -> float:
        """Sharpe Ratio = (Mean Return - Risk Free Rate) / Std Dev of Returns"""
        if not bets:
            return 0.0
        
        returns = [b.get('profit', 0) / b.get('stake', 1) for b in bets]
        
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        sharpe = (mean_return - risk_free_rate) / std_return
        return sharpe
    
    def _calculate_max_drawdown(self, bets: List[Dict]) -> float:
        """Maximum drawdown from peak"""
        if not bets:
            return 0.0
        
        sorted_bets = sorted(bets, key=lambda x: x.get('settlement_timestamp', ''))
        
        cumulative_profit = []
        running_total = 0
        
        for bet in sorted_bets:
            running_total += bet.get('profit', 0)
            cumulative_profit.append(running_total)
        
        peak = cumulative_profit[0]
        max_dd = 0
        
        for profit in cumulative_profit:
            if profit > peak:
                peak = profit
            dd = peak - profit
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def _save_data(self):
        """Save all data to disk"""
        data = {
            'bets_log': self.bets_log,
            'daily_performance': dict(self.daily_performance),
            'market_performance': dict(self.market_performance)
        }
        
        with open(self.storage_path / 'performance_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_data(self):
        """Load data from disk"""
        data_file = self.storage_path / 'performance_data.json'
        if data_file.exists():
            with open(data_file, 'r') as f:
                data = json.load(f)
                self.bets_log = data.get('bets_log', [])
                self.daily_performance = defaultdict(dict, data.get('daily_performance', {}))
                self.market_performance = defaultdict(
                    lambda: {'wins': 0, 'total': 0, 'profit': 0},
                    data.get('market_performance', {})
                )


# Global analytics instance
_analytics = None

def get_analytics() -> PerformanceAnalytics:
    """Get global analytics instance"""
    global _analytics
    if _analytics is None:
        _analytics = PerformanceAnalytics()
    return _analytics


if __name__ == '__main__':
    # Test analytics
    analytics = PerformanceAnalytics()
    
    # Simulate some bets
    for i in range(20):
        analytics.log_bet({
            'match': f'Team A vs Team B {i}',
            'market': 'Match Result' if i % 2 == 0 else 'BTTS',
            'selection': 'Home Win',
            'odds': 2.0 + (i % 5) * 0.2,
            'stake': 50,
            'confidence': 0.6 + (i % 4) * 0.1
        })
        
        # Settle some bets
        if i < 15:
            result = 'win' if i % 3 != 0 else 'loss'
            profit = 50 if result == 'win' else -50
            analytics.settle_bet(f"bet_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}", result, profit)
    
    # Get stats
    print("\n" + "="*80)
    print("📊 PERFORMANCE ANALYTICS")
    print("="*80)
    
    overall = analytics.get_overall_stats()
    print(f"\n📈 Overall Stats:")
    print(f"  Total Bets: {overall['total_bets']}")
    print(f"  Win Rate: {overall['win_rate']:.1%}")
    print(f"  Total Profit: €{overall['total_profit']:.2f}")
    print(f"  ROI: {overall['roi']:.1f}%")
    print(f"  Current Streak: {overall['current_streak']}")
    print(f"  Sharpe Ratio: {overall['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: €{overall['max_drawdown']:.2f}")
    
    market_perf = analytics.get_market_performance()
    print(f"\n🎯 Market Performance:")
    for market, stats in list(market_perf['markets'].items())[:3]:
        print(f"  {market}: {stats['win_rate']:.1%} WR, {stats['roi']:.1f}% ROI")
    
    calibration = analytics.get_confidence_calibration()
    print(f"\n🎲 Confidence Calibration Score: {calibration['calibration_score']:.1%}")
