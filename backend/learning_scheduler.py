"""
🧠 DE MEESTER - AUTONOMOUS LEARNING SCHEDULER 🧠

Dit is het zenuwstelsel van De Meester. Het zorgt ervoor dat de AI
zichzelf continu verbetert door dagelijks te leren en wekelijks
volledig opnieuw te trainen.
"""
from apscheduler.schedulers.background import BackgroundScheduler
import time
import os
import subprocess
import pandas as pd
from datetime import datetime

# Global reference to the meester object (set by app.py)
_meester_instance = None

def set_meester_instance(meester):
    """Set the global meester instance for the scheduler to use."""
    global _meester_instance
    _meester_instance = meester

def daily_learning_task():
    """
    Taak die elke dag wordt uitgevoerd.
    Haalt de resultaten van gisteren op en laat het model ervan leren.
    """
    print("="*80)
    print(f"🧠 DAILY LEARNING CYCLE: GESTART ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("   - Stap 1: Resultaten van gisteren ophalen...")
    
    try:
        # Voer het scraper script uit
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'get_daily_results.py')
        result = subprocess.run(['python', script_path], capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            # Zoek de CSV data in de output
            output = result.stdout
            if "--- DAILY RESULTS CSV START ---" in output:
                csv_start = output.find("--- DAILY RESULTS CSV START ---") + len("--- DAILY RESULTS CSV START ---")
                csv_end = output.find("--- DAILY RESULTS CSV END ---")
                csv_data = output[csv_start:csv_end].strip()
                
                # Parse CSV data
                from io import StringIO
                df = pd.read_csv(StringIO(csv_data))
                
                print(f"   ✅ {len(df)} nieuwe wedstrijden gevonden!")
                print("   - Stap 2: Model updaten met nieuwe resultaten...")
                
                # Sla de nieuwe resultaten op in een append-only log
                data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
                os.makedirs(data_dir, exist_ok=True)
                log_path = os.path.join(data_dir, 'daily_learning_log.csv')
                
                # Append to log file
                if os.path.exists(log_path):
                    df.to_csv(log_path, mode='a', header=False, index=False)
                else:
                    df.to_csv(log_path, mode='w', header=True, index=False)
                
                print(f"   ✅ Resultaten opgeslagen in daily_learning_log.csv")
                print(f"   📊 De Meester heeft nu {len(df)} nieuwe wedstrijden om van te leren tijdens de volgende retraining!")
                
            else:
                print("   ℹ️ Geen nieuwe resultaten gevonden voor gisteren.")
        else:
            print("   ℹ️ Scraper meldt: Geen data beschikbaar voor gisteren.")
            
    except Exception as e:
        print(f"   ❌ FOUT tijdens scrapen: {e}")
    
    print("✅ DAILY LEARNING CYCLE: VOLTOOID")
    print("="*80)

def weekly_retrain_task():
    """
    Taak die elke week wordt uitgevoerd.
    Voert het volledige trainingsscript uit om het model fundamenteel te verbeteren.
    """
    print("="*80)
    print("🏆 MASTERCLASS RETRAINING: GESTART (Zondag 04:00)")
    print("   - Volledige 'train_model.py' script wordt nu uitgevoerd...")
    
    try:
        # We gebruiken subprocess om het externe script aan te roepen
        # We moeten het pad correct construeren
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'train_model.py')
        subprocess.run(['python', script_path], check=True)
        print("✅ MASTERCLASS RETRAINING: SUCCESVOL VOLTOOID")
    except subprocess.CalledProcessError as e:
        print(f"❌ FOUT TIJDENS MASTERCLASS RETRAINING: {e}")
    except FileNotFoundError:
        print("❌ FOUT: Kon 'train_model.py' niet vinden.")
        
    print("="*80)


def start_scheduler():
    """
    Initialiseert en start de scheduler.
    """
    scheduler = BackgroundScheduler(daemon=True)
    
    # --- Plan de taken ---
    # Dagelijkse taak: elke dag om 03:00 uur 's nachts
    scheduler.add_job(daily_learning_task, 'cron', hour=3, minute=0)
    
    # Wekelijkse taak: elke zondag om 04:00 uur 's nachts
    scheduler.add_job(weekly_retrain_task, 'cron', day_of_week='sun', hour=4, minute=0)
    
    scheduler.start()
    
    print("✅ Autonome Leer-Scheduler is GESTART.")
    print("   - Dagelijkse leertaak gepland om 03:00.")
    print("   - Wekelijkse Masterclass retraining gepland op zondag om 04:00.")
    
    return scheduler
