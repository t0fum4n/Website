import http.server
import socketserver
import mysql.connector  # Use this to connect to MySQL
import os

# Set the directory where your HTML files are stored
web_dir = "/var/www/html"
os.chdir(web_dir)

PORT = 80  # Use HTTP port 80

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/users.html":
            # Generate and serve the users HTML page
            html_content = self.get_users_html()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
        else:
            # Serve other static files as usual
            super().do_GET()

    def get_users_html(self):
        # Connect to the MySQL database and query user data
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="readonly_user",  # MySQL root user
                password="readonly_user",  # No password for root
                database="website_data"  # Correct database name
            )
        except mysql.connector.Error as err:
            return f"<h1>Database connection error: {err}</h1>"

        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")  # Query user data
        rows = cursor.fetchall()
        conn.close()

        # Generate HTML with the user data
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Users | T0fum4n Blog</title>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
            <style>
                body { margin: 0; padding: 0; font-family: 'Roboto', sans-serif; background-color: #0d1117; color: #c9d1d9; }
                header, footer { background-color: #161b22; padding: 20px; text-align: center; }
                .content { padding: 40px; display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }
                .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; width: 300px; }
                nav a { margin: 0 15px; color: #c9d1d9; text-decoration: none; }
                nav a:hover { color: #58a6ff; }
            </style>
        </head>
        <body>
            <header>
                <h1>Users List</h1>
                <nav>
                    <a href="index.html">Home</a>
                    <a href="/users.html">Users</a>
                </nav>
            </header>
            <section class="content">
        """

        # Add each user as a card
        for user_id, name, email in rows:
            html += f"""
            <div class="card">
                <h3>User ID: {user_id}</h3>
                <p>Name: {name}</p>
                <p>Email: {email}</p>
            </div>
            """

        # Close the HTML structure
        html += """
            </section>
            <footer>
                <p>© 2024 T0fum4n. All rights reserved.</p>
            </footer>
        </body>
        </html>
        """
        return html

# Start the web server
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving content from {web_dir} on port {PORT}")
    httpd.serve_forever()
