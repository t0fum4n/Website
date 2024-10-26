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
                if "successfully" in result:
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

    def do_DELETE(self):
        if self.path.startswith("/delete_user"):
            # Extract the user ID from the query string
            query = self.path.split('?')[-1]
            params = parse_qs(query)
            user_id = params.get('id', [None])[0]

            if user_id:
                result = self.delete_user_from_db(user_id)
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(result.encode("utf-8"))
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Invalid user ID")

    def get_users_html(self):
        # Connect to the MySQL database and query user data
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="website_data"
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
                body {
                    margin: 0;
                    padding: 0;
                    font-family: 'Roboto', sans-serif;
                    background-color: #0d1117;
                    color: #c9d1d9;
                }
                header, footer {
                    background-color: #161b22;
                    padding: 20px;
                    text-align: center;
                }
                .container {
                    display: flex;
                    padding: 40px;
                    gap: 20px;
                    flex-wrap: wrap;
                }
                .form-container {
                    flex: 1;
                    max-width: 300px;
                    background-color: #161b22;
                    border: 1px solid #30363d;
                    border-radius: 10px;
                    padding: 20px;
                    box-sizing: border-box;
                    margin-bottom: 20px;
                }
                .users-container {
                    flex: 3;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    justify-content: flex-start;
                }
                .card {
                    background-color: #161b22;
                    border: 1px solid #30363d;
                    border-radius: 10px;
                    padding: 20px;
                    width: 300px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }
                .delete-btn {
                    align-self: center;
                    background-color: #d73a49;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                    font-size: 12px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                    margin-top: 10px;
                }
                .delete-btn:hover {
                    background-color: #e55361;
                }
                input {
                    width: 100%;
                    margin-top: 10px;
                    padding: 12px;
                    background-color: #0d1117;
                    border: 1px solid #30363d;
                    border-radius: 8px;
                    color: #c9d1d9;
                    font-size: 16px;
                    box-sizing: border-box;
                }
                input::placeholder {
                    color: #8b949e;
                }
                input:focus {
                    outline: none;
                    border-color: #58a6ff;
                    box-shadow: 0 0 8px #58a6ff;
                }
                button {
                    width: 100%;
                    padding: 12px;
                    margin-top: 10px;
                    background-color: #0366d6;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-size: 16px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }
                button:hover {
                    background-color: #005cc5;
                }
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
            <div class="container">
                <div class="form-container">
                    <h3>Add New User</h3>
                    <form method="POST" action="/add_user">
                        <input type="text" name="name" placeholder="Name" required>
                        <input type="email" name="email" placeholder="Email" required>
                        <input type="password" name="password" placeholder="Password" required>
                        <button type="submit">Add User</button>
                    </form>
                </div>
                <div class="users-container">
        """

        # Add each user as a card with a delete button at the bottom
        for user_id, name, email in rows:
            html += f"""
            <div class="card">
                <div>
                    <h3>User ID: {user_id}</h3>
                    <p>Name: {name}</p>
                    <p>Email: {email}</p>
                </div>
                <button class="delete-btn" data-user-id="{user_id}">Delete</button>
            </div>
            """

        html += """
                </div>
            </div>
            <footer>
                <p>© 2024 T0fum4n. All rights reserved.</p>
            </footer>
            <script>
                document.querySelectorAll('.delete-btn').forEach(button => {
                    button.addEventListener('click', () => {
                        const userId = button.getAttribute('data-user-id');
                        if (confirm('Do you want to delete this user?')) {
                            fetch(`/delete_user?id=${userId}`, { method: 'DELETE' })
                                .then(response => response.text())
                                .then(result => {
                                    alert(result);
                                    location.reload();
                                })
                                .catch(error => console.error('Error:', error));
                        }
                    });
                });
            </script>
        </body>
        </html>
        """
        return html

    def add_user_to_db(self, name, email, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="website_data"
            )
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                           (name, email, hashed_password.decode('utf-8')))
            conn.commit()
            conn.close()
            return "User added successfully!"
        except mysql.connector.Error as err:
            return f"Error: {err}"

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
