"""
⏰ DAGELIJKSE AUTO-TRAINING SCHEDULER ⏰
Run dit script elke dag (via Windows Task Scheduler of cron)
"""

from continuous_learning import ContinuousLearningEngine
from datetime import datetime
import sys

def main():
    print("\n" + "="*80)
    print(f"⏰ AUTO-TRAINING GESTART: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    try:
        engine = ContinuousLearningEngine()
        success = engine.daily_update()
        
        if success:
            print("\n✅ DAGELIJKSE TRAINING SUCCESVOL!")
            return 0
        else:
            print("\n⚠️  Geen updates vandaag")
            return 0
    
    except Exception as e:
        print(f"\n❌ FOUT: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
