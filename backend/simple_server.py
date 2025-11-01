"""
Simple HTTP server for testing - Alternative to Flask
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Professor AI Server is LIVE!</h1><p>Flask alternative working!</p>')
        elif self.path == '/api/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'ok', 'message': 'Server is working!'}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 5000), SimpleHandler)
    print(f"\n{'='*80}")
    print("🚀 SIMPLE SERVER RUNNING ON http://127.0.0.1:5000")
    print(f"{'='*80}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
        server.shutdown()
