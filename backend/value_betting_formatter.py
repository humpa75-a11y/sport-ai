"""
📊 VALUE BETTING FORMATTER - Mooie Output Generatie
===================================================
Converteert value betting analyses naar leesbare tekst formats
Vergelijkbaar met de originele Bundesliga output
"""

from typing import Dict, List
from datetime import datetime


class ValueBettingFormatter:
    """
    📊 Formatter voor value betting outputs
    
    Maakt mooie, leesbare rapporten zoals het originele Bundesliga script
    """
    
    def __init__(self):
        self.separator = "="*80
        self.subseparator = "-"*80
    
    
    def format_match_simulations(self, analyses: List[Dict]) -> str:
        """
        📊 FORMAT: Simulatie Resultaten Tabel
        
        Output zoals:
        SIMULATIE RESULTATEN (100 runs per match):
        home                away           home_goals  away_goals  p_over_2_5  p_btts  p_home_win
        Ajax                PSV            2.08        1.38        0.72        0.60    0.58
        """
        output = []
        output.append("\n" + self.separator)
        output.append("📊 SIMULATIE RESULTATEN (100 runs per match):")
        output.append(self.separator)
        
        # Header
        output.append(f"{'Home':<20} {'Away':<20} {'H-Goals':>8} {'A-Goals':>8} {'Over2.5':>8} {'BTTS':>8} {'HomeWin':>8}")
        output.append(self.subseparator)
        
        # Data rows
        for analysis in analyses:
            match = analysis['match'].split(' vs ')
            home = match[0]
            away = match[1] if len(match) > 1 else ''
            sim = analysis['simulation_stats']
            
            output.append(
                f"{home:<20} {away:<20} "
                f"{sim['home_goals_mean']:>8.2f} "
                f"{sim['away_goals_mean']:>8.2f} "
                f"{sim['p_over_2_5']:>8.1%} "
                f"{sim['p_btts_yes']:>8.1%} "
                f"{sim['p_home_win']:>8.1%}"
            )
        
        output.append(self.separator)
        return "\n".join(output)
    
    
    def format_value_bets_table(self, value_bets: List[Dict], min_ev: float = 0.05) -> str:
        """
        💎 FORMAT: Value Bets Tabel
        
        Output zoals:
        BESTE BETS (EV > 0.05):
        match                          bet         odds    prob      ev
        Ajax vs PSV                    Home Win    2.10    58.0%    +23.9%
        """
        output = []
        output.append("\n" + self.separator)
        output.append(f"💎 BESTE BETS (EV > {min_ev}):")
        output.append(self.separator)
        
        if not value_bets:
            output.append("❌ Geen value bets gevonden met deze criteria")
            output.append(self.separator)
            return "\n".join(output)
        
        # Header
        output.append(f"{'Match':<35} {'Bet':<15} {'Odds':>6} {'Prob':>8} {'EV':>10}")
        output.append(self.subseparator)
        
        # Data rows
        for bet in value_bets:
            output.append(
                f"{bet['match']:<35} "
                f"{bet['bet']:<15} "
                f"{bet['odds']:>6.2f} "
                f"{bet['probability']:>7.1%} "
                f"{bet['ev_percentage']:>+9.1f}%"
            )
        
        output.append(self.separator)
        return "\n".join(output)
    
    
    def format_accumulator(self, acca: Dict, stake: float = 10.0) -> str:
        """
        🎰 FORMAT: Accumulator Details
        
        Output zoals:
        4-FOLD ALL IN (€10 → €65):
        • Ajax vs PSV → Home Win @ 2.10 (p=58.0%)
        • Feyenoord vs AZ → Over 2.5 @ 1.80 (p=72.0%)
        Total Odds: 3.78x | Hit Rate: 41.8% | €10 → €38
        """
        output = []
        output.append(f"\n{'='*80}")
        output.append(f"🎰 {acca['type'].upper()} (€{stake:.0f} → €{acca['potential_win']:.0f}):")
        output.append(f"{'='*80}")
        
        for bet in acca['bets']:
            output.append(
                f"• {bet['match']:<35} → {bet['bet']:<15} @ {bet['odds']:<5.2f} "
                f"(p={bet['probability']*100:.1f}%)"
            )
        
        output.append(f"\n📊 ACCUMULATOR STATISTIEKEN:")
        output.append(f"   Total Odds: {acca['total_odds']:.2f}x")
        output.append(f"   Hit Rate: {acca['win_probability_pct']:.2f}%")
        output.append(f"   Stake: €{stake:.2f}")
        output.append(f"   Potential Win: €{acca['potential_win']:.2f}")
        output.append(f"   Profit: €{acca['potential_profit']:.2f}")
        output.append(f"   Expected Return: €{acca['expected_return']:.2f} ({'+' if acca['is_value_bet'] else '-'}EV)")
        output.append(f"{'='*80}")
        
        return "\n".join(output)
    
    
    def format_full_report(self, report: Dict, title: str = "BETTING RAPPORT") -> str:
        """
        📄 FORMAT: Volledig Betting Rapport
        
        Combineert alle secties in één mooi rapport
        """
        output = []
        
        # Title
        output.append("\n" + "="*80)
        output.append(f"📊 {title}")
        output.append(f"   Gegenereerd: {datetime.now().strftime('%d %b %Y %H:%M')}")
        output.append("="*80)
        
        # Summary
        output.append("\n📈 SAMENVATTING:")
        output.append(f"   • Matches Geanalyseerd: {report['total_matches_analyzed']}")
        output.append(f"   • Value Bets Gevonden: {report['total_value_bets_found']}")
        output.append(f"   • Gemiddelde EV: +{report['summary']['average_ev']*100:.1f}%")
        output.append(f"   • Markten: {report['summary']['total_markets_covered']}")
        
        # Simulatie resultaten
        if report.get('analyses'):
            output.append(self.format_match_simulations(report['analyses']))
        
        # Value bets tabel
        if report.get('top_single_bets'):
            output.append(self.format_value_bets_table(report['top_single_bets'][:10]))
        
        # Top 3 Single Bets
        output.append("\n" + "="*80)
        output.append("💎 TOP 3 VALUE BETS:")
        output.append("="*80)
        for i, bet in enumerate(report['top_single_bets'][:3], 1):
            output.append(f"\n{i}. {bet['match']}")
            output.append(f"   Bet: {bet['bet']} @ {bet['odds']}")
            output.append(f"   EV: +{bet['ev_percentage']:.1f}% | Kans: {bet['probability']*100:.1f}%")
            output.append(f"   Marktsegment: {bet['market']}")
        
        # Accumulators
        if report.get('recommended_accumulators'):
            output.append("\n" + "="*80)
            output.append("🎰 AANBEVOLEN ACCUMULATORS:")
            output.append("="*80)
            
            for acca in report['recommended_accumulators'][:3]:
                output.append(f"\n{acca['type']} Accumulator:")
                output.append(f"   Odds: {acca['total_odds']:.2f}x | Kans: {acca['win_probability_pct']:.2f}%")
                output.append(f"   €10 → €{acca['potential_win']:.2f}")
                output.append(f"   Bets:")
                for bet in acca['bets']:
                    output.append(f"      • {bet['bet']} ({bet['match']}) @ {bet['odds']}")
        
        # Footer
        output.append("\n" + "="*80)
        output.append("✅ GEREED VOOR INZET – KOPIEER NAAR JE BOOKIE!")
        output.append("⚠️  Check lineups 30 min voor KO! | BET RESPONSIBLY 🎰")
        output.append("="*80 + "\n")
        
        return "\n".join(output)
    
    
    def format_bundesliga_style(self, report: Dict) -> str:
        """
        🇩🇪 FORMAT: Bundesliga-style Output (exact zoals origineel)
        
        Reproduceert de exacte output van het originele script
        """
        output = []
        
        # Header
        output.append("\n" + "="*80)
        output.append("🇩🇪 DEEP ANALYSE MET 100x SIMULATIE – BUNDESLIGA STYLE")
        output.append("="*80)
        
        # Simulatie resultaten
        output.append(self.format_match_simulations(report['analyses']))
        
        # Beste bets
        output.append(self.format_value_bets_table(report['top_single_bets'], min_ev=0.05))
        
        # 4-FOLD
        if len(report['recommended_accumulators']) >= 1:
            acca_4 = next((a for a in report['recommended_accumulators'] if '4' in a['type']), 
                         report['recommended_accumulators'][0])
            
            output.append(f"\n{'='*80}")
            output.append(f"🎰 4-FOLD ALL IN (€10 → €{acca_4['potential_win']:.0f}):")
            output.append(f"{'='*80}")
            for bet in acca_4['bets'][:4]:
                output.append(f"• {bet['match']} → {bet['bet']} @ {bet['odds']} (p={bet['probability']*100:.1f}%)")
            output.append(f"Total Odds: {acca_4['total_odds']:.2f}x | Hit Rate: {acca_4['win_probability_pct']:.1f}% | €10 → €{acca_4['potential_win']:.0f}")
        
        # 7-FOLD (monster)
        if len(report['top_single_bets']) >= 7:
            # Maak custom 7-fold
            from poisson_value_engine import PoissonValueEngine
            engine = PoissonValueEngine()
            acca_7 = engine.create_accumulator(report['top_single_bets'][:7], stake=1.0)
            
            output.append(f"\n{'='*80}")
            output.append(f"🔥 MONSTER 7-FOLD (€1 → €{acca_7['potential_win']:.0f}):")
            output.append(f"{'='*80}")
            for bet in acca_7['bets']:
                output.append(f"• {bet['match']} → {bet['bet']} @ {bet['odds']} (p={bet['probability']*100:.1f}%)")
            output.append(f"Total Odds: {acca_7['total_odds']:.2f}x | Hit Rate: {acca_7['win_probability_pct']:.2f}% | €1 → €{acca_7['potential_win']:.0f}")
        
        # Footer
        output.append("\n" + "="*80)
        output.append("✅ GEREED VOOR INZET – KOPIEER NAAR JE BOOKIE!")
        output.append("⚠️  Check lineups 30 min voor KO! | BET RESPONSIBLY 🎰")
        output.append("="*80 + "\n")
        
        return "\n".join(output)


# Helper functie voor quick formatting
def quick_format_report(report: Dict, style: str = 'full') -> str:
    """
    Quick format helper
    
    Args:
        report: Output van value_engine.generate_betting_report()
        style: 'full', 'bundesliga', 'compact'
    
    Returns:
        Geformatteerde tekst string
    """
    formatter = ValueBettingFormatter()
    
    if style == 'bundesliga':
        return formatter.format_bundesliga_style(report)
    elif style == 'compact':
        return formatter.format_value_bets_table(report['top_single_bets'])
    else:
        return formatter.format_full_report(report)


if __name__ == '__main__':
    """Test de formatter"""
    print("📊 VALUE BETTING FORMATTER - Test Module")
    print("\nDeze module bevat formatting functies voor value betting output")
    print("Gebruik via: from value_betting_formatter import quick_format_report")
