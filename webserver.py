import http.server
import socketserver
import os

# Set the directory where your content (HTML, CSS, etc.) is stored
web_dir = "/var/www/html"
os.chdir(web_dir)  # Change directory to serve content from this folder

PORT = 80  # Use port 80 for HTTP

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith(".py"):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"403 Forbidden")
        else:
            super().do_GET()

# Create a TCP server using the handler
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving content from {web_dir} on port {PORT}")
    httpd.serve_forever()
