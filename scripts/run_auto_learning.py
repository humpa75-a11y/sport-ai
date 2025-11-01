"""
⏰ AUTOMATED LEARNING SCHEDULER
===============================

Runs continuous learning on schedule:
- Every day at 03:00 AM (after most matches finished)
- Or run manually anytime

BLIJF LEREN MEESTER! 24/7! 🚀
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.continuous_learner import ContinuousLearner

def scheduled_learning_job():
    """Job that runs on schedule"""
    print("\n" + "="*80)
    print("⏰ SCHEDULED LEARNING JOB TRIGGERED")
    print("="*80)
    print(f"Time: {datetime.now()}")
    print("="*80 + "\n")
    
    try:
        learner = ContinuousLearner()
        learner.run_learning_cycle()
        
        print("\n✅ Scheduled job completed successfully")
        
    except Exception as e:
        print(f"\n❌ Scheduled job failed: {e}")
        import traceback
        traceback.print_exc()


def run_scheduler():
    """Start the scheduler"""
    print("\n" + "="*80)
    print("🤖 AUTOMATED LEARNING SCHEDULER")
    print("="*80)
    print("Schedule: Every day at 03:00 AM")
    print("Press Ctrl+C to stop")
    print("="*80 + "\n")
    
    scheduler = BlockingScheduler()
    
    # Schedule: Every day at 3 AM
    scheduler.add_job(
        scheduled_learning_job,
        trigger=CronTrigger(hour=3, minute=0),
        id='daily_learning',
        name='Daily Learning Cycle',
        replace_existing=True
    )
    
    # Also run immediately on startup
    print("🚀 Running initial learning cycle...")
    scheduled_learning_job()
    
    print("\n⏰ Scheduler started. Waiting for next scheduled time...")
    print("Next run: Tomorrow at 03:00 AM\n")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n\n⏹️  Scheduler stopped by user")
        scheduler.shutdown()


if __name__ == '__main__':
    
    if len(sys.argv) > 1 and sys.argv[1] == '--now':
        # Run immediately without scheduler
        print("🚀 Running learning cycle NOW (no scheduler)...\n")
        scheduled_learning_job()
    else:
        # Start scheduler
        run_scheduler()
