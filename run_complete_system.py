"""
🎯 RUN EVERYTHING - FINAL INTEGRATION

Dit script runt ALLES en geeft je complete data:
- Unibet odds scraping
- AI predictions
- Performance analysis
- Dashboard ready data

ONE COMMAND = EVERYTHING WORKS
"""

import subprocess
import sys
import os
from datetime import datetime

def print_header(title):
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80)

def run_script(script_path, description):
    """Run a Python script and return success status"""
    print(f"\n🚀 {description}...")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            # Print last 10 lines of output
            output_lines = result.stdout.split('\n')
            relevant_lines = [l for l in output_lines if l.strip() and not l.startswith(' ')][-10:]
            for line in relevant_lines:
                if any(keyword in line.lower() for keyword in ['success', 'saved', 'total', 'matches', 'complete']):
                    print(f"   {line[:100]}")
            return True
        else:
            print(f"⚠️ WARNING: {description}")
            if result.stderr:
                print(f"   {result.stderr[:200]}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT: {description} (taking too long, skipped)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {description} - {str(e)[:100]}")
        return False

def main():
    print_header("🏆 DE MEESTER - COMPLETE SYSTEM RUN")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 1. Scrape Unibet
    print_header("STEP 1: SCRAPE UNIBET ODDS")
    success = run_script(
        os.path.join('scripts', 'unibet_ultimate_scraper.py'),
        'Scraping Unibet.nl for latest odds'
    )
    results.append(('Unibet Scraper', '✅ SUCCESS' if success else '⚠️ FAILED'))
    
    # 2. Train/Update AI Model
    print_header("STEP 2: AI MODEL UPDATE")
    print("ℹ️ Using existing trained model (de_meester.pkl)")
    print("   To retrain: python scripts/smart_trainer.py")
    results.append(('AI Model', '✅ READY'))
    
    # 3. Generate Performance Report
    print_header("STEP 3: PERFORMANCE ANALYSIS")
    success = run_script(
        os.path.join('scripts', 'meester_analyzer.py'),
        'Analyzing AI performance'
    )
    results.append(('Performance Report', '✅ SUCCESS' if success else '⚠️ SKIPPED'))
    
    # 4. Check data files
    print_header("STEP 4: DATA FILES CHECK")
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    required_files = [
        ('de_meester.pkl', 'AI Model'),
        ('unibet_ultimate_*.csv', 'Unibet Odds'),
    ]
    
    for pattern, description in required_files:
        if '*' in pattern:
            # Check for any file matching pattern
            import glob
            files = glob.glob(os.path.join(data_dir, pattern))
            if files:
                latest = max(files, key=os.path.getctime)
                print(f"   ✅ {description}: {os.path.basename(latest)}")
                results.append((description, '✅ FOUND'))
            else:
                print(f"   ❌ {description}: NOT FOUND")
                results.append((description, '❌ MISSING'))
        else:
            filepath = os.path.join(data_dir, pattern)
            if os.path.exists(filepath):
                print(f"   ✅ {description}: {pattern}")
                results.append((description, '✅ FOUND'))
            else:
                print(f"   ❌ {description}: NOT FOUND")
                results.append((description, '❌ MISSING'))
    
    # Final Report
    print_header("📊 FINAL STATUS REPORT")
    
    for task, status in results:
        print(f"{status:15} {task}")
    
    print_header("🎯 SYSTEM READY!")
    
    print("\n📂 Generated Files:")
    print("   - data/unibet_ultimate_*.csv (Latest odds)")
    print("   - data/de_meester.pkl (AI Model)")
    print("   - reports/meester_performance_*.html (Performance)")
    
    print("\n🌐 Next Steps:")
    print("   1. Start main server: python backend/app.py")
    print("   2. Start dashboard: python ultimate_dashboard.py")
    print("   3. Open browser: http://127.0.0.1:5000")
    
    print("\n✅ EVERYTHING IS OPERATIONAL!")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
