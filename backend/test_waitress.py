from flask import Flask
from waitress import serve
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>HELLO FROM WAITRESS!</h1>"

if __name__ == '__main__':
    print("="*80)
    print("TESTING WAITRESS...")
    print("="*80)
    print("Starting serve()...")
    sys.stdout.flush()
    
    try:
        print("About to call serve()...")
        serve(app, host='0.0.0.0', port=5000)
        print("serve() returned - this is unexpected!")
    except KeyboardInterrupt:
        print("\nStopped by CTRL+C")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("Program ending...")
