"""
📊 LEARNING PROGRESS CHECKER 📊
Check hoe goed de AI is geworden!
"""

import json
import os
from datetime import datetime

def check_progress():
    print("\n" + "="*80)
    print("📊 AI LEARNING PROGRESS REPORT")
    print("="*80)
    
    # Load stats
    stats_file = 'data/learning_stats.json'
    
    if not os.path.exists(stats_file):
        print("\n❌ Nog geen learning stats gevonden!")
        print("   Run eerst: python continuous_learning.py")
        return
    
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    # Current status
    print(f"\n🎯 HUIDIGE STATUS:")
    print(f"   Laatste update: {stats.get('last_update', 'Nooit')}")
    print(f"   Totaal trainingen: {stats.get('total_trainings', 0)}")
    print(f"   Huidige accuracy: {stats.get('accuracy', 0):.2f}%")
    print(f"   Totaal wedstrijden: {stats.get('total_matches', 0)}")
    
    # Improvement history
    improvements = stats.get('improvements', [])
    
    if len(improvements) > 1:
        print(f"\n📈 VERBETERING OVER TIJD:")
        print("-" * 80)
        
        for i, imp in enumerate(improvements[-10:], 1):  # Last 10
            date = datetime.fromisoformat(imp['date']).strftime('%Y-%m-%d')
            acc = imp['accuracy']
            change = imp.get('improvement', 0)
            
            emoji = "🚀" if change > 0 else "⚠️" if change < 0 else "➡️"
            print(f"   {emoji} {date}: {acc:.2f}% ({change:+.2f}%)")
    
    # Predictions
    if len(improvements) >= 3:
        recent_improvements = [imp['improvement'] for imp in improvements[-5:]]
        avg_improvement = sum(recent_improvements) / len(recent_improvements)
        
        print(f"\n🔮 VOORSPELLING:")
        print(f"   Gemiddelde verbetering per training: {avg_improvement:.2f}%")
        
        if avg_improvement > 0:
            weeks_to_15 = (15 - stats['accuracy']) / (avg_improvement * 7)  # 7 days
            print(f"   Geschatte tijd tot 15% accuracy: {int(weeks_to_15)} weken")
            print(f"   → Bij 15%: BOOKMAKER NIVEAU! 🏆")
    
    # Goal
    print(f"\n🎯 DOEL:")
    print(f"   Huidige: {stats['accuracy']:.1f}%")
    print(f"   Bookmakers: 15-20%")
    print(f"   Te gaan: {15 - stats['accuracy']:.1f}%")
    
    progress_to_goal = (stats['accuracy'] / 15) * 100
    bar_length = 50
    filled = int(bar_length * progress_to_goal / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\n   [{bar}] {progress_to_goal:.1f}%")
    
    # Advice
    print(f"\n💡 ADVIES:")
    if stats['accuracy'] < 10:
        print("   → Blijf dagelijks trainen!")
        print("   → Focus op Eerste Divisie (minder concurrentie)")
    elif stats['accuracy'] < 15:
        print("   → Goed bezig! Keep going!")
        print("   → Voeg meer live data toe via /api/learn")
    else:
        print("   → 🏆 PROFESSIONEEL NIVEAU BEREIKT!")
        print("   → Tijd om te MONETIZEN!")
    
    print("="*80)


if __name__ == "__main__":
    check_progress()
