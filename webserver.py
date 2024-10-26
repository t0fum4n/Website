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

        # Load the HTML template from file
        with open("users_template.html", "r") as file:
            template = file.read()

        # Generate user cards dynamically
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

        # Insert user cards into the template
        html_content = template.replace("<!-- USER_CARDS -->", user_cards)
        return html_content

    def do_POST(self):
        if self.path == "/add_user":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = parse_qs(post_data.decode("utf-8"))

            name = form_data.get("name", [""])[0]
            email = form_data.get("email", [""])[0]
            password = form_data.get("password", [""])[0]

            if name and email and password:
                result = self.add_user_to_db(name, email, password)
                if "successfully" in result:
                    self.send_response(303)
                    self.send_header("Location", "/users.html")
                    self.end_headers()
                else:
                    self.send_error(400, result)
            else:
                self.send_error(400, "All fields are required.")

    def add_user_to_db(self, name, email, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="website_data"
            )
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed_password.decode('utf-8')),
            )
            conn.commit()
            conn.close()
            return "User added successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

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
