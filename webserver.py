import http.server
import socketserver
import mysql.connector
import os
from urllib.parse import parse_qs
import bcrypt

web_dir = "/var/www/html"
os.chdir(web_dir)

PORT = 80

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/users.html":
            html_content = self.get_users_html()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
        else:
            super().do_GET()

    def get_users_html(self):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="website_data"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email FROM users")
            rows = cursor.fetchall()
            conn.close()
        except mysql.connector.Error as err:
            return f"<h1>Database connection error: {err}</h1>"

        with open("users_template.html", "r") as file:
            template = file.read()

        user_cards = ""
        for user_id, name, email in rows:
            user_cards += f"""
            <div class="card">
                <div>
                    <h3>User ID: {user_id}</h3>
                    <p>Name: {name}</p>
                    <p>Email: {email}</p>
                </div>
                <button class="delete-btn" data-user-id="{user_id}">Delete</button>
            </div>
            """

        html_content = template.replace("<!-- USER_CARDS -->", user_cards)
        return html_content

    def do_DELETE(self):
        if self.path.startswith("/delete_user"):
            query = self.path.split('?')[-1]
            params = parse_qs(query)
            user_id = params.get('id', [None])[0]

            if user_id:
                result = self.delete_user_from_db(user_id)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(result.encode("utf-8"))
            else:
                self.send_error(400, "Invalid user ID.")

    def delete_user_from_db(self, user_id):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="website_data"
            )
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            conn.close()
            return "User deleted successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving content from {web_dir} on port {PORT}")
    httpd.serve_forever()
