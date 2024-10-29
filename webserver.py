import http.server
import socketserver
import mysql.connector
import os
from urllib.parse import parse_qs

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

        elif self.path == "/ftp_ips.html":
            html_content = self.get_ftp_ips_html()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))

        else:
            super().do_GET()

    def get_users_html(self):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="Justus2009!", database="website_data"
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

    def get_ftp_ips_html(self):
        """Generate the HTML for displaying FTP IP addresses."""
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="Justus2009!", database="ftp_data"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT ip_address, last_checked FROM ftp_ips")
            rows = cursor.fetchall()
            conn.close()
        except mysql.connector.Error as err:
            return f"<h1>Database connection error: {err}</h1>"

        with open("ftp_ips_template.html", "r") as file:
            template = file.read()

        ip_list_html = ""
        for ip_address, last_checked in rows:
            ip_list_html += f"""
            <tr>
                <td>{ip_address}</td>
                <td>{last_checked}</td>
            </tr>
            """

        html_content = template.replace("<!-- FTP_IPS -->", ip_list_html)
        return html_content

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving content from {web_dir} on port {PORT}")
    httpd.serve_forever()
