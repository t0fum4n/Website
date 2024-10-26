import http.server
import socketserver
import mysql.connector  # Use this to connect to MySQL
import os
from urllib.parse import parse_qs
import bcrypt  # For password hashing

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

    def do_POST(self):
        if self.path == "/add_user":
            # Handle form submission to add a new user
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = parse_qs(post_data.decode("utf-8"))

            name = form_data.get("name", [""])[0]
            email = form_data.get("email", [""])[0]
            password = form_data.get("password", [""])[0]

            if name and email and password:
                # Insert new user into the database
                result = self.add_user_to_db(name, email, password)
                if "successfully" in result:  # Check if the insertion was successful
                    # Redirect to the users.html page
                    self.send_response(303)  # 303 See Other for redirects after POST
                    self.send_header("Location", "/users.html")
                    self.end_headers()
                else:
                    response = f"<h1>{result}</h1>"
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(response.encode("utf-8"))
            else:
                response = "<h1>Error: All fields are required!</h1>"
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(response.encode("utf-8"))

    def get_users_html(self):
        # Connect to the MySQL database and query user data
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",  # Replace with the appropriate user
                password="",  # Replace with the actual password
                database="website_data"  # Correct database name
            )
        except mysql.connector.Error as err:
            return f"<h1>Database connection error: {err}</h1>"

        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")
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
                form { margin-top: 20px; }
                input, button { padding: 10px; margin: 5px 0; width: 100%; max-width: 300px; }
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

        # Add form to create a new user with a password field
        html += """
            </section>
            <section class="content">
                <form method="POST" action="/add_user">
                    <h3>Add New User</h3>
                    <input type="text" name="name" placeholder="Name" required><br>
                    <input type="email" name="email" placeholder="Email" required><br>
                    <input type="password" name="password" placeholder="Password" required><br>
                    <button type="submit">Add User</button>
                </form>
            </section>
            <footer>
                <p>© 2024 T0fum4n. All rights reserved.</p>
            </footer>
        </body>
        </html>
        """
        return html

    def add_user_to_db(self, name, email, password):
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",  # Replace with the appropriate user
                password="",  # Replace with the actual password
                database="website_data"
            )
            cursor = conn.cursor()
            # Insert the user with the hashed password
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                           (name, email, hashed_password.decode('utf-8')))
            conn.commit()
            conn.close()
            return "User added successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

# Start the web server
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving content from {web_dir} on port {PORT}")
    httpd.serve_forever()
