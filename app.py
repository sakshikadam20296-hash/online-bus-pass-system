from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


# =========================
# DATABASE TABLES
# =========================
def create_table():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Bus Pass Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bus_pass (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            college TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            pass_type TEXT NOT NULL,
            start_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users
            (name, email, mobile, password)
            VALUES (?, ?, ?, ?)
        """, (name, email, mobile, password))

        conn.commit()
        conn.close()

        return "Registration Successful!"

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users
            WHERE email = ? AND password = ?
        """, (email, password))

        user = cursor.fetchone()

        conn.close()

        if user:
            return render_template("dashboard.html")
        else:
            return "Invalid Email or Password!"

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# =========================
# APPLY FOR BUS PASS
# =========================
@app.route("/apply-pass", methods=["GET", "POST"])
def apply_pass():

    if request.method == "POST":

        student_name = request.form["student_name"]
        college = request.form["college"]
        source = request.form["source"]
        destination = request.form["destination"]
        pass_type = request.form["pass_type"]
        start_date = request.form["start_date"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bus_pass
            (student_name, college, source, destination, pass_type, start_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_name,
            college,
            source,
            destination,
            pass_type,
            start_date
        ))

        conn.commit()
        conn.close()

        # Success Page
        return render_template("success.html")

    return render_template("apply_pass.html")


# =========================
# MY BUS PASS
# =========================
@app.route("/my-pass")
def my_pass():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM bus_pass
        ORDER BY id DESC
        LIMIT 1
    """)

    pass_data = cursor.fetchone()

    conn.close()

    if pass_data:
        return render_template(
            "my_pass.html",
            pass_data=pass_data
        )
    else:
        return "No Bus Pass Application Found!"


# =========================
# RUN APPLICATION
# =========================
if __name__ == "__main__":

    create_table()

    app.run(debug=True)