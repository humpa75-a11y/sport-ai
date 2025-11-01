from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World!"

if __name__ == '__main__':
    print("Starting simple Flask test...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter...")
